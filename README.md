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
	# Rest command to recieve feedback on the pin status
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
