# odroid_gpio_flask
Home Assistant custom addon that runs on HAOS: A Flask server to switch GPIOs on ODROID M1S

Installion:
1) Copy the contents of the repository to the "Addons" folder on HAOS via Studio Code Server or similar editing tool
2) The physical pin # on the Odroid M1S can be established by:
 		- https://wiki.odroid.com/odroid-m1s/hardware/expansion_connectors#j4_-_2x20_pins
   	- Example for physical pin 7: GPIO0.B6 (#14) --> Line/Pin #14 in the HAOS configuration. See below:
4) Add the necesary rest commands to configuration.yaml
		# HTTP commands to send to your add-on
		rest_command:
  			gpio7_on:
				url: "http://localhost:8000/pin/14/on"
			    	method: GET

			gpio7_off:
			    	url: "http://localhost:8000/pin/14/off"
			    	method: GET
		# Rest comman to recieve feedback on the pin status
	 	rest:
		  - resource: http://localhost:8000/pin/14/status
		    scan_interval: 5
		    sensor:
		      - name: "Battery Heating Status"
		        value_template: >
		          {% if value_json.result == '1' %}
		            on
		          {% else %}
		            off
		          {% endif %}
   5) Add a Switch of Helper in HAOS to controll the pin output
