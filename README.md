# odroid_gpio_flask
Home Assistant custom addon that runs on HAOS: A Flask server to switch GPIOs on ODROID M1S

Installion:
1) Copy the contents of the repository to the "Addons" folder on HAOS via Studio Code Server or similar editing tool
2) The physical pin # are mapped to the corresponding gpiochip number and line. This is mapped in  gpio_server.py
4) Add the necesary rest commands to configuration.yaml

# HTTP commands to send to your add-on
rest_command:
  gpio7_on:
    url: "http://localhost:8000/pin/7/on"
    method: GET

  gpio7_off:
    url: "http://localhost:8000/pin/7/off"
    method: GET

  gpio8_on:
    url: "http://localhost:8000/pin/8/on"
    method: GET

  gpio8_off:
    url: "http://localhost:8000/pin/8/off"
    method: GET

switch:
  - platform: template
    switches:
      battery_heating_test:
        friendly_name: "Battery Heater"
        value_template: "{{ is_state('sensor.battery_heating_status', 'on') }}"
        turn_on:
          - action: input_boolean.turn_on
            target:
              entity_id: input_boolean.gpio_pin7
          - action: rest_command.gpio7_on
        turn_off:
          - action: input_boolean.turn_off
            target:
              entity_id: input_boolean.gpio_pin7
          - action: rest_command.gpio7_off

      charging_enabled:
        friendly_name: "Charging Enabled"
        value_template: "{{ is_state('sensor.battery_charging_status', 'on') }}"
        turn_on:
          - action: input_boolean.turn_on
            target:
              entity_id: input_boolean.gpio_pin8
          - action: rest_command.gpio8_on
        turn_off:
          - action: input_boolean.turn_off
            target:
              entity_id: input_boolean.gpio_pin8
          - action: rest_command.gpio8_off

command_line:
  - sensor:
      name: "Battery Heating Status"
      command: "curl -s http://localhost:8000/pin/7/status"
      scan_interval: 86400  # disables auto-updating
      value_template: >
        {% set result = value | regex_findall_index('"result":\\s*"?(\\d)"?') %}
        {% if result == '1' %}
          on
        {% else %}
          off
        {% endif %}

  - sensor:
      name: "Battery Charging Status"
      command: "curl -s http://localhost:8000/pin/8/status"
      scan_interval: 86400  # disables auto-updating
      value_template: >
        {% set result = value | regex_findall_index('"result":\\s*"?(\\d)"?') %}
        {% if result == '1' %}
          on
        {% else %}
          off
        {% endif %}


   5) Add a Switch or Helper in HAOS to controll the pin output
