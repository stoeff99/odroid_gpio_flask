# odroid_gpio_flask
Home Assistant custom addon that runs on HAOS: A Flask server to switch GPIOs on ODROID M1S

Installion:
1) Copy the contents of the repository to the "Addons" folder on HAOS via Studio Code Server or similar editing tool
2) The physical pin # are mapped to the corresponding gpiochip number and line. This is mapped in  gpio_server.py
4) Add the necesary rest commands to configuration.yaml. See example configuration.yaml
5) Add a Switch or Helper in HAOS to controll the pin output
