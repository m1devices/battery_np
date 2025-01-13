import ha_control
import datetime
from pprint import pprint

CHEAPEST_HOURS=4
MOST_EXPENSIVE_HOURS=4
MORE_EXPENSIVE_HOURS=12
DELTA=0.03
LOOK_AHEAD=12

def get_cheapest(prices_all, hours):
    #remove history hours and remove more than LOOK_AHEAD hours
    prices = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 20)
    look_ahead = datetime.timedelta(hours = 24)
    for item in prices_all:
        start_time = datetime.datetime.fromisoformat(item['start'])
        now_in_start_tz = now.astimezone(start_time.tzinfo)
        if start_time + delta > now_in_start_tz and start_time - look_ahead < now_in_start_tz:
            prices.append(item)


    pprint(prices_all)
    sorted_data = sorted(prices, key=lambda x: x['value'])
    #pprint(sorted_data)


    cheapest = sorted_data[:CHEAPEST_HOURS]
    sorted_data = sorted(prices, key=lambda x: x['value'], reverse=True)
    #pprint(sorted_data)
    most_expensive = sorted_data[:MOST_EXPENSIVE_HOURS]
    more_expensive = sorted_data[:MORE_EXPENSIVE_HOURS]
    return(cheapest, most_expensive, more_expensive)


#def get_

def calc_delta(cheapest, most_expensive):
    sum = 0
    for item in cheapest:
        sum = sum + item['value']
    cheap_avg = sum / CHEAPEST_HOURS
    sum = 0
    for item in most_expensive:
        sum = sum + item['value']
    exp_avg = sum / MOST_EXPENSIVE_HOURS
    return(exp_avg - cheap_avg)

def get_charge_schedule(period):
    sorted_data = sorted(period, key=lambda x: x['start'])
    pprint(sorted_data)
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 20)

    #check current hour status
    for item in sorted_data:
        start_time = datetime.datetime.fromisoformat(item['start'])
        now_in_start_tz = now.astimezone(start_time.tzinfo)
        if start_time + delta > now_in_start_tz and start_time - delta < now_in_start_tz:
            ha_control.set_solax_charge_start(item['start'])
            ha_control.set_solax_charge_end(item['end'])
            ha_control.set_solax_grid_charge(1)
            return(1)
    ha_control.disable_solax_charge()
    return(0)


def set_soonest_discharge_period(period):
    sorted_data = sorted(period, key=lambda x: x['start'])
    pprint(sorted_data)
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 20)
    
    #check current hour status
    for item in sorted_data:
        start_time = datetime.datetime.fromisoformat(item['start'])
        now_in_start_tz = now.astimezone(start_time.tzinfo)
        if start_time + delta > now_in_start_tz and start_time - delta < now_in_start_tz:
            ha_control.set_solax_discharge_start(item['start'])
            ha_control.set_solax_discharge_end(item['end'])
            return(1)
    ha_control.disable_solax_discharge()
    return(0)

def calc_schedule():

    sensor_data = ha_control.get_value("sensor.nordpool_kwh_lt_eur_3_10_021")
    prices = sensor_data['attributes']['raw_today'] + sensor_data['attributes']['raw_tomorrow']
    cheapest, most_expensive, more_expensive = get_cheapest(prices, CHEAPEST_HOURS)
    delta = calc_delta(cheapest, most_expensive)
    #print(delta)

    #print(cheapest)
    #print()
    #print(most_expensive)
    #get_charge_schedule(cheapest)
    #set_soonest_discharge_period(most_expensive)



calc_schedule()
