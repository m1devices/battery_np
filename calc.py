import ha_control
import datetime
from pprint import pprint
import algo
import sun
import usage

CHEAPEST_HOURS=4
MOST_EXPENSIVE_HOURS=4
MORE_EXPENSIVE_HOURS=12
DELTA=0.05
LOOK_AHEAD=11

MEDIUM_BAT=70
LOW_BAT=30
LOW_PRICE=0.04
HIGH_PRICE=0.15

def get_cheapest(prices_all, hours):
    #remove history hours and remove more than LOOK_AHEAD hours
    prices = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 20)
    look_ahead = datetime.timedelta(hours = LOOK_AHEAD)
    for item in prices_all:
        start_time = datetime.datetime.fromisoformat(item['start'])
        now_in_start_tz = now.astimezone(start_time.tzinfo)
        if start_time + delta > now_in_start_tz and start_time - look_ahead < now_in_start_tz:
            prices.append(item)


    #pprint(prices)
    sorted_data = sorted(prices, key=lambda x: x['value'])
    #print()
    #pprint(sorted_data)
    #print()

    cheapest = sorted_data[:CHEAPEST_HOURS]
    sorted_data = sorted(prices, key=lambda x: x['value'], reverse=True)
    #pprint(sorted_data)
    most_expensive = sorted_data[:MOST_EXPENSIVE_HOURS]
    more_expensive = sorted_data[:MORE_EXPENSIVE_HOURS]
    return(cheapest, most_expensive, more_expensive)


#def get_

def calc_delta(cur_price, cheapest, most_expensive):
    min = 9999
    max = -9999
    for item in cheapest:
        if min > item['value']:
            min = item['value']

    for item in most_expensive:
        if max < item['value']:
            max = item['value']
    #print(max, min)
    return(max - min)

def get_charge_schedule(period):
    sorted_data = sorted(period, key=lambda x: x['start'])
    #pprint(sorted_data)
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
    #pprint(sorted_data)
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

def force_charge():
    now = datetime.datetime.now()
    now_tz = now.astimezone()
    print(now_tz)
    delta = datetime.timedelta(minutes = 60)
    later = now + delta
    later_tz = later.astimezone()
    ha_control.set_solax_charge_start(str(now_tz))
    ha_control.set_solax_charge_end(str(later_tz))
    ha_control.set_solax_grid_charge(1)
    ha_control.disable_solax_discharge()


def force_discharge():
    now = datetime.datetime.now()
    now_tz = now.astimezone()
    print(now_tz)
    delta = datetime.timedelta(minutes = 60)
    later = now + delta
    later_tz = later.astimezone()
    ha_control.set_solax_discharge_start(str(now_tz))
    ha_control.set_solax_discharge_end(str(later_tz))
    ha_control.set_solax_grid_charge(0)

def standby():
    ha_control.disable_solax_discharge()
    ha_control.set_solax_grid_charge(0)

def calc_schedule():

    sensor_data = ha_control.get_value("sensor.nordpool_kwh_lt_eur_3_10_021")
    prices = sensor_data['attributes']['raw_today'] + sensor_data['attributes']['raw_tomorrow']
    cheapest, most_expensive, more_expensive = get_cheapest(prices, CHEAPEST_HOURS)
    bat = ha_control.get_battery_level()
    cur_price = ha_control.get_current_price()


    delta = calc_delta(cur_price, cheapest, most_expensive)
    print("Delta: %.3f" % (delta))

    print("Current price: %.3f EUR, Current battery: %.1f" % (cur_price, bat))
    if delta < DELTA:
        bat = ha_control.get_battery_level()
        cur_price = ha_control.get_current_price()
        print("Bat: %.0f, cur_price: %.3f" % (bat, cur_price))
        print("Cheapest:")
        pprint(cheapest)
        if bat < MEDIUM_BAT and cur_price < LOW_PRICE:
            print("low bat low price")
            get_charge_schedule(cheapest)
            #force_charge()
        elif bat > LOW_BAT and cur_price > HIGH_PRICE:
           print("expensive hour:")
           print(most_expensive)
           set_soonest_discharge_period(most_expensive)
        else:
            ha_control.set_solax_grid_charge(0)
            ha_control.disable_solax_discharge()
        return

    print("Cheapest:")
    print(cheapest)
    print()
    print("Most expensive:")
    print(most_expensive)
    get_charge_schedule(cheapest)
    set_soonest_discharge_period(most_expensive)

def calc_random_schedule():
    sensor_data = ha_control.get_value("sensor.nordpool_kwh_lt_eur_3_10_021")
    prices = sensor_data['attributes']['raw_today'] + sensor_data['attributes']['raw_tomorrow']
    cheapest, most_expensive, more_expensive = get_cheapest(prices, CHEAPEST_HOURS)
    bat = ha_control.get_battery_level()
    cur_price = ha_control.get_current_price()


    delta = calc_delta(cur_price, cheapest, most_expensive)
    print("Delta: %.3f" % (delta))

    print("Current price: %.3f EUR, Current battery: %.1f" % (cur_price, bat))
    if delta < DELTA:
        bat = ha_control.get_battery_level()
        cur_price = ha_control.get_current_price()
        print("Bat: %.0f, cur_price: %.3f" % (bat, cur_price))
        print("Cheapest:")
        pprint(cheapest)
        if bat < MEDIUM_BAT and cur_price < LOW_PRICE:
            print("low bat low price")
            get_charge_schedule(cheapest)
            #force_charge()
        elif bat > LOW_BAT and cur_price > HIGH_PRICE:
           print("expensive hour:")
           print(most_expensive)
           set_soonest_discharge_period(most_expensive)
        else:
            ha_control.set_solax_grid_charge(0)
            ha_control.disable_solax_discharge()
        return
    res = algo.learn_random(prices)
    print(res)
    if res == 'charge':
        force_charge()
    if res == 'discharge':
        force_discharge()
    if res == 'none':
        #do conditioning
        standby()

def filter_data(data):
    #remove history hours and limit to 24h
    prices = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 30)
    counter = 0
    for item in data:
        start_time = datetime.datetime.fromisoformat(item['start'])
        now_in_start_tz = now.astimezone(start_time.tzinfo)
        if start_time + delta > now_in_start_tz:
            prices.append(item)
            #print(item)
            counter = counter + 1
            if counter > 23:
                break
    return(prices)


def calc_lp():
    sensor_data = ha_control.get_value("sensor.nordpool_kwh_lt_eur_3_10_021")
    prices = sensor_data['attributes']['raw_today'] + sensor_data['attributes']['raw_tomorrow']
    data = filter_data(prices)  

    data = algo.add_placeholders(data)
    data = sun.add_sun_data(data)
    data = usage.add_usage_data(data)

    bat_cap = int(ha_control.get_battery_level())*algo.BAT_CAPACITY / 100
    cur_price = ha_control.get_current_price()

    algo.lp_algo(data, bat_cap, cur_price)

    print(data[0])
    if data[0]['action'] == 'charge':
        force_charge()
    if data[0]['action'] == 'discharge':
        force_discharge()
    if data[0]['action'] == 'none':
        #do conditioning
        standby()


def main():
    #calc_schedule() 
    #calc_random_schedule()
    calc_lp()


if __name__ == "__main__":
    main()

