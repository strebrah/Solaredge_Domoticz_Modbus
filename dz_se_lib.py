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

import configparser
import json
import os
import re
import urllib.parse

import requests
import solaredge_modbus

# 'debug_on' argument will printout debug data
print_debug_information = ""
domoticz_ip = ""
domoticz_port = ""
baseurl = ""


def domoticz_create_hardware(settings, session):
    domoticz_hw_idx_found = 'unknown'
    domoticz_hw_name = settings.get('USER SETTINGS', 'domoticz_hw_name')
    urlmessage = str(baseurl) + '/json.htm?type=command&param=addhardware&htype=15&port=1&name=' + str(
        domoticz_hw_name) + '&enabled=true'
    post_request(urlmessage, session)

    urlmessage = baseurl + '/json.htm?type=hardware'
    try:
        data = session.get(urlmessage).text
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    data = json.loads(data)
    for i in data['result']:
        if (i["Name"]) == domoticz_hw_name:
            domoticz_hw_idx_found = i["idx"]
            break
    cfgfile = open(get_path_to_init_file(), 'w')
    settings.set('IDX LIST', 'domoticz_hw_idx', domoticz_hw_idx_found)
    settings.write(cfgfile)
    cfgfile.close()
    print("Created hardware device in domoticz\n")


def domoticz_create_devices(settings, session, inverter_handler):
    bigpart_of_url = baseurl + '/json.htm?type=createdevice&idx=' + str(settings.get('IDX LIST', 'domoticz_hw_idx')) + \
                     '&sensorname='

    values = inverter_handler.read_all()

    if values['c_sunspec_did'] is solaredge_modbus.sunspecDID.THREE_PHASE_INVERTER:

        # AC VOLTAGE P1
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p1'))) + '&devicetype=243&devicesubtype=8'
        post_request(urlmessage, session)

        # AC VOLTAGE P2
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p2'))) + '&devicetype=243&devicesubtype=8'
        post_request(urlmessage, session)

        # AC VOLTAGE P3
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p3'))) + '&devicetype=243&devicesubtype=8'
        post_request(urlmessage, session)

        # AC VOLTAGE P1-N
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p1n'))) + '&devicetype=243&devicesubtype=8'
        post_request(urlmessage, session)

        # AC VOLTAGE P2-N
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p2n'))) + '&devicetype=243&devicesubtype=8'
        post_request(urlmessage, session)

        # AC VOLTAGE P3-N
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p3n'))) + '&devicetype=243&devicesubtype=8'
        post_request(urlmessage, session)

        # AC CURRENT P1
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_current_p1'))) + '&devicetype=243&devicesubtype=23'
        post_request(urlmessage, session)

        # AC CURRENT P2
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_current_p1'))) + '&devicetype=243&devicesubtype=23'
        post_request(urlmessage, session)

        # AC CURRENT P3
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_current_p1'))) + '&devicetype=243&devicesubtype=23'
        post_request(urlmessage, session)
    else:

        # AC VOLTAGE
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage'))) + '&devicetype=243&devicesubtype=8'
        post_request(urlmessage, session)

        # AC CURRENT
        urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_current'))) + '&devicetype=243&devicesubtype=23'
        post_request(urlmessage, session)

    # DC VOLTAGE
    urlmessage = bigpart_of_url + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_dc_voltage'), )) + '&devicetype=243&devicesubtype=8'
    post_request(urlmessage, session)

    # DC CURRENT
    urlmessage = bigpart_of_url + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_dc_current'))) + '&devicetype=243&devicesubtype=23'
    post_request(urlmessage, session)

    # DC POWER
    urlmessage = bigpart_of_url + str(
        urllib.parse.quote(settings.get('SENSOR NAME LIST', 'solaredge_dc_power'))) + '&devicetype=248&devicesubtype=1'
    post_request(urlmessage, session)

    # AC POWER
    urlmessage = bigpart_of_url + str(
        urllib.parse.quote(settings.get('SENSOR NAME LIST', 'solaredge_ac_power'))) + '&devicetype=248&devicesubtype=1'
    post_request(urlmessage, session)

    # AC POWER APPARENT
    urlmessage = bigpart_of_url + str(
        urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_power_apparent'))) + '&devicetype=243&devicesubtype=31&sensoroptions=1;VA'
    post_request(urlmessage, session)

    # AC POWER REACTIVE
    urlmessage = bigpart_of_url + str(
        urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_ac_power_reactive'))) + '&devicetype=243&devicesubtype=31&sensoroptions=1;VAr'
    post_request(urlmessage, session)

    # FREQUENCY
    urlmessage = bigpart_of_url + str(
        urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_frequency'))) + '&devicetype=243&devicesubtype=31&sensoroptions=1;Hz'
    post_request(urlmessage, session)

    # POWER FACTOR
    urlmessage = bigpart_of_url + str(urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'solaredge_power_factor'))) + '&devicetype=243&devicesubtype=31&sensoroptions=1;pct.'
    post_request(urlmessage, session)

    # INVERTER TEMPERATURE
    urlmessage = bigpart_of_url + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_inverter_temp'))) + '&devicetype=80&devicesubtype=5'
    post_request(urlmessage, session)

    # TOTAL ENERGY
    urlmessage = bigpart_of_url + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_total_energy'))) + '&devicetype=243&devicesubtype=33&Switchtype=4'
    post_request(urlmessage, session)

    # INVERTER STATE
    urlmessage = bigpart_of_url + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_inverter_state'))) + '&devicetype=243&devicesubtype=19'
    post_request(urlmessage, session)

    # RESIDENCE POWER CONSUMPTION
    urlmessage = bigpart_of_url + str(
        urllib.parse.quote(
            settings.get('SENSOR NAME LIST', 'residence_power_consumption'))) + '&devicetype=248&devicesubtype=1'
    post_request(urlmessage, session)

    cfgfile = open(get_path_to_init_file(), 'w')
    settings.set('CURRENT STATE', 'inverter_type', solaredge_modbus.C_SUNSPEC_DID_MAP[str(values['c_sunspec_did'])])
    settings.write(cfgfile)
    cfgfile.close()

    print("Created devices in domoticz\n")


def domoticz_retrieve_device_idx(settings, session):
    cfgfile = open(get_path_to_init_file(), 'w')
    urlmessage = baseurl + '/json.htm?type=devices&filter=all&used=true'
    try:
        data = session.get(urlmessage).text
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    data = json.loads(data)

    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_dc_voltage')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_dc_voltage_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_dc_current')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_dc_current_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_dc_power')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_dc_power_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_power')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_ac_power_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_power_apparent')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_ac_power_apparent_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_power_reactive')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_ac_power_reactive_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_frequency')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_frequency_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_power_factor')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_power_factor_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_inverter_temp')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_inverter_temp_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_total_energy')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_total_energy_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_inverter_state')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'solaredge_inverter_state_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'residence_power_consumption')):
            found_idx = i["idx"]
            settings.set('IDX LIST', 'residence_power_consumption_idx', found_idx)
            break
    # 3-PHASE:
    if settings.get('CURRENT STATE', 'inverter_type') == 'Three Phase Inverter':
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p1')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_voltage_p1_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p2')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_voltage_p2_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p3')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_voltage_p3_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p1')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_voltage_p1n_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p2')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_voltage_p2n_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage_p3')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_voltage_p3n_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_current_p1')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_current_p1_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_current_p2')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_current_p2_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_current_p3')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_current_p3_idx', found_idx)
                break
    # 1-PHASE:
    else:
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_voltage_idx', found_idx)
                break
        for i in data['result']:
            if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_current')):
                found_idx = i["idx"]
                settings.set('IDX LIST', 'solaredge_ac_current_idx', found_idx)
                break
    settings.set('CURRENT STATE', 'domoticz_solaredge_comm_init_done', '1')
    settings.write(cfgfile)
    cfgfile.close()
    print("Retrieved and stored IDX values from Domoticz\n")


def domoticz_transceive_data(settings, session, inverter_handler):
    global baseurl

    values = inverter_handler.read_all()
    transceiveurl = baseurl + '/json.htm?type=command&param=udevice&idx='

    if print_debug_information == 'on':
        print_solaredge_data(values, inverter_handler)

    if (solaredge_modbus.INVERTER_STATUS_MAP[values['status']] != get_current_inverterstate(settings)) or (
            get_current_inverterstate(settings) == 0):
        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_inverter_state_idx')) + '&svalue=' + \
                     str('Model:' + values['c_model'] + '\n'
                         + 'Type:' + solaredge_modbus.C_SUNSPEC_DID_MAP[str(values['c_sunspec_did'])] + '\n'
                         + 'Version:' + values['c_version'] + '\n'
                         + 'Serial:' + values['c_serialnumber'] + '\n'
                         + 'Status: ' + solaredge_modbus.INVERTER_STATUS_MAP[values['status']] + '\n')
        post_request(urlmessage, session)
        set_current_inverterstate(settings, solaredge_modbus.INVERTER_STATUS_MAP[values['status']])

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_inverter_temp_idx')) + '&svalue=' + str(
        (values['temperature'] * (10 ** values['temperature_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_ac_current_idx')) + '&svalue=' + str(
        (values['current'] * (10 ** values['temperature_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_ac_power_apparent_idx')) + '&svalue=' + str(
        (values['power_apparent'] * (10 ** values['power_apparent_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_ac_power_reactive_idx')) + '&svalue=' + str(
        (values['power_reactive'] * (10 ** values['power_reactive_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_frequency_idx')) + '&svalue=' + str(
        (values['frequency'] * (10 ** values['frequency_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_power_factor_idx')) + '&svalue=' + str(
        (values['power_factor'] * (10 ** values['power_factor_scale'])))
    post_request(urlmessage, session)

    # 3-PHASE:
    if values['c_sunspec_did'] is solaredge_modbus.sunspecDID.THREE_PHASE_INVERTER:
        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_current_p1_idx')) + '&svalue=' + str(
            (values['current'] * (10 ** values['temperature_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_current_p2_idx')) + '&svalue=' + str(
            (values['current'] * (10 ** values['temperature_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_current_p3_idx')) + '&svalue=' + str(
            (values['current'] * (10 ** values['temperature_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_voltage_p1_idx')) + '&svalue=' + str(
            (values['p1_voltage'] * (10 ** values['voltage_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_voltage_p2_idx')) + '&svalue=' + str(
            (values['p1_voltage'] * (10 ** values['voltage_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_voltage_p3_idx')) + '&svalue=' + str(
            (values['p1_voltage'] * (10 ** values['voltage_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_voltage_p1n_idx')) + '&svalue=' + str(
            (values['p1_voltage'] * (10 ** values['voltage_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_voltage_p2n_idx')) + '&svalue=' + str(
            (values['p1_voltage'] * (10 ** values['voltage_scale'])))
        post_request(urlmessage, session)

        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_voltage_p3n_idx')) + '&svalue=' + str(
            (values['p1_voltage'] * (10 ** values['voltage_scale'])))
        post_request(urlmessage, session)
    else:
        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'solaredge_ac_voltage_idx')) + '&svalue=' + str(
            (values['p1_voltage'] * (10 ** values['voltage_scale'])))
        post_request(urlmessage, session)

    ac_power = (values['power_ac'] * (10 ** values['power_ac_scale']))
    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_ac_power_idx')) + '&svalue=' + str(ac_power)
    post_request(urlmessage, session)

    if (settings.get('USER SETTINGS', 'p1_energy_delivery_to_grid_idx') != '-1') or (
            settings.get('USER SETTINGS', 'p1_energy_usage_idx') != '-1'):
        urlmessage = transceiveurl + str(
            settings.get('IDX LIST', 'residence_power_consumption_idx')) + '&svalue=' + str(
            calculate_actual_residence_power_consumption(settings, session, ac_power))
        post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_total_energy_idx')) + '&svalue=' + str(
        (values['energy_total'] * (10 ** values['energy_total_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_dc_current_idx')) + '&svalue=' + str(
        (values['current_dc'] * (10 ** values['current_dc_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_dc_voltage_idx')) + '&svalue=' + str(
        (values['voltage_dc'] * (10 ** values['voltage_dc_scale'])))
    post_request(urlmessage, session)

    urlmessage = transceiveurl + str(
        settings.get('IDX LIST', 'solaredge_dc_power_idx')) + '&svalue=' + str(
        (values['power_dc'] * (10 ** values['power_dc_scale'])))
    post_request(urlmessage, session)


def get_current_inverterstate(settings):
    return settings.get('CURRENT STATE', 'inverter_state')


def set_current_inverterstate(settings, state):
    cfgfile = open(get_path_to_init_file(), 'w')
    settings.set('CURRENT STATE', 'inverter_state', state)
    settings.write(cfgfile)
    cfgfile.close()


def get_path_to_init_file():
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    initfile = os.path.join(thisfolder, 'dz_se_settings.ini')
    return initfile


def calculate_actual_residence_power_consumption(settings, session, pv_generated_energy):
    urlmessage = baseurl + '/json.htm?type=devices&rid=' + str(
        settings.get('USER SETTINGS', 'p1_energy_delivery_to_grid_idx'))
    try:
        data = session.get(urlmessage).text
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    data = json.loads(data)
    p1_energy_delivery_to_grid = data["result"][0]["Data"]
    if not p1_energy_delivery_to_grid[0].isdigit():
        print("p1 energy delivery to grid value is not a numeric value")
        raise SystemExit()
    urlmessage = baseurl + '/json.htm?type=devices&rid=' + str(
        settings.get('USER SETTINGS', 'p1_energy_usage_idx'))

    try:
        data = session.get(urlmessage).text
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    data = json.loads(data)
    p1_energy_usage = data["result"][0]["Data"]
    if not p1_energy_usage[0].isdigit():
        print("p1 energy usage value is not a numeric value")
        raise SystemExit()
    p1_energy_delivery_to_grid = re.sub('[^0-9]', '', p1_energy_delivery_to_grid)
    p1_energy_usage = re.sub('[^0-9]', '', p1_energy_usage)
    return str(pv_generated_energy - (float(p1_energy_delivery_to_grid) + float(p1_energy_usage)))


def sys_init():
    global domoticz_ip
    global domoticz_port
    global baseurl

    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(get_path_to_init_file())

    domoticz_ip = settings.get('USER SETTINGS', 'domoticz_ip')
    domoticz_port = settings.get('USER SETTINGS', 'domoticz_port')
    if not domoticz_port.isnumeric():
        print("domoticz_port is not a numeric value")
        raise SystemExit()
    baseurl = 'http://' + domoticz_ip + ':' + domoticz_port
    session = requests.Session()

    solaredge_inverter_ip = settings.get('USER SETTINGS', 'solaredge_inverter_ip')
    solaredge_inverter_port = settings.get('USER SETTINGS', 'solaredge_inverter_port')
    if not solaredge_inverter_port.isnumeric():
        print("solaredge_inverter_port is not a numeric value")
        raise SystemExit()

    inverter_handler = solaredge_modbus.Inverter(host=solaredge_inverter_ip,
                                                 port=solaredge_inverter_port,
                                                 timeout=1,
                                                 unit=1)

    return settings, session, inverter_handler


def post_request(url, session):
    try:
        session.post(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_request(url, session):
    try:
        data = session.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return data


def print_solaredge_data(values, inverter_handler):
    print(f"{inverter_handler}:")
    print("\nRegisters:")
    print(f"Model: {values['c_model']}")
    print(f"Type: {solaredge_modbus.C_SUNSPEC_DID_MAP[str(values['c_sunspec_did'])]}")
    print(f"Version: {values['c_version']}")
    print(f"Serial: {values['c_serialnumber']}")
    print(f"Status: {solaredge_modbus.INVERTER_STATUS_MAP[values['status']]}")
    print(
        f"Temperature: {(values['temperature'] * (10 ** values['temperature_scale'])):.2f}{inverter_handler.registers['temperature'][6]}")
    print(
        f"AC Current: {(values['current'] * (10 ** values['temperature_scale'])):.2f}{inverter_handler.registers['current'][6]}")
    if values['c_sunspec_did'] is solaredge_modbus.sunspecDID.THREE_PHASE_INVERTER:
        print(
            f"Phase 1 Current: {(values['p1_current'] * (10 ** values['current_scale'])):.2f}{inverter_handler.registers['p1_current'][6]}")
        print(
            f"Phase 2 Current: {(values['p2_current'] * (10 ** values['current_scale'])):.2f}{inverter_handler.registers['p2_current'][6]}")
        print(
            f"Phase 3 Current: {(values['p3_current'] * (10 ** values['current_scale'])):.2f}{inverter_handler.registers['p3_current'][6]}")
        print(
            f"Phase 1 voltage: {(values['p1_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter_handler.registers['p1_voltage'][6]}")
        print(
            f"Phase 2 voltage: {(values['p2_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter_handler.registers['p2_voltage'][6]}")
        print(
            f"Phase 3 voltage: {(values['p3_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter_handler.registers['p3_voltage'][6]}")
        print(
            f"Phase 1-N voltage: {(values['p1n_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter_handler.registers['p1n_voltage'][6]}")
        print(
            f"Phase 2-N voltage: {(values['p2n_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter_handler.registers['p2n_voltage'][6]}")
        print(
            f"Phase 3-N voltage: {(values['p3n_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter_handler.registers['p3n_voltage'][6]}")
    else:
        print(
            f"AC Voltage: {(values['p1_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter_handler.registers['p1_voltage'][6]}")
    print(
        f"Frequency: {(values['frequency'] * (10 ** values['frequency_scale'])):.2f}{inverter_handler.registers['frequency'][6]}")
    print(
        f"Power: {(values['power_ac'] * (10 ** values['power_ac_scale'])):.2f}{inverter_handler.registers['power_ac'][6]}")
    print(
        f"Power (Apparent): {(values['power_apparent'] * (10 ** values['power_apparent_scale'])):.2f}{inverter_handler.registers['power_apparent'][6]}")
    print(
        f"Power (Reactive): {(values['power_reactive'] * (10 ** values['power_reactive_scale'])):.2f}{inverter_handler.registers['power_reactive'][6]}")
    print(
        f"Power Factor: {(values['power_factor'] * (10 ** values['power_factor_scale'])):.2f}{inverter_handler.registers['power_factor'][6]}")
    print(
        f"Total Energy: {(values['energy_total'] * (10 ** values['energy_total_scale']))}{inverter_handler.registers['energy_total'][6]}")
    print(
        f"DC Current: {(values['current_dc'] * (10 ** values['current_dc_scale'])):.2f}{inverter_handler.registers['current_dc'][6]}")
    print(
        f"DC Voltage: {(values['voltage_dc'] * (10 ** values['voltage_dc_scale'])):.2f}{inverter_handler.registers['voltage_dc'][6]}")
    print(
        f"DC Power: {(values['power_dc'] * (10 ** values['power_dc_scale'])):.2f}{inverter_handler.registers['power_dc'][6]}")


def debug_information(state):
    global print_debug_information

    state = state.lower()
    if state == 'debug_off':
        print_debug_information = 'off'
    elif state == 'debug_on':
        print_debug_information = 'on'
    else:
        print('invalid argument! use -h')


def debug_information_state():
    global print_debug_information
    return print_debug_information


def get_domoticz_ip():
    global domoticz_ip
    return domoticz_ip


def get_domoticz_port():
    global domoticz_port
    return domoticz_port
