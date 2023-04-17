# Power Monitoring
### Voltage and current monitoring and logging projects

This code repo contains example code using the INA260 breakout board from Adafruit to monitor voltage and current. 
It uses a relay board attached to a Raspberry Pi to control the load in a test circuit. The load consists of a number 
of high wattage resistors attached to the relays and mounted on a large heatsink. A combination of 4 x 5R and a 10R 
resistor wired in a parallel allows the current at 5V to be set in increments of approximately 0.5A up to 4.5A total load. 
These are configured with a resistive load in series with each relay as follows:
```
Relay 1: 10R
Relay 2: 5R
Relay 3: 5R
Relay 4: 2 x 5R in parallel = 2.5R
```
With a 5V supply, the current added for each of the relays is approximately as follows:
```
Relay 1: 0.5A
Relay 2: 1.0A
Relay 3: 1.0A
Relay 4: 2.0A
```
If multiple relays are closed, then the load currents are added together, so all 4 relays closed gives a 4.5A load at 5V. 
This increases with supply voltage, along with an increase in the heat needing to be disapated by the heatsink. 
A large PC CPU heatsink is recommended as these resistors put out a lot of heat, especially if you power multiple of them at once.
The resistors I used are 10W wire wound resistors. So the 5R resistors are able to handle 7V max. The 10R resistor can handle 10V max.
Take care not to overload the resistors or the relays if you are testing higher voltage supplies. Larger wattage versions are availble 
but cost considerably more. Alternatively wiring a pair of 5R resistors in series will make a 10R load capable of handling 20W as the 
power is shared across the resistors. So this would be good up to 14V load for 3S batteries.
For testing 2S batteries I only use the 10R load resistor. If you pair up resistors in parallel for higher current loads, remember 
that this combined current goes through the relay. So a 2A relay is needed for relay 4 when testing a 5V regulator board on my rig.

To monitor temperature of devices being tested (or the load heatsink) a DS20B18 one-wire bus temperature sensor is used. 
See this tutorial on how to wire up and configure a Pi to use one of these: https://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/

## Applications

### Li battery profiling

- li-cell_logger.py - A basic logger program (no temperature monitoring) for a single cell LiPo or Li-Ion cell
- li-battery_2S_logger.pyn- A more sophisticated logger for 2S batteries, including temperature logging and better console output and exception handling.
