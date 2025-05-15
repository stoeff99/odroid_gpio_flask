from flask import Flask, jsonify, abort
import gpiod
import subprocess

app = Flask(__name__)
active_lines = {}

def get_gpio_line(line_number):
    if line_number in active_lines:
        return active_lines[line_number]

    for chip_index in range(4):
        try:
            chip_path = f"/dev/gpiochip{chip_index}"
            chip = gpiod.Chip(chip_path)
            if line_number < chip.num_lines():
                line = chip.get_line(line_number)
                line.request(consumer="ha_gpio", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
                active_lines[line_number] = line
                print(f"Using {chip_path} for GPIO line {line_number}")
                return line
        except Exception as e:
            print(f"Failed on gpiochip{chip_index}: {e}")
            continue

    raise RuntimeError(f"GPIO line {line_number} not found")

@app.route("/pin/<int:line>/<action>", methods=["GET"])
def control_pin(line, action):
    try:
        line_obj = get_gpio_line(line)

        if action == "on":
            line_obj.set_value(1)
            result = "HIGH"
        elif action == "off":
            line_obj.set_value(0)
            result = "LOW"
        elif action == "toggle":
            value = line_obj.get_value()
            new_value = 0 if value else 1
            line_obj.set_value(new_value)
            result = f"Toggled to {'HIGH' if new_value else 'LOW'}"
        elif action == "status":
            result = str(line_obj.get_value())
        else:
            abort(400, description="Invalid action. Use on, off, toggle, or status.")

        print(f"GPIO {line}: {action.upper()} -> {result}")
        return jsonify(line=line, result=result)

    except Exception as e:
        print(f"Error handling GPIO {line}: {e}")
        return jsonify(error=str(e)), 500

@app.route("/debug/gpioinfo", methods=["GET"])
def debug_gpioinfo():
    import shutil
    gpioinfo_path = shutil.which("gpioinfo")
    if not gpioinfo_path:
        print("gpioinfo not found")
        return jsonify(error="gpioinfo not found on system"), 404

    try:
        output = subprocess.check_output([gpioinfo_path], text=True)
        return f"<pre>{output}</pre>"
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
        return jsonify(error=f"Command failed: {e}"), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify(error=f"Unexpected error: {e}"), 500

if __name__ == "__main__":
    print("Starting Flask GPIO server on port 8000...")
    app.run(host="0.0.0.0", port=8000)
