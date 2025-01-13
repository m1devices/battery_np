import json
import datetime
from pprint import pprint
import argparse
import sys
import random
import copy
#sys.path.append('..')
import algo
import sun
import usage

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Load and display JSON data from a specified file."
    )
    parser.add_argument(
        'filename',
        type=str,
        help="Path to the JSON file to be loaded."
    )
    return parser.parse_args()

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data_txt = f.read()
            data = data_txt.replace('\'', '\"')
            jdata = json.loads(data)
            return(jdata)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return

def display_data(data):
    max = 0
    index = 0

    for item in data:
        if item['value'] > max:
            max = item['value']

    for row in range(0,10):
        for item in data:
            val = item['value']
            display = (val / max ) * 10
            if display >= (9 - index) and display <= (10 - index):
                if val >= 10:
                    sys.stdout.write(" %d " % (val))
                else:
                    sys.stdout.write(" %.1f" % (val))
            if display < 9 - index:
                sys.stdout.write("    ")
            if display > (10 - index):
                try:
                    #print(item['action'])
                    if item['action'] == 'charge':
                        sys.stdout.write("^^^^")
                    elif item['action'] == 'discharge':
                        sys.stdout.write("||||")
                    else:
                        sys.stdout.write("oooo")
                except:
                    sys.stdout.write("oooo")



        index = index + 1
        print()

def limit_data(data):
    new_data = []
    index = 0
    for item in data:
        #item['value'] = item['value'] * 100
        new_data.append(item)
        index = index + 1
        if index > 23:
            break
    return(new_data)


def main():
    args = parse_arguments()
    file_path = args.filename
    data = load_data(file_path)
    data = limit_data(data)
    data = algo.add_placeholders(data)
    data = sun.add_sun_data(data)
    data = usage.add_usage_data(data)

    display_data(data)
    avg, sum = algo.calc_day_average(data)
    base = sum
    print("Day average: %.3f, sum %.1f" % (avg, sum))
    cheapest, most_expensive, more_expensive = algo.get_cheapest(data)
    
    cheapest4_data = copy.deepcopy(data)
    cheapest4_data = algo.charge_cheapest4( cheapest4_data, cheapest, most_expensive)
    display_data( cheapest4_data)
    avg, sum = algo.calc_day_average( cheapest4_data)
    print("Day average: %.3f, sum %.1f, comp: %.1f %%, %.2f EUR" % (avg, sum, sum/base*100, base - sum))  

    #learn_random_data = copy.deepcopy(data)
    #new_learn_random_data = algo.learn_random(learn_random_data)
    #new_learn_random_data = algo.learn_tree(learn_random_data)

    #display_data(new_learn_random_data)
    #avg, sum = algo.calc_day_average(new_learn_random_data)
    #print("Day average: %.3f, sum %.1f, comp: %.1f %%, %.2f EUR" % (avg, sum, sum/base*100, base - sum))
    lp_data = copy.deepcopy(data)
    algo.lp_algo(lp_data, bat_cap=7, price_bat_kwh=0.08)
    display_data(lp_data)
    avg, sum = algo.calc_day_average(lp_data)
    print("Day average: %.3f, sum %.1f, comp: %.1f %%, %.2f EUR" % (avg, sum, sum/base*100, base - sum))

main()
