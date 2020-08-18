#!/usr/bin/env python3
####################################################################################################
# Created by EH (NL) https://github.com/strebrah/Solaredge_Domoticz_Modbus                         #
# Date: August 2020                                                                                #
# Version: 0.2                                                                                     #
# Designed for python 3.7 (based on the requirements of the 'solaredge_modbus' library.)           #
# Thanks to Niels for the 'solaredge_modbus' library https://pypi.org/project/solaredge-modbus/    #
# Capabilities:                                                                                    #
#   *  Creating a hardware device in Domoticz                                                      #
#   *  Creating sensors for the data types in Domoticz                                             #
#   *  Sending the solaredge modbus data to Domoticz                                               #
#   *  Calculating residence usage, based on P1 meters and Solaredge inverter data                 #
# How to use                                                                                       #
#    1. Enter your configuration under 'USER SETTINGS in the 'dz_se_settings.ini' file             #
#    2. configure crontab task for periodic data transfer to Domoticz.                             #
#    example:                                                                                      #
#    sudo crontab -e                                                                               #
#    for example, every minute                                                                     #
#    */1 * * * * /usr/bin/python3 /home/pi/domoticz/scripts/python/dz_se_comm.py debug_off         #
####################################################################################################

import argparse
import time

from dz_se_lib import domoticz_create_hardware
from dz_se_lib import domoticz_create_devices
from dz_se_lib import domoticz_retrieve_device_idx
from dz_se_lib import domoticz_transceive_data
from dz_se_lib import sys_init
from dz_se_lib import debug_information
from dz_se_lib import debug_information_state

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("debug_information", type=str, help="debug information: use 'debug_on' or 'debug_off'")
    args = argparser.parse_args()
    debug_information(args.debug_information)

    if debug_information_state() == 'on':
        start = time.time()

    settings, session, inverter_handler = sys_init()

    # Get values from Solaredge inverter over Modbus TCP
    if settings.get('CURRENT STATE', 'domoticz_solaredge_comm_init_done') == '0':
        # SET HARDWARE IN DOMOTICZ
        domoticz_create_hardware(settings, session)
        # CREATE DEVICES IN DOMOTICZ
        domoticz_create_devices(settings, session, inverter_handler)
        # GET ALL SENSOR IDX VALUES AND STORE
        domoticz_retrieve_device_idx(settings, session)
        session.close()
    else:
        # Sent data to Domoticz
        domoticz_transceive_data(settings, session, inverter_handler)
        session.close()
        if debug_information_state() == 'on':
            end = time.time()
            print("\nSolaredge to Domoticz update in", round(end - start, 3), "seconds")
