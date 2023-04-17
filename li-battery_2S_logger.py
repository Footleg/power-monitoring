#!/usr/bin/env python3
""" Li battery discharge rate logger
    --------------------------------
    This project discharges a Li battery through a resistive load and logs the
    voltage and current at a set interval to a CSV file. You can set the battery
    voltage which the test ends at. Start with the battery fully charged, and run
    the test until it stops when the end voltage is reached. 
    Take care not to over-discharge your battery  as this can damage it. Typically 
    when the voltage drops below 3.0V there is very little power left in the cell. 
    Most built in protection cuts off the cell at 2.7V to prevent damage. This version
    is set up for 2S batteries, so the cut off voltage is set to 5.8V for a pair of cells
    in series.
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
    - Adafruit INA260 i2c voltage and current monitoring breakout.
    - Relay HAT (any generic relay board using GPIO pins to switch relays).
    - Resistors attached to a heatsink as a load. See main repo readme for details.
    - DS20B18 one wire bus temperature sensor (data line on GPIO 4) .

    For more details, see the full code repo on github:
    https://github.com/Footleg/power-monitoring
    
    License

    (c) Paul 'Footleg' Fretwell 2023

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
import glob

from gpiozero import LED
from time import sleep,monotonic_ns

# Set parameters for this run
endVoltage = 5.8 # Battery voltage to end the run at
logInterval = 15 # Seconds between readings (this results in readings every 22s due to time taken for readings)
readingsToAverage = 8 # Number of readings to take a average of for each log line

logging.basicConfig(format='%(asctime)s, %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.INFO,filename="BattLog.txt")

relay1 = LED(6)
relay2 = LED(13)
relay3 = LED(19)
relay4 = LED(26)

i2c = busio.I2C(board.SCL, board.SDA)
ina260 = adafruit_ina260.INA260(i2c)

averageCurrent = 0 # This is added to each reading to calculate the average at the end
totalReadings = 0  # Count of the number of readings taken. Used to calculate average.
temperature = 0

# Set up DS20B18 temperature sensor reading on 1-wire bus
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    try:
        # lines[0].strip()[-3:] threw a list index out of range error
        while lines[0].strip()[-3:] != 'YES':
            sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
    except:
        print(lines)
        return -99

try:
    volts = ina260.voltage
    msg = f"Battery profiling started: Starting at {volts}V, Ending at {endVoltage}V"
    logging.info(msg)
    print(msg)
    temperature = read_temp()
    print(f"Starting temperature: {temperature} degC")
    relay1.on() # Apply a 10 Ohm load. This starts the discharge of the battery at around 800 mA

    readCount = 0
    Vave = 0
    Aave = 0
    Tave = 0
    startTime = monotonic_ns()
    
    while volts > endVoltage:
        sleep(logInterval/readingsToAverage)
        Vdat = ina260.voltage
        Adat = ina260.current
        Tdat = read_temp()
        Vave = Vave + Vdat
        Aave = Aave + Adat
        Tave = Tave + Tdat
        readCount = readCount + 1
        # Log reading every set number of reads
        if readCount >= readingsToAverage:
            volts = Vave / readingsToAverage
            current = Aave / readingsToAverage
            temperature = Tave / readingsToAverage
            readCount = 0
            Vave = 0
            Aave = 0
            Tave = 0
            logging.info(f"{volts},{current},{temperature}")
            print(f"Time: {(monotonic_ns() - startTime) / 1000000000:.0f}s, {volts:.2f} V, {current:.2f} mA, {temperature:.1f} degC")
            averageCurrent += current
            totalReadings += 1

    # End of run. Write final stats to log
    if totalReadings > 0:
        averageCurrent = averageCurrent / totalReadings
    totalSeconds = (monotonic_ns() - startTime) / 1000000000 
    totalHours = totalSeconds / 3600 #logInterval * totalReadings / 3600
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