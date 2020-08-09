#!/usr/bin/env python3
####################################################################################################
# Created by EH (NL) https://github.com/strebrah/Solaredge_Domoticz_Modbus                         #
# Date: August 2020                                                                                #
# Version: 0.1                                                                                     #
# Designed for python 3.7 (based on the requirements of the 'solaredge_modbus' library.)           #
# Thanks to Niels for the 'solaredge_modbus' library https://pypi.org/project/solaredge-modbus/    #
# Capabilities:                                                                                    #
#   *  Creating a hardware device in Domoticz                                                      #
#   *  Creating sensors for the data types in Domoticz                                             #
#   *  Sending the solaredge modbus data to Domoticz                                               #
# How to use                                                                                       #
#    1. Enter your configuration in the 'dz_se_settings.ini' file                                  #
#    2. configure crontab task for periodic data transfer to Domoticz.                             #
#    example:                                                                                      #
#    sudo crontab -e                                                                               #
#    for example, every minute                                                                     #
#    */1 * * * * /usr/bin/python3 /home/pi/domoticz/scripts/python/dz_se_comm.py                   #
####################################################################################################


import requests
import configparser
import time
import solaredge_modbus

from dz_se_lib import domoticz_create_hardware
from dz_se_lib import domoticz_create_devices
from dz_se_lib import domoticz_retrieve_device_idx
from dz_se_lib import domoticz_transceive_data
from dz_se_lib import get_path_to_init_file

if __name__ == "__main__":

    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(get_path_to_init_file())

    domoticz_ip = settings.get('GENERAL SETTINGS', 'domoticz_ip')
    domoticz_port = settings.get('GENERAL SETTINGS', 'domoticz_port')
    inverter = solaredge_modbus.Inverter(host=settings.get('GENERAL SETTINGS', 'solaredge_inverter_ip'),
                                         port=settings.get('GENERAL SETTINGS', 'solaredge_inverter_port'), timeout=1,
                                         unit=1)

    # Get values from Solaredge inverter over TCP Modbus
    if settings.get('GENERAL SETTINGS', 'domoticz_solaredge_comm_init_done') == '0':
        session = requests.Session()
        # SET HARDWARE IN DOMOTICZ
        DOMOTICZ_HW_IDX = domoticz_create_hardware(domoticz_ip, domoticz_port, settings, session)
        # CREATE DEVICES IN DOMOTICZ
        domoticz_create_devices(domoticz_ip, domoticz_port, settings, session, DOMOTICZ_HW_IDX)
        # GET ALL SENSOR IDX VALUES AND STORE
        domoticz_retrieve_device_idx(domoticz_ip, domoticz_port, settings, session)
        session.close()
    else:
        time.sleep(0.5)
        session = requests.Session()
        domoticz_transceive_data(domoticz_ip, domoticz_port, settings, session, inverter)
        session.close()
