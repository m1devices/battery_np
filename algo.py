import json
import time
import datetime
from pprint import pprint
import argparse
import sys
import random
import copy
import bat_acc
#sys.path.append('..')
#import calc

CHEAPEST_HOURS=4
MOST_EXPENSIVE_HOURS=4
MORE_EXPENSIVE_HOURS=12
DELTA=0.03
LOOK_AHEAD=12
ESO = 0
#ESO = 11
BAT_CAPACITY=12
MIN_BAT_LEVEL = 1.8
BAT_CHARGE_POWER=4.3
BAT_DISCHARGE_POWER=5.3
EFFICIENCY=0.95
BAT_WEAROUT=0.02

def get_cheapest(prices_all):
    #remove history hours and remove more than LOOK_AHEAD hours
    hours = CHEAPEST_HOURS
    prices = []
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 20)
    look_ahead = datetime.timedelta(hours = 12)
    #for item in prices_all:
    #    start_time = datetime.datetime.fromisoformat(item['start'])
    #    now_in_start_tz = now.astimezone(start_time.tzinfo)
    #    if start_time + delta > now_in_start_tz and start_time - look_ahead < now_in_start_tz:
    #        prices.append(item)
    prices = prices_all

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




def calc_day_average(data):
    sum = 0
    count = 0
    for item in data:
        sum  = sum + item['value']
        count = count + 1
    #return(sum / count, ((sum / count) + ESO) * 70)
    return(sum / count, sum)


def charge_cheapest4(data, cheapest, most_expensive):
    cheapest_avg = calc_day_average(cheapest)[0]
    #discharge at most expensive, increase cheapest by 2x (disabled increase)
    for item in data:
        for st in most_expensive:
            if st['start'] == item['start']:
                item['value'] = cheapest_avg
        for st in cheapest:
            if st['start'] == item['start']:
                #item['value'] = item['value'] * 2
                item['value'] = item['value']

    return(data)
    #print(cheapest_avg)


def calc_potential_charge_hours(current_charge, data, index):
    # total BAT_CAP (12 kwh)
    charge = 0
    discharge = 0

    charge_index = index
    ch_ch = current_charge
    while (ch_ch < BAT_CAPACITY):
        try:
            ch_ch = ch_ch + BAT_CHARGE_POWER + data[charge_index]['sun']
        except:
            # index error
            break
        charge_index = charge_index + 1
        charge = charge + 1

    discharge_index = index
    dis_ch = current_charge
    while (dis_ch > MIN_BAT_LEVEL):
        try:
            dis_ch = dis_ch - data[discharge_index]['usage']
        except:
            # index error
            break
        discharge_index = discharge_index + 1
        discharge = discharge + 1

    return(charge, discharge)


def add_placeholders(data):
    for item in data:
        item['sun'] = 0
        item['usage'] = 0
    return(data)

def learn_random(data_orig):
    min_sum = 10000
    index = 0
    
    avg, sum = calc_day_average(data_orig)
    current_bat_cap = int(bat_acc.get_battery_level_prc())*BAT_CAPACITY / 100
    current_bat_price = float(bat_acc.get_bat_price())
    # action (charge/discharge/none)
    # value (eur/kwh)
    # expected charge from sun (kwh)
    # expected usage at home (kwh)
    for it in range(1,10000):
        #print(it)
        # max hours battery expected to charge
        MAX_BAT = 4
        # current battery charge
        bat_cap = current_bat_cap
        # current price of charge per kwh
        last_charge = current_bat_price
        data = copy.deepcopy(data_orig)
        index = 0
        for item in data:
            pot_charge_h, pot_discharge_h = calc_potential_charge_hours(bat_cap, data, index)
            index = index + 1
            #print(bat_cap, pot_charge_h, pot_discharge_h , item)
            while 1:
                do_nothing = random.randint(1,2)
                if do_nothing == 1:
                    #print("do nothing")
                    item['action'] = 'none'
                    item['value'] = item['value'] * item['usage']
                    break
                charge_chance = random.randint(1,10) * pot_charge_h
                discharge_chance = random.randint(1,10) * pot_discharge_h
                #discharge
                if discharge_chance > charge_chance and item['value'] > avg:
                    bat_cap = bat_cap - item['usage']
                    if bat_cap < 0:
                        bat_cap = 0
                    item['action']= 'discharge'
                    item['value'] = (last_charge * (1/EFFICIENCY)) + BAT_WEAROUT
                    break
                #charge
                if discharge_chance <= charge_chance and item['value'] < avg:
                    bat_cap = bat_cap + BAT_CHARGE_POWER
                    if bat_cap > MAX_BAT:
                        bat_cap = MAX_BAT
                    item['action']= 'charge'
                    last_charge = item['value']
                    break
        avg, sum = calc_day_average(data)
        if sum < min_sum:
            min_sum = sum
            new_data = []
            new_data = data
        index = index + 1
        #debug
        #break
    return(new_data)




import pulp
def lp_algo(data, bat_cap, price_bat_kwh):
    #print(len(data))
    #data must be 24 elements 
    E_max = BAT_CAPACITY  # kWh
    C_max = BAT_CHARGE_POWER   # kWh per hour
    D_max = BAT_DISCHARGE_POWER   # kWh per hour
    eta_c = EFFICIENCY
    eta_d = EFFICIENCY

    # Initialize the problem
    prob = pulp.LpProblem("Battery_Optimization", pulp.LpMaximize)

    print(bat_cap, price_bat_kwh)
    # Assuming 'prices' is already loaded and verified to have 24 elements
    num_hours = len(data)  # Should be 24

    # Decision variables
    C = [pulp.LpVariable(f"C_{t}", 0, C_max) for t in range(num_hours)]      # Charge variables
    D = [pulp.LpVariable(f"D_{t}", 0, D_max) for t in range(num_hours)]      # Discharge variables
    SoC = [pulp.LpVariable(f"SoC_{t}", MIN_BAT_LEVEL, E_max) for t in range(num_hours + 1)]  # State of Charge variables

    # Initial SoC
    prob += SoC[0] == bat_cap  

    # Constraints
    for t in range(num_hours):
        # SoC balance
        prob += SoC[t+1] == SoC[t] + eta_c * C[t] - (1 / eta_d) * D[t] + data[t]['sun'] 

        # SoC limits
        prob += SoC[t+1] >= MIN_BAT_LEVEL
        prob += SoC[t+1] <= E_max


    #initial battery charge price. if battery price is cheaper than day avg, tend to discharge
    sum = 0
    for item in data:
        sum = sum + item['value']
    avg = sum / num_hours
    final_target = 0
    if avg > price_bat_kwh:
        final_target = MIN_BAT_LEVEL
    else:
        final_target = SoC[0]

    #print("Final target: %.1f, initial charge: %.1f" % (final_target, bat_cap))
    # Final SoC equals initial SoC
    #prob += SoC[24] == SoC[0]
    prob += SoC[num_hours] == final_target

    # Objective function
    profit = pulp.lpSum([
        data[t]['value'] * D[t] * eta_d - data[t]['value'] * C[t] / eta_c  - BAT_WEAROUT * C[t]
        for t in range(num_hours)
    ])
    #print(profit)
    prob += profit

    # Solve the problem
    prob.solve()
    # Output the results
    last_charge = price_bat_kwh
    for t in range(num_hours):
        print(f"Hour {t} {data[t]['start']}: Charge {C[t].varValue} kWh, Discharge {D[t].varValue} kWh, SoC {SoC[t+1].varValue} kWh")
        if C[t].varValue > 1:
            data[t]['action'] = 'charge'
            last_charge = data[t]['value']
        elif D[t].varValue > 1:
            data[t]['action'] = 'discharge'
            data[t]['value'] = last_charge
        else:
            data[t]['action'] = 'none'

