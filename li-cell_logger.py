#!/usr/bin/env python3
""" Li battery discharge rate logger
    --------------------------------
    This project discharges a Li battery through a resistive load and logs the
    voltage and current at a set interval to a CSV file. You can set the battery
    voltage which the test ends at. Start with the battery fully charged, and run
    the test until it stops when the end voltage is reached. 
    Take care not to over-discharge your battery  as this can damage it. Typically 
    when the voltage drops below 3.0V there is very little power left in the cell. 
    Most built in protection cuts off the cell at 2.7V to prevent damage. 
    If you run your batteries down this low then don't leave them in that state 
    for too long. Put them on charge to bring the voltage up before storing them.

    Once you have a log file from a full run, you can plot the results in a spreadsheet
    to see the discharge graph. You can calculate the approximate capacity by taking 
    the average current measured across all the time intervals, and multipling this 
    by the total time of the test in hours.

    Dependencies
    ------------
    This library requires the following Adafruit libraries to be installed:
    - adafruit_blinka
    - adafruit-circuitpython-ina260

    These can be installed/upgraded to the latest using the following command:
    pip3 install --upgrade adafruit-circuitpython-ina260

    These are installed through apt (they may already be installed in the default Raspberry Pi OS)
    - GPIOzero
    - logging

    The program requires the following hardware attached to a Raspberry Pi computer:
    - Adafruit INA260 i2c voltage and current monitoring breakout
    - Relay HAT (any generic relay board using GPIO pins to switch relays).

    For more details, see the full code repo on github:
    https://github.com/Footleg/power-monitoring
    
    License

    (c) Paul 'Footleg' Fretwell 2022

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    It is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
     
    You should have received a copy of the GNU General Public License
    along with this software.  If not, see <http://www.gnu.org/licenses/>.
"""

import board
import busio
import adafruit_ina260
import logging

from gpiozero import LED
from time import sleep

#Set parameters for this run
endVoltage = 2.7 # Battery voltage to end the run at
logInterval = 15 # Seconds between readings

logging.basicConfig(format='%(asctime)s, %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO,filename="BattLog.txt")

relay1 = LED(6)
relay2 = LED(13)
relay3 = LED(19)
relay4 = LED(26)

i2c = busio.I2C(board.SCL, board.SDA)
ina260 = adafruit_ina260.INA260(i2c)

averageCurrent = 0 # This is added to each reading to calculate the average at the end
totalReadings = 0  # Count of the number of readings taken. Used to calculate average.

try:
    volts = ina260.voltage
    msg = f"Battery profiling started: Starting at {volts}V, Ending at {endVoltage}V"
    logging.info(msg)
    print(msg)
    relay2.on() # Apply a 5 Ohm load. This starts the discharge of the battery at around 800 mA

    while volts > endVoltage:
        sleep(logInterval)
        volts = ina260.voltage
        current = ina260.current
        logging.info(f"{volts},{current}")
        averageCurrent += current
        totalReadings += 1

    # End of run. Write final stats to log
    if totalReadings > 0:
        averageCurrent = averageCurrent / totalReadings
    totalHours = logInterval * totalReadings / 3600
    capacity = averageCurrent * totalHours

    logging.info(f"\"Total time\",\"{totalHours:.2f} hours\"")
    logging.info(f"\"Capacity\",\"{capacity:.2f} mAH\"")

    print(f"Run ended. Average current: {averageCurrent:.2f}; Total time: {totalHours:.2f} hours; Calculated capacity: {capacity:.2f} mAH")
    
finally:
    #All power off
    relay1.off()
    relay2.off()
    relay3.off()
    relay4.off()