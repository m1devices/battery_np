Requirements
Homeassistant integrations:
Nordpool https://github.com/custom-components/nordpool/
Solax Power: https://homeassistant-solax-modbus.readthedocs.io/en/latest/
Helpers (numeric values):
bat_acc_price, bat_price


Python modules:
pulp,
requests,
argparse



Run crontab:
0 * * * * /usr/bin/python3 calc.py
* * * * * /usr/bin/python3 /home/jedas/battery/bat_acc.py


Save new data to simulator:
python3 save-sim > data/data_x.dat

Run simulation:
python3 simulator data/data_x.dat


