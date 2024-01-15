#!/usr/bin/env python3
####################################################################################################
# Created by EH (NL) https://github.com/strebrah/Solaredge_Domoticz_Modbus                         #
# Date: August 2020                                                                                #
# Version: 0.1                                                                                     #
# Designed for python 3.7 (based on the requirements of the 'solaredge_modbus' library.)           #
# Thanks to Niels for the 'solaredge_modbus' library https://pypi.org/project/solaredge-modbus/    #
# Read instruction on https://github.com/strebrah/Solaredge_Domoticz_Modbus     				   # 
####################################################################################################
# DOCS
# https://www.domoticz.com/wiki/Developing_a_Python_plugin#Available_Device_Types

import urllib.parse
import json
import time
import solaredge_modbus
import os

# '1' will printout debug data
DEBUG_ON = 0

def domoticz_create_hardware(domoticz_ip, domoticz_port, settings, session):
    domoticz_hw_name = settings.get('GENERAL SETTINGS', 'domoticz_hw_name')
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=addhardware&htype=15&port=1&name=' + str(
        domoticz_hw_name) + '&enabled=true'
    r = session.get(urlmessage)
    if DEBUG_ON:
        print(r)
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=hardware'
    data = session.get(urlmessage).text
    data = json.loads(data)
    for i in data['result']:
        if (i["Name"]) == domoticz_hw_name:
            domoticz_hw_idx_found = i["idx"]
            break
    cfgfile = open(get_path_to_init_file(), 'w')
    settings.set('GENERAL SETTINGS', 'domoticz_hw_idx', domoticz_hw_idx_found)
    settings.write(cfgfile)
    cfgfile.close()
    print("Created hardware device in domoticz\n")
    return domoticz_hw_idx_found


def domoticz_create_devices(domoticz_ip, domoticz_port, settings, session, domoticz_hw_idx):
    # DC VOLTAGE
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_dc_voltage'), )) + '&devicetype=243&devicesubtype=8'
    data = session.get(urlmessage)

    # DC CURRENT
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_dc_current'))) + '&devicetype=243&devicesubtype=23'
    data = session.get(urlmessage)

    # DC POWER
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(
        urllib.parse.quote(settings.get('SENSOR NAME LIST', 'solaredge_dc_power'))) + '&devicetype=248&devicesubtype=1'
    data = session.get(urlmessage)

    # AC VOLTAGE
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage'))) + '&devicetype=243&devicesubtype=8'
    data = session.get(urlmessage)

    # AC CURRENT
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_ac_current'))) + '&devicetype=243&devicesubtype=23'
    data = session.get(urlmessage)

    # AC POWER
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(
        urllib.parse.quote(settings.get('SENSOR NAME LIST', 'solaredge_ac_power'))) + '&devicetype=248&devicesubtype=1'
    data = session.get(urlmessage)

    # INVERTER TEMPERATURE
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_inverter_temp'))) + '&devicetype=80&devicesubtype=5'
    data = session.get(urlmessage)

    # TOTAL ENERGY
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_total_energy'))) + '&devicetype=243&devicesubtype=33&Switchtype=4'
    data = session.get(urlmessage)

    # INVERTER STATE
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=createdevice&idx=' + str(
        domoticz_hw_idx) + '&sensorname=' + str(urllib.parse.quote(
        settings.get('SENSOR NAME LIST', 'solaredge_inverter_state'))) + '&devicetype=243&devicesubtype=19'
    data = session.get(urlmessage)
    print("Created devices in domoticz\n")


def domoticz_retrieve_device_idx(domoticz_ip, domoticz_port, settings, session):
    cfgfile = open(get_path_to_init_file(), 'w')
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=devices&filter=all&used=true'
    data = session.get(urlmessage).text
    data = json.loads(data)

    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_dc_voltage')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_dc_voltage_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_dc_current')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_dc_current_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_dc_power')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_dc_power_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_voltage')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_ac_voltage_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_current')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_ac_current_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_ac_power')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_ac_power_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_inverter_temp')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_inverter_temp_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_total_energy')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_total_energy_idx', found_idx)
            break
    for i in data['result']:
        if (i["Name"]) == (settings.get('SENSOR NAME LIST', 'solaredge_inverter_state')):
            found_idx = i["idx"]
            settings.set('SENSOR IDX LIST', 'solaredge_inverter_state_idx', found_idx)
            break
    settings.set('GENERAL SETTINGS', 'domoticz_solaredge_comm_init_done', '1')
    settings.write(cfgfile)
    cfgfile.close()
    print("Retrieved and stored IDX values from Domoticz\n")


def domoticz_transceive_data(domoticz_ip, domoticz_port, settings, session, inverter):
    values = inverter.read_all()
    if DEBUG_ON:
        print(f"{inverter}:")
        print("\nRegisters:")
        print(f"\tModel: {values['c_model']}")
        print(f"\tType: {solaredge_modbus.C_SUNSPEC_DID_MAP[str(values['c_sunspec_did'])]}")
        print(f"\tVersion: {values['c_version']}")
        print(f"\tSerial: {values['c_serialnumber']}")
        print(f"\tStatus: {solaredge_modbus.INVERTER_STATUS_MAP[values['status']]}")
    if (solaredge_modbus.INVERTER_STATUS_MAP[values['status']] != get_current_inverterstate(settings)) or (get_current_inverterstate(settings) == 0):
        urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
            settings.get('SENSOR IDX LIST', 'solaredge_inverter_state_idx')) + '&svalue=' + \
                     str('Model:' + values['c_model'] + '\n'
                         + 'Type:' + solaredge_modbus.C_SUNSPEC_DID_MAP[str(values['c_sunspec_did'])] + '\n'
                         + 'Version:' + values['c_version'] + '\n'
                         + 'Serial:' + values['c_serialnumber'] + '\n'
                         + 'Status: ' + solaredge_modbus.INVERTER_STATUS_MAP[values['status']])
        r = session.post(urlmessage)
        time.sleep(0.5)
        set_current_inverterstate(settings, solaredge_modbus.INVERTER_STATUS_MAP[values['status']])
    if DEBUG_ON:
        print(
            f"\tTemperature: {(values['temperature'] * (10 ** values['temperature_scale'])):.2f}{inverter.registers['temperature'][6]}")
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
        settings.get('SENSOR IDX LIST', 'solaredge_inverter_temp_idx')) + '&svalue=' + str(
        (values['temperature'] * (10 ** values['temperature_scale'])))
    r = session.post(urlmessage)
    if DEBUG_ON:
        print(r)
    time.sleep(0.5)
    if DEBUG_ON:
        print(
            f"\tAC Current: {(values['current'] * (10 ** values['temperature_scale'])):.2f}{inverter.registers['current'][6]}")
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
        settings.get('SENSOR IDX LIST', 'solaredge_ac_current_idx')) + '&svalue=' + str(
        (values['current'] * (10 ** values['temperature_scale'])))
    r = session.post(urlmessage)
    if DEBUG_ON:
        print(r)
    time.sleep(0.5)
    if values['c_sunspec_did'] is solaredge_modbus.sunspecDID.THREE_PHASE_INVERTER:
        print(
            f"\tPhase 1 Current: {(values['p1_current'] * (10 ** values['current_scale'])):.2f}{inverter.registers['p1_current'][6]}")
        print(
            f"\tPhase 2 Current: {(values['p2_current'] * (10 ** values['current_scale'])):.2f}{inverter.registers['p2_current'][6]}")
        print(
            f"\tPhase 3 Current: {(values['p3_current'] * (10 ** values['current_scale'])):.2f}{inverter.registers['p3_current'][6]}")
        print(
            f"\tPhase 1 voltage: {(values['p1_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter.registers['p1_voltage'][6]}")
        print(
            f"\tPhase 2 voltage: {(values['p1_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter.registers['p1_voltage'][6]}")
        print(
            f"\tPhase 3 voltage: {(values['p1_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter.registers['p1_voltage'][6]}")
        print(
            f"\tPhase 1-N voltage: {(values['p1n_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter.registers['p1n_voltage'][6]}")
        print(
            f"\tPhase 2-N voltage: {(values['p2n_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter.registers['p2n_voltage'][6]}")
        print(
            f"\tPhase 3-N voltage: {(values['p3n_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter.registers['p3n_voltage'][6]}")
    else:
        if DEBUG_ON:
            print(f"\tAC Voltage: {(values['l1_voltage'] * (10 ** values['voltage_scale'])):.2f}{inverter.registers['l1_voltage'][6]}")
        urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
            settings.get('SENSOR IDX LIST', 'solaredge_ac_voltage_idx')) + '&svalue=' + str(
            (values['l1_voltage'] * (10 ** values['voltage_scale'])))
        r = session.post(urlmessage)
        if DEBUG_ON:
            print(r)
        time.sleep(0.5)
    # print(f"\tFrequency: {(values['frequency'] * (10 ** values['frequency_scale'])):.2f}{inverter.registers['frequency'][6]}")
    if DEBUG_ON:
        print(f"\tPower: {(values['power_ac'] * (10 ** values['power_ac_scale'])):.2f}{inverter.registers['power_ac'][6]}")
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
        settings.get('SENSOR IDX LIST', 'solaredge_ac_power_idx')) + '&svalue=' + str(
        (values['power_ac'] * (10 ** values['power_ac_scale'])))
    r = session.post(urlmessage)
    if DEBUG_ON:
        print(r)
    time.sleep(0.5)
    # print(f"\tPower (Apparent): {(values['power_apparent'] * (10 ** values['power_apparent_scale'])):.2f}{inverter.registers['power_apparent'][6]}")
    # print(f"\tPower (Reactive): {(values['power_reactive'] * (10 ** values['power_reactive_scale'])):.2f}{inverter.registers['power_reactive'][6]}")
    # print(f"\tPower Factor: {(values['power_factor'] * (10 ** values['power_factor_scale'])):.2f}{inverter.registers['power_factor'][6]}")
    if DEBUG_ON:
        print(f"\tTotal Energy: {(values['energy_total'] * (10 ** values['energy_total_scale']))}{inverter.registers['energy_total'][6]}")
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
        settings.get('SENSOR IDX LIST', 'solaredge_total_energy_idx')) + '&svalue=' + str(
        (values['energy_total'] * (10 ** values['energy_total_scale'])))
    r = session.post(urlmessage)
    if DEBUG_ON:
        print(r)
    time.sleep(0.5)
    # print(urlmessage)
    if DEBUG_ON:
        print(f"\tDC Current: {(values['current_dc'] * (10 ** values['current_dc_scale'])):.2f}{inverter.registers['current_dc'][6]}")
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
        settings.get('SENSOR IDX LIST', 'solaredge_dc_current_idx')) + '&svalue=' + str(
        (values['current_dc'] * (10 ** values['current_dc_scale'])))
    r = session.post(urlmessage)
    if DEBUG_ON:
        print(r)
    time.sleep(0.5)
    if DEBUG_ON:
        print(f"\tDC Voltage: {(values['voltage_dc'] * (10 ** values['voltage_dc_scale'])):.2f}{inverter.registers['voltage_dc'][6]}")
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
        settings.get('SENSOR IDX LIST', 'solaredge_dc_voltage_idx')) + '&svalue=' + str(
        (values['voltage_dc'] * (10 ** values['voltage_dc_scale'])))
    r = session.post(urlmessage)
    if DEBUG_ON:
        print(r)
    time.sleep(0.5)
    if DEBUG_ON:
        print(
            f"\tDC Power: {(values['power_dc'] * (10 ** values['power_dc_scale'])):.2f}{inverter.registers['power_dc'][6]}")
    urlmessage = 'http://' + domoticz_ip + ':' + domoticz_port + '/json.htm?type=command&param=udevice&idx=' + str(
        settings.get('SENSOR IDX LIST', 'solaredge_dc_power_idx')) + '&svalue=' + str(
        (values['power_dc'] * (10 ** values['power_dc_scale'])))
    r = session.post(urlmessage)
    if DEBUG_ON:
        print(r)
    time.sleep(0.5)
    print("SE to DZ update\n")


def get_current_inverterstate(settings):
    return settings.get('GENERAL SETTINGS', 'current_inverter_State')

def set_current_inverterstate(settings, state):
    cfgfile = open(get_path_to_init_file(), 'w')
    settings.set('GENERAL SETTINGS', 'current_inverter_state', state)
    settings.write(cfgfile)
    cfgfile.close()

def get_path_to_init_file():
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    initfile = os.path.join(thisfolder, 'dz_se_settings.ini')
    return initfile
