from flask import Flask, jsonify, abort
import gpiod
import subprocess

app = Flask(__name__)
active_lines = {}

# === Pin map defined directly here ===
# Maps physical pin number to (gpiochip name, line number)
# Examples: 
# http://localhost:8000/pin/7/on; http://localhost:8000/pin/10/off; 
# http://localhost:8000/pin/15/toggle ;http://localhost:8000/pin/26/status

PHYSICAL_PIN_MAP = {
    7:  ("gpiochip0", 14),  # Example: GPIO0_A6
    8:  ("gpiochip2", 4),   # Example: GPIO2_A4
    10:  ("gpiochip2", 3),   # Example: GPIO2_A3
    11: ("gpiochip0", 16),  # Example: GPIO0_C0
    12:  ("gpiochip2", 7),   # Example: GPIO2_A7
    13: ("gpiochip0", 17),  # Example: GPIO0_C1
    15: ("gpiochip0", 18),  # Example: GPIO0_C2
    16: ("gpiochip2", 13),  # Example: GPIO2_B5
    18: ("gpiochip2", 14),  # Example: GPIO2_B6
    22: ("gpiochip2", 8),  # Example: GPIO2_B0
    23: ("gpiochip3", 19),  # Example: GPIO3_C3
    24: ("gpiochip3", 1),  # Example: GPIO3_A1
    26: ("gpiochip2", 9),  # Example: GPIO2_B1
    27: ("gpiochip0", 12),  # Example: GPIO0_B4
    28: ("gpiochip0", 11),  # Example: GPIO0_B3
    29: ("gpiochip2", 16),  # Example: GPIO2_C0
    31: ("gpiochip2", 15),  # Example: GPIO2_B7
    32: ("gpiochip2", 10),  # Example: GPIO2_B2
    35: ("gpiochip2", 5),   # Example: GPIO2_A5
    36: ("gpiochip2", 6),   # Example: GPIO2_A6
    # Add more pins from J3 2x7pin as needed. https://wiki.odroid.com/odroid-m1s/hardware/expansion_connectors
}

def get_gpio_line(physical_pin):
    if physical_pin not in PHYSICAL_PIN_MAP:
        raise ValueError(f"Pin {physical_pin} is not defined in PHYSICAL_PIN_MAP")

    chip_name, line_number = PHYSICAL_PIN_MAP[physical_pin]
    key = (chip_name, line_number)

    if key in active_lines:
        return active_lines[key]

    try:
        chip_path = f"/dev/{chip_name}"
        chip = gpiod.Chip(chip_path)
        line = chip.get_line(line_number)
        line.request(consumer="ha_gpio", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
        active_lines[key] = line
        print(f"Using {chip_path} for GPIO line {line_number} (pin {physical_pin})")
        return line
    except Exception as e:
        raise RuntimeError(f"Failed to access {chip_name} line {line_number} for pin {physical_pin}: {e}")

@app.route("/pin/<int:pin>/<action>", methods=["GET"])
def control_pin(pin, action):
    try:
        line_obj = get_gpio_line(pin)

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

@app.route("/pins", methods=["GET"])
def list_pins():
    return jsonify(available_pins=list(PHYSICAL_PIN_MAP.keys()))

@app.route("/pins/full", methods=["GET"])
def list_full_pinmap():
    return jsonify(PHYSICAL_PIN_MAP)

if __name__ == "__main__":
    print("Starting Flask GPIO server on port 8000...")
    app.run(host="0.0.0.0", port=8000)
