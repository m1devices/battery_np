Run crontab every hour:
0 * * * * /usr/bin/python3 calc.py


Save new data to simulator:
python3 save-sim > data/data_x.dat

Run simulation:
python3 simulator data/data_x.dat
