# home-battery
Model battery state-of-charge (SOC) and self-consumption based on input battery parameters, hourly consumption (kWh) and solar production (kWh) data. 

## Introduction 
In mid-2022, we installed a residential (6.21 kW) solar system without a battery. We also added a consumption meter at that time.  The hourly data on ***our*** energy use is very enlightening. With net metering and the size of our system, we generate enough energy during the day to export more during the solar day than we use throughout the nighttime.  We can feel good about putting clean electricity on the grid for others to use during the day and benefit finanacially from reduced energy bills, but don't know what the source of energy is used at night when pulling from the grid.  To investigate whether a battery might be useful to reduce our nighttime use of grid energy, I wrote this code to model and visual the effect of having a battery in our system.  This battery model code allows us to analyze how different sized batteries would perform with our personal data and impact of different battery parameters such as desired reserve, roundtrip inefficiency, and temperature inefficiency.  If you are interested in anaylyzing your own data (production and consumption), this code can be modified to parse your data.  The code can also be modified to incorporate modeled production and consumption.  

*** give credit to @abdullah2891 for inspiration and battery model code.  Also, see his code to see how to model system production for given location and weather history ***

## Inputs

### Battery
The battery parameters that can be changed are:
1. battery capacity (kWh): Theoretical (or as-advertised) capacity of the battery and in practice never fully realized.
2. percent of reserve (%):  What percent of battery capacity to hold in reserve.  This value is 100% - depth of discharge. For example, lead acid batteries should only be discharged 50% or a reserve of 50%, while lithium-ion batteries can be almost fully discharged to 100%, but good practice to reserve 10-20%. This paramerter can be used to also represent or combine additional battery inefficiencies, like round trip and temperature factors. For example in colder temperatures, the battery will not perform as efficiently reducing the available capacity.  For AC-to-DC battery systems, the round trip inefficiency is 10%.  That is because the energy from the panels is converted to AC then the battery converts it back to DC to store it and then inverts it a third time to AC for use in the home.  
3. charging rate (%/hour):  The percentage amount the battery can recharge in a given hour. 

The typical battery size for house battery range from 1-40 kWh.  This capacity is dimished by cold temperature and battery efficiency.  One does not get 100% of all the capacity.  Also another factor is how much of that usable capacity to hold in reserve.  LFP and NMC Lithium-ion batteries in theory can be discharged fully while it is not recommmended. So holding some in reserve (10-20%) is good practice and allows your battery system to have energy to power inverters (AC to DC) as the sun begins to charge the battery.

### Consumption and Production Data
In this routine, we use data that was collected and available by the SolarEdge Controller

## Models

## Interactive Graph 

This code generates an interactive graph to help analyze the results over different time periods (day, week, month, year, all) and on different frequencies (hourly, daily, weekly, monthly). It is a graph of energy production, consumption, imported/exported and state-of-charge (SOC) of the battery with time period and detail chosen.  

The top subplot is the solar production (green).  The 2nd subplot shows overall consumption (red), self-consumption (light-blue) (both from solar and/or battery) and what energy comes from the battery (yellow-brown).  The 3rd subplot is of export (green) which is excess solar and import (red).  The 4th subplot depicts the state-of-charge (SOC) between 0 and 100%. 

![2023_Figure_20kWh_battery](https://github.com/user-attachments/assets/60982bca-107d-458b-9adb-b25f41e1157d)
