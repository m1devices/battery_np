

from datetime import datetime


monthly_usage = {
    1: 2700,
    2: 1800,
    3: 1500,
    4: 980,
    5: 540,
    6: 560,
    7: 530,
    8: 500,
    9: 500,
    10: 1000,
    11: 1600,
    12: 2000
}

def get_typical_hourly_usage():
    current_datetime = datetime.now()
    current_month = current_datetime.month
    monthly = monthly_usage[current_month]
    hourly = monthly / 30 / 24
    #print(f"usage: {hourly}")
    return(hourly)

def add_usage_data(data):
    for item in data:
        item['usage'] = get_typical_hourly_usage()
    return(data)

def main():
   res = get_typical_hourly_usage()
   #res = get_usage()
   print(res)

if __name__ == "__main__":
    main()



