from flask import Flask, jsonify, abort
import gpiod
import subprocess

app = Flask(__name__)
active_lines = {}

# === Pin map with optional invert_logic ===
# Format: pin: (chip, line, {"invert_logic": True/False})
PHYSICAL_PIN_MAP = {
    7:  ("gpiochip0", 14, {"invert_logic": False}),
    8:  ("gpiochip2", 4, {"invert_logic": False}),
    10: ("gpiochip2", 3, {"invert_logic": False}),
    11: ("gpiochip0", 16, {"invert_logic": False}),
    12: ("gpiochip2", 7, {"invert_logic": False}),
    13: ("gpiochip0", 17, {"invert_logic": True}),  # Inverted
    15: ("gpiochip0", 18, {"invert_logic": False}),
    16: ("gpiochip2", 13, {"invert_logic": False}),
    18: ("gpiochip2", 14, {"invert_logic": False}),
    22: ("gpiochip2", 8, {"invert_logic": False}),
    23: ("gpiochip3", 19, {"invert_logic": False}),
    24: ("gpiochip3", 1, {"invert_logic": False}),
    26: ("gpiochip2", 9, {"invert_logic": False}),
    27: ("gpiochip0", 12, {"invert_logic": False}),
    28: ("gpiochip0", 11, {"invert_logic": False}),
    29: ("gpiochip2", 16, {"invert_logic": False}),
    31: ("gpiochip2", 15, {"invert_logic": False}),
    32: ("gpiochip2", 10, {"invert_logic": False}),
    33: ("gpiochip0", 13, {"invert_logic": False}),
    35: ("gpiochip2", 5, {"invert_logic": False}),
    36: ("gpiochip2", 6, {"invert_logic": False}),
    # Add more pins as needed
}

def get_gpio_line(physical_pin):
    if physical_pin not in PHYSICAL_PIN_MAP:
        raise ValueError(f"Pin {physical_pin} is not defined in PHYSICAL_PIN_MAP")

    entry = PHYSICAL_PIN_MAP[physical_pin]
    chip_name, line_number, config = entry if len(entry) == 3 else (*entry, {})

    invert_logic = config.get("invert_logic", False)
    key = (chip_name, line_number)

    if key in active_lines:
        return active_lines[key], invert_logic

    try:
        chip = gpiod.Chip(f"/dev/{chip_name}")
        line = chip.get_line(line_number)
        line.request(consumer="ha_gpio", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
        active_lines[key] = line
        print(f"Using /dev/{chip_name} line {line_number} (pin {physical_pin})")
        return line, invert_logic
    except Exception as e:
        raise RuntimeError(f"Failed to access {chip_name} line {line_number} for pin {physical_pin}: {e}")

def apply_invert(val, invert_logic):
    return 1 - val if invert_logic else val

@app.route("/pin/<int:pin>/<action>", methods=["GET"])
def control_pin(pin, action):
    try:
        line, invert_logic = get_gpio_line(pin)

        if action == "on":
            line.set_value(apply_invert(1, invert_logic))
            result = "HIGH" if not invert_logic else "LOW"
        elif action == "off":
            line.set_value(apply_invert(0, invert_logic))
            result = "LOW" if not invert_logic else "HIGH"
        elif action == "toggle":
            actual = line.get_value()
            logical = apply_invert(actual, invert_logic)
            new_logical = 0 if logical else 1
            new_actual = apply_invert(new_logical, invert_logic)
            line.set_value(new_actual)
            result = f"Toggled to {'HIGH' if new_logical else 'LOW'}"
        elif action == "status":
            actual = line.get_value()
            logical = apply_invert(actual, invert_logic)
            result = str(logical)
        else:
            abort(400, description="Invalid action. Use on, off, toggle, or status.")

        print(f"GPIO pin {pin}: {action.upper()} -> {result}")
        return jsonify(pin=pin, result=result)

    except Exception as e:
        print(f"Error handling GPIO pin {pin}: {e}")
        return jsonify(error=str(e)), 500

@app.route("/debug/gpioinfo", methods=["GET"])
def debug_gpioinfo():
    import shutil
    gpioinfo_path = shutil.which("gpioinfo")
    if not gpioinfo_path:
        return jsonify(error="gpioinfo not found on system"), 404

    try:
        output = subprocess.check_output([gpioinfo_path], text=True)
        return f"<pre>{output}</pre>"
    except subprocess.CalledProcessError as e:
        return jsonify(error=f"Command failed: {e}"), 500
    except Exception as e:
        return jsonify(error=f"Unexpected error: {e}"), 500

@app.route("/pins", methods=["GET"])
def list_pins():
    return jsonify(available_pins=list(PHYSICAL_PIN_MAP.keys()))

@app.route("/pins/full", methods=["GET"])
def list_full_pinmap():
    return jsonify(PHYSICAL_PIN_MAP)

if __name__ == "__main__":
    print("Starting Flask GPIO server on port 8000...")
    app.run(host="0.0.0.0", port=8000)
