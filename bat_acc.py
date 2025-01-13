import ha_control


def get_counter():
    res = ha_control.get_value("input_number.bat_acc_price")['state']
    return(res)

def set_counter(value):
    ha_control.set_ha_input_number("input_number.bat_acc_price", value)

def get_battery_state():
    res = int(ha_control.get_value("sensor.solax_battery_power_charge")['state'])
    return(res)

def get_battery_level_prc():
    res = int(ha_control.get_value("sensor.solax_battery_capacity")['state'])
    return(res)

def get_current_price():
    res = float(ha_control.get_value("sensor.nordpool_kwh_lt_eur_3_10_021")['state'])
    return(res)

def get_bat_price():
    res = ha_control.get_value("input_number.bat_price")['state']
    return(res)

def set_bat_price(value):
    ha_control.set_ha_input_number("input_number.bat_price", value)



def main():
    current = float(get_counter());
    bat_charge = -get_battery_state()
    price = get_current_price()
    bat_kwh_price = float(get_bat_price())
    print("total: %.4f, price %.3f, charge: %.0f" % (current, price, bat_charge))
    new_total = current + ((bat_charge / 1000 / 60) * price)
    set_counter(new_total)


    if bat_charge >= 0:
        return
    bat_charge = - bat_charge
    #usable battery capacity
    BAT_SIZE_IN_KWH = 12
    #charge_percent_per_last_minute
    charge_percent = (bat_charge / 1000 / 60) / BAT_SIZE_IN_KWH
    print("Charge percent: %.3f" % (charge_percent))
    bat_kwh_price = bat_kwh_price + (charge_percent * price) - (charge_percent * bat_kwh_price)
    print("current bat charge price: %.4f" % (bat_kwh_price))
    set_bat_price(bat_kwh_price)

if __name__ == "__main__":
    main()

