# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 17:03:22 2024

@author: haines
"""

import os
import glob
import re

import time
import datetime

import numpy as np
import pandas as pd

REAL_RE_STR = '\\s*(-?\\d(\\.\\d+|)[Ee][+\\-]\\d\\d?|-?(\\d+\\.\\d*|\\d*\\.\\d+)|-?\\d+)\\s*'

def load_data(inFile):
    lines=None
    if os.path.exists(inFile):
        f = open(inFile, 'r')
        lines = f.readlines()
        f.close()
        if len(lines)<=0:
            print('Empty file: '+ inFile)
    else:
        print('File does not exist: '+ inFile)
    # pop off the first line of the file 
    lines.pop(0)
    return lines

def get_filenames(indir='./data', interval='15 min'):
    """ read all files for an interval (15 min, hourly, daily, weekly) 
    File name should be 'Export CSV {interval} YYYY-MM-DD.csv' 
    with DD first day of data in file even if multiple days in the file """
    fns = glob.glob(indir+'/Export CSV *'+interval+'*.csv')
    # logs should have filename with timestamp so can sort from youngest to oldest
    fns.sort()
    return fns

def scanf_datetime(ts, fmt='%Y-%m-%dT%H:%M:%S'):
    """Convert string representing date and time to datetime object"""
    # default string format follows convention YYYY-MM-DDThh:mm:ss
    
    try:
        t = time.strptime(ts, fmt)
        # the '*' operator unpacks the tuple, producing the argument list.
        dt = datetime.datetime(*t[0:6])
    except ValueError:
        # value error if something not valid for datetime
        # e.g. month 1...12, something parsed wrong
        dt = None

    return dt

def dt2es(dt):
    """Convert datetime object to epoch seconds (es) as seconds since Jan-01-1970 """
    # microseconds of timedelta object not used
    delta = dt - datetime.datetime(1970,1,1,0,0,0)
    es = delta.days*24*60*60 + delta.seconds
    return es

def es2dt(es):
    """ Convert epoch seconds (es) to datetime object"""
    dt = datetime.datetime(*time.gmtime(es)[0:6])
    return dt

def uniqify(seq):
    seen = {}
    result = []
    for item in seq:
        # in old Python versions:
        # if seen.has_key(item)
        # but in new ones:
        if item in seen: continue
        seen[item] = 1
        result.append(item)
    return result

def parse_data_regexp(lines, data):
    """
    Parse data using Regular Expressions (regexp, or re)
    Example data

    Time,Consumption Meter E (Wh),Consumption Meter P (W),Inv1 Eac (Wh),Inv1 Pac (W)
    10/01/2022 00:00,"333","338.1968","",""
    10/01/2022 01:00,"268","266.7061","",""
    10/01/2022 02:00,"267","258.4614","",""
    10/01/2022 03:00,"259","248.8705","",""
    10/01/2022 04:00,"377","393.7561","",""
    10/01/2022 05:00,"298","297.8074","",""
    10/01/2022 06:00,"270","265.7765","0","0"
    10/01/2022 07:00,"235","217.2353","1","3.6778"
    10/01/2022 08:00,"513","504.4155","169","182.5677"
     
    """
    
    # how many samples 
    N = len(lines)
    data['dt'] = np.array(np.ones((N,), dtype=object)*np.nan)
    # data['time'] = np.array(np.ones((N,), dtype=int)*np.nan)
    # default fill to zeros and not NaN 
    data['consumption'] = np.array(np.zeros((N,), dtype=float))
    data['production'] = np.array(np.zeros((N,), dtype=float))
    
    # sample count
    i = 0
    for line in lines:
        csi = []
        # remove double quotes
        line = line.replace('"','')
        # remove the line-feed
        line = line.replace('\n','')
        # split line
        sw = re.split(',', line)
        if len(sw)<=0:
            print(' ... skipping line %d -- %s' % (i,line))
            continue
        # parse data float and integers
        for s in sw[1:5]:
            m = re.search(REAL_RE_STR, s)
            if m:
                csi.append(float(m.groups()[0]))
            else:
                csi.append(np.nan)
        # parse the date and time
        sample_dt = scanf_datetime(sw[0], fmt='%m/%d/%Y %H:%M')
        
        data['dt'][i] = sample_dt # sample datetime
        # data['time'][i] = dt2es(sample_dt) # sample time in epoch seconds
        if len(csi)==4:
            data['consumption'][i] = csi[0]/1000 # Energy consumption (kWh)
            # data['consumption'][i] = csi[1]/1000 # Power consumption (kW)
            data['production'][i] = csi[2]/1000 # Energy production (kWh)
            # data['production'][i] = csi[3]/1000 # Power production (kW)
            i=i+1
        else:
            print(' ... skipping line %d -- %s ' % (i,line))
            continue
    # where production is NaN set to zero
    data['production'][np.isnan(data['production'])]=0
    return data

def to_series(data):
    """ 
    convert the data as nparray to Pandas Dataframe 
    for easy summation on different time periods of energy (kWh)
    
    """
        
    # Expample how-to create a 2 dimensional numpy array to Pandas dataframe
    # >>> data = np.array([[5.8, 2.8], [6.0, 2.2]])
    # Creating pandas dataframe from numpy array
    # >>> dataset = pd.DataFrame({'Column1': data[:, 0], 'Column2': data[:, 1]})

    # Creating pandas dataframe from numpy array
    # var = 'production'
    # df = pd.DataFrame({'Datetime': data['dt'], var: data[var]})
    df = pd.DataFrame({'Datetime': data['dt'], 
                       'production': data['production'], 
                       'consumption': data['consumption']})
    
    df.dtypes
    
    # explicitly convert the date column to type DATETIME if not already
    # df['Datetime'] = pd.to_datetime(df['Datetime'])
    
    # set index to 
    df = df.set_index('Datetime')
    df.plot()
    
    # test plots summing Wh
    df.resample('D').sum().plot()
    df.resample('W').sum().plot()
    df.resample('M').sum().plot()
    
    return df

    
def get_data(indir='./data', interval='hourly', data={}):   
     fns=get_filenames(indir, interval)
     lines=[]
     for fn in fns:
         lines.extend(load_data(fn))
     # remove any duplicate lines 
     lines=uniqify(lines)
     data=parse_data_regexp(lines, data)
     return data
 

