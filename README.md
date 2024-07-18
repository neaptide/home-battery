# home-battery
Model battery state-of-charge (SOC) and self-consumption based on input battery parameters, hourly consumption (kWh) and solar production (kWh) data. 

## Introduction 
In mid-2022, we installed a residential (6.21 kW) solar system without a battery. We also added a consumption meter at that time.  The hourly data on ***our*** energy use is very enlightening. 

While we use the energy directly from the panels when the sun is shining, we still use a lot of energy after sundown and before sunup.  For us, over the past two years, of the energy we used (consumed), only 30% was from the sun (self-consumption).  Sometimes it is less, sometimes more, but on average 30%. We try to run our dryer and bake with the electric oven during the day, but it is not practicable all the time.  With net metering and the size of our system, we generate enough energy during the day to export more during the solar day than we use throughout the nighttime.  We can feel good about putting clean electricity on the grid for others to use during the day, but don't know what the source of energy is used at night when pulling from the grid.  So the quetions we wanted answers to if we had a battery are: 

1. What size of battery optimizes self-consumption for a given solar system size?
2.  How would the battery hold up (charge and discharge) on an daily basis, throughout the year?
3.  
4.  How many days of self-sufficiency as a backup battery would we have with a grid power outage and little solar gain? 

## Inputs

### Battery
The battery parameters that can be changed are:
1. battery capacity (kWh): Theoretical (or as-advertised) capacity of the battery and in practice never fully realized.
2. percent of reserve (%):  What percent of battery capacity to prevent from fully discharging or 100% - Depth of discharge. 
3. charging rate (%/hour):  The percentage amount the battery can recharge in a given hour. 

The typical battery size for house battery range from 1-40 kWh.  This capacity is dimished by cold temperature and battery efficiency.  One does not get 100% of all the capacity.  Also another factor is how much of that usable capacity to hold in reserve.  LFP and NMC Lithium-ion batteries in theory can be discharged fully while it is not recommmended. So holding some in reserve (10-20%) is good practice and allows your battery system to have energy to power inverters (AC to DC) as the sun begins to charge the battery.

### Consumption and Production Data
In this routine, we use data that was collected and available by the SolarEdge Controller

## Models

## Interactive Graph 

This code generates an interactive graph to help analyze the results over different time periods (day, week, month, year, all) and on different frequencies (hourly, daily, weekly, monthly). It is a graph of energy production, consumption, imported/exported and state-of-charge (SOC) of the battery with time period and detail chosen.  

The top subplot is the solar production (green).  The 2nd subplot shows overall consumption (red), self-consumption (light-blue) (both from solar and/or battery) and what energy comes from the battery (yellow-brown).  The 3rd subplot is of export (green) which is excess solar and import (red).  The 4th subplot depicts the state-of-charge (SOC) between 0 and 100%. 

![2023_Figure_20kWh_battery](https://github.com/user-attachments/assets/60982bca-107d-458b-9adb-b25f41e1157d)
