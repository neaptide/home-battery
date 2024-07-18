# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 14:31:47 2024

@author: haines

TODO 
Other models of charging and discharging the battery?
1. solar-only -- no battery
3. storm model or power outage 
    determine when (or how many times) over a 2- or 3-day period SOC 
    would battery become "empty" because little solar production (cloudy)
   OR
   determine how many days of off-grid capacity (no import)

"""

import numpy as np


def maximize_self_consumption(data):
    """ Maximize self-consumption and calculate the SOC, based on 
    battery size, reserve, and charging rate.  

    Parameters
    ----------
    data : dict of 1-d numpy arrays
        Container to hold data of production, consumption.
        Also holds battery parameters to pass to the model.

    Returns
    -------
    data : dict of 1-d numpy arrays
        Data container with added calculated self-consumption, import and 
        export energy.
    
    Start the battery model(s) with equation from
    https://github.com/abdullah2891/solar_energy_calculator
    More specifically from 
    https://github.com/abdullah2891/solar_energy_calculator/blob/master/lib/solar.py
    See the Class Batteries function solve_nonlinear algorithm
    
    TODO 
    3. other models of charging and discharging the battery?
    4. determine when (or how many times) over a 2- or 3-day period SOC 
    would dip below DOD because of no productivity (little solar)
       OR
       determine how many days of off-grid capacity (no import allowed when no production)
    """
    N = len(data['dt'])
    # default fill SOC data with ones (for now) 
    data['SOC'] = np.array(np.ones((N,), dtype=float))
    
    # all units of energy in kWh
    data['self_consumption'] = np.array(np.zeros((N,), dtype=float))
    data['from_battery'] = np.array(np.zeros((N,), dtype=float))
    data['import'] = np.array(np.zeros((N,), dtype=float))
    data['export'] = np.array(np.zeros((N,), dtype=float))

    # used to scale SOC with battery reserve
    xSOC = np.linspace(0,1,100)
    ySOC = np.linspace(data['battery_reserve'],1.0,100)

    # e.g. useable capacity of 12kWh battery with 20% reserve is 
    # 12kW * 0.80 = 9.6 kW
    usable_capacity = data['battery_capacity']*data['depth_of_discharge']
    # initial state of charge at beginning of time series: 100%
    SOC = 1.0
    
    # Integrate SOC for each time point (hour by hour)
    for i in range(N):
        # reset these each hour : kWh
        self_consumption = 0.0
        from_battery = 0.0
        to_battery = 0.0
        imported = 0.0
        exported = 0.0
        
        # available energy in battery: kWh
        # available = SOC * data['battery_capacity']
        available = SOC * usable_capacity
        # PV energy generated during this hour: kWh
        generated = data['production'][i]
        # Energy consumed by loads during this hour: kWh
        consumed = data['consumption'][i]

        # Discharge to meet any load after self-consumption until the 
        # battery is empty. This occurs when load > generation. 
        if consumed >= generated:
            # use from battery if available
            if consumed-generated <= available:
                from_battery = consumed - generated
                imported = 0                
            else:
                # use from battery what is available then import what's needed
                from_battery = available 
                imported = consumed - generated - available
            # 
            self_consumption = from_battery + generated
        
        # Charge from any excess solar generation remaining after offsetting 
        # the load until the battery is full. This occurs when generation > load.
        if generated > consumed:
            # adjust what is needed by charging rate depending on SOC
            # for now just use 0.8
            need = (usable_capacity - available)*data['battery_c_rate']
            # if SOC < 0.8:
            #     need = (usable_capacity - available)*0.5
            # else:
            #     need = (usable_capacity - available)*0.2
            #                
            if generated - consumed > need:
                self_consumption = consumed
                to_battery = need
                exported = generated - consumed - to_battery
            else:
                # 
                to_battery = generated - consumed
            # 
            self_consumption = consumed

            # Adjust how much charged to battery depending on charging rate of LFP
            # lithium batteryes: (LFP and NMC) 0.5C to 1.0C
            # lead-acid: 0.2C to 0.5C
            # https://www.power-sonic.com/blog/how-to-charge-lithium-iron-phosphate-lifepo4-batteries/
            #
            # 
            
        # Base SOC calculation: kWh / kWh -> percentage
        if usable_capacity > 0:
            SOC = (available + to_battery - from_battery) / usable_capacity
        else:
            SOC = 0.0

        # Bound between 0 and 100 % of usable capacity
        if SOC >= 1.0:
            SOC = 1.0
        elif SOC <= 0.0:
            SOC = 0.0

        # scale SOC with reserve
        data['SOC'][i] = np.interp(SOC, xSOC, ySOC)

        data['self_consumption'][i] = self_consumption
        data['from_battery'][i] = from_battery
        data['import'][i] = imported
        data['export'][i] = exported
        #
    return data

def only_solar(data):
    """
    Model for just solar and no battery.  This model is what our grid-tied 
    solar system is without a battery for comparison with other battery models
    mainly, but can also pe used to compare if not using battery. 
    The SOC and from_battery data is zero.

    Parameters
    ----------
    data : dict of 1-d numpy arrays
        Container to hold data of production, consumption.
        Also holds battery parameters to pass to the model.

    Returns
    -------
    data : dict of 1-d numpy arrays
        Data container with added calculated self-consumption, import and 
        export energy.

    """
    data['battery_capacity'] = 0.0 # units of kWh
    data['battery_reserve'] = 0.00 # reserve factor (0.2 = 20% reserve)
    data = maximize_self_consumption(data)

    return data