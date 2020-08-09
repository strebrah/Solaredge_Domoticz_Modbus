# Solaredge Domoticz Modbus

Designed for python 3.7 (based on the requirements of the 'solaredge_modbus' library.)<br/>
Thanks to Niels for the 'solaredge_modbus' library https://pypi.org/project/solaredge-modbus/<br/>
Tested on Raspberry Pi Zero W, running Domoticz, in combination with a SE5000HD Solaredge inverter.

# Capabilities:                                                                                    
- Creating a hardware device in Domoticz                                                      
- Creating sensors for the data types in Domoticz                                             
- Sending the solaredge modbus data to Domoticz     

# Limitations:                                                                                    
- No 3-phase inverters (for now)                                                    
- Sensor types are fixed in code                                          
- Zero to none errors checks   

## How to use (for example, on a raspberry pi)
1. download files
2. Enter configuration in ini file.<br/>
<br/>**Only change values in bold**

    [GENERAL SETTINGS]<br/>
    domoticz_ip = **192.168.100.3**<br/>
    domoticz_port = **80**<br/>
    domoticz_hw_name = **Solaredge Modbus TCP** <br/>
    solaredge_inverter_ip = **192.168.100.211**<br/>
    solaredge_inverter_port = **502**<br/>
    domoticz_hw_idx = 0<br/>
    domoticz_solaredge_comm_init_done = 0<br/>
    current_inverter_state = 0<br/>

    [SENSOR NAME LIST]<br/>
    solaredge_dc_voltage = **Solaredge DC Voltage**<br/>
    solaredge_dc_current = **Solaredge DC Current**<br/>
    solaredge_dc_power = **Solaredge DC Power**<br/>
    solaredge_ac_voltage = **Solaredge AC Voltage**<br/>
    solaredge_ac_current = **Solaredge AC Current**<br/>
    solaredge_ac_power = **Solaredge AC Power**<br/>
    solaredge_inverter_temp = **Solaredge Inverter Temperature**<br/>
    solaredge_total_energy = **Solaredge Total Energy**<br/>
    solaredge_inverter_state = **Solaredge Inverter State**<br/>

    [SENSOR IDX LIST]<br/>
    solaredge_dc_voltage_idx = 0<br/>
    solaredge_dc_current_idx = 0<br/>
    solaredge_dc_power_idx = 0<br/>
    solaredge_ac_voltage_idx = 0<br/>
    solaredge_ac_current_idx = 0<br/>
    solaredge_ac_power_idx = 0<br/>
    solaredge_inverter_temp_idx = 0<br/>
    solaredge_total_energy_idx = 0<br/>
    solaredge_inverter_state_idx = 0<br/>

3. copy files to raspberry pi, for example in: /home/pi/domoticz/scripts/python/

4. add crontab job, sudo crontab-e
for example every minute:
*/1 * * * * /usr/bin/python3 /home/pi/domoticz/scripts/python/dz_se_comm.py

First time it configures all hardware and sensor devices. 
After that it updates the values in Domoticz.

Problems? 
Start with turning on 'DEBUG_ON = 1' in dz_se_lib.py
<img width=“964” alt=“” src=“https://github.com/strebrah/Solaredge_Domoticz_Modbus/blob/master/images/screenshot_DZ.png”>

