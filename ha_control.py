import requests
from pprint import pprint
import datetime
HA_URL = "http://192.168.x.x:8123"
TOKEN = "xxx"


def get_value(sensor):
    url = f"{HA_URL}/api/states/{sensor}"
    # Headers
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    # Make the GET request
    response = requests.get(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        sensor_data = response.json()
        #pprint(sensor_data)
        #prices = sensor_data['attributes']['raw_today'] + sensor_data['attributes']['raw_tomorrow']
        return(sensor_data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return()

def set_ha_number(variable, value):
    url = f"{HA_URL}/api/services/number/set_value"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "entity_id": variable,
        "value": value
    }
    print("Setting %s to %s" % (variable, value))
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        pass
        #print("Select option set successfully.")
    else:
        print(f"Failed to set select option. Status Code: {response.status_code}")
        print(f"Response: {response.text}")

def set_ha_input_number(variable, value):
    url = f"{HA_URL}/api/services/input_number/set_value"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "entity_id": variable,
        "value": value
    }
    print("Setting %s to %s" % (variable, value))
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        pass
        #print("Select option set successfully.")
    else:
        print(f"Failed to set select option. Status Code: {response.status_code}")
        print(f"Response: {response.text}")


def set_ha_variable(variable, value):
    # API Endpoint
    url = f"{HA_URL}/api/services/select/select_option"
    # Headers
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    # Payload
    payload = {
        "entity_id": variable,
        "option": value
    }
    print("Setting %s to %s" % (variable, value))
    # Send POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check the response
    if response.status_code == 200:
        pass
        #print("Select option set successfully.")
    else:
        print(f"Failed to set select option. Status Code: {response.status_code}")
        print(f"Response: {response.text}")

def get_battery_level():
    res = float(get_value("sensor.solax_battery_capacity")['state'])
    return(res)

def get_current_price():
    res = float(get_value("sensor.nordpool_kwh_lt_eur_3_10_021")['state'])
    return(res)

def set_solax_grid_charge(set):
    if set == 1:
        value = 'Enabled'
    else:
        value = 'Disabled'
    variable = 'select.solax_selfuse_night_charge_enable'
    set_ha_variable(variable, value)

def set_solax_charge_start(time):
    variable = 'select.solax_charger_start_time_1'
    value = convert_time(time, 0)
    set_ha_variable(variable, value)
    #set_solax_grid_charge(1)

def set_solax_charge_end(time):
    variable = 'select.solax_charger_end_time_1'
    #add one minute to charge end time, to prevent switching at the end of the hour during crontab
    value = convert_time(time, 5)
    set_ha_variable(variable, value)


def set_solax_discharge_start(time):
    variable = 'select.solax_discharger_start_time_1'
    value = convert_time(time, 0)
    set_ha_variable(variable, value)

def set_solax_discharge_end(time):
    variable = 'select.solax_discharger_end_time_1'
    value = convert_time(time, 5)
    set_ha_variable(variable, value)

def disable_solax_discharge():
    variable = 'select.solax_discharger_start_time_1'
    set_ha_variable(variable, '00:00')
    variable = 'select.solax_discharger_end_time_1'
    set_ha_variable(variable, '00:00')

def disable_solax_charge():
    variable = 'select.solax_charger_start_time_1'
    set_ha_variable(variable, '00:00')
    variable = 'select.solax_charger_end_time_1'
    set_ha_variable(variable, '00:00')
    set_solax_grid_charge(0)

def round_to_nearest_five(n):
    return 5 * round(n / 5)

def convert_time(time_str, add_offset):
    aware_dt = datetime.datetime.fromisoformat(time_str)
    offset = datetime.timedelta(minutes = add_offset)
    #offset = aware_dt.utcoffset()
    #skip offet, looks like it's not being sent correctly
    shifted_dt = aware_dt + offset
    hours = shifted_dt.hour
    minutes = shifted_dt.minute
    min5 =  round_to_nearest_five(minutes)
    if min5 > 55:
        min5 = 55
    res = '%02d:%02d' % (int(hours), int(min5))
    return(res)
