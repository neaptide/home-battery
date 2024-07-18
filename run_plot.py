# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 14:30:30 2024

@author: haines
"""

import pandas as pd
from read_data import get_data
from battery_models import maximize_self_consumption, only_solar
from datetime import timedelta

data=get_data()
data['battery_capacity'] = 20.0 # units of kWh
data['battery_reserve'] = 0.20 # reserve factor (0.2 = 20% reserve)
data['battery_c_rate'] = 0.80 # C-rate (for LFP 0.5C to 1.0C) how much of capacity charged in one hour
data['depth_of_discharge'] = 1-data['battery_reserve'] # what fraction of battery can be used
if data['battery_capacity'] > 0.0:
    data['battery_model']='Maximize Self-Consumption'
    data = maximize_self_consumption(data)
else:
    data['battery_model']='Only Solar, NO BATTERY'
    data = only_solar(data)

df = pd.DataFrame({'Datetime': data['dt'], 
                   'production': data['production'], 
                   'consumption': data['consumption'],
                   'self_consumption' : data['self_consumption'],
                   'from_battery' : data['from_battery'],
                   'import' : data['import'],
                   'export' : data['export'],
                   'SOC' : data['SOC']
                   })
df = df.set_index('Datetime')

# use other data frames for using 7d and 30d rolling averages of SOC
df_soc_7d_roll = df['SOC'].rolling(window=7*24, 
                                   center=True, 
                                   min_periods=1).mean()
df_soc_30d_roll  = df['SOC'].rolling(window=30*24, 
                                     center=True, 
                                     min_periods=1).mean()

# list of timesteps for xlimits
# using pd.date_range to generate list depending on frequency
first_date = df.index[0]
last_date = df.index[-1]

oneday = timedelta(days=1)
oneweek = timedelta(weeks=1)
oneyear = timedelta(days=365)
# strange way to get next month by remaining days in the month +1, but works
onemonth = timedelta(days=last_date.days_in_month-last_date.day+1)

days = pd.date_range(start=first_date, end=last_date+oneday, freq='D')
weeks = pd.date_range(start=first_date-oneweek, end=last_date+oneweek, freq='W')
months = pd.date_range(start=first_date, end=last_date+onemonth, freq='MS')
years = pd.date_range(start=first_date-oneyear, end=last_date+oneyear, freq='Y')
all_data = pd.date_range(start=first_date, end=last_date+onemonth, periods=2)

df_hourly = df.resample('h').sum()
df_daily = df.resample('D').sum()
df_weekly = df.resample('W').sum()
df_monthly = df.resample('M').sum()

# use other data frames for using 7d and 30d rolling averages of SOC
df_soc_7d_roll = df_hourly['SOC'].rolling(window=7*24, 
                                          center=True, 
                                          min_periods=1).mean()
df_soc_30d_roll  = df_hourly['SOC'].rolling(window=30*24, 
                                            center=True, 
                                            min_periods=1).mean()

plotparams = {'xstep': days,
              'df' : df_hourly}

# -------------------------------------------------------
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

fig = plt.figure(figsize=(12, 9))
fig.set_layout_engine('tight')

# define layout of axes for plots and GUI using subplot_moasic()
button_mosaic = [["text1","text1","text1","text1"],
                 ["text1","text1","text1","text1"],
                 ["text1","text1","text1","text1"],
                 ["start","prev","next","end"]]
date_mosaic = [["plottype"],
               ["plottype"],
               ['plottype'],
               ["date_slider"]]
mosaic = [["prod", button_mosaic],
          ["cons", "xstep"],
          ["port", date_mosaic],
          ["SOC", 'text2']]
ax = fig.subplot_mosaic(mosaic, 
                        empty_sentinel="BLANK", 
                        width_ratios=[5, 1])
t_left = ax['prod'].set_title('datestr1', loc='left')
t_right = ax['prod'].set_title('datestr2', loc='right')
t_middle = ax['prod'].set_title('datestr1')

# Display input params
# turn off all visual axis
ax['text1'].set_axis_off()
ax['text1'].set_title('Battery Input Params')
text1str = 'Model: {3}\nCapacity: {0} (kWh)\nReserve: {1} (%)\nCharge Rate: {2} (%/hr)'.format(
    data['battery_capacity'], 
    data['battery_reserve']*100, 
    data['battery_c_rate']*100,
    data['battery_model'])

text1 = ax['text1'].text(0,1,text1str)
text1.set_verticalalignment('top')

# Data Summary
ax['text2'].set_axis_off()
ax['text2'].set_title('Energy Sums for \nTime Range Selected')
text2str = ''
text2 = ax['text2'].text(0,1,text2str)
text2.set_verticalalignment('top')

def update_plots(val):
    global plotparms, t_left, t_right, t_middle
    #
    ax['prod'].clear()
    ax['cons'].clear()
    ax['port'].clear()
    ax['SOC'].clear()
   
    label = radio2.value_selected
    print('xstep:',label)
    if label=='EACH DAY':
        plotparams['xstep'] = days
    elif label=='EACH WEEK':
        plotparams['xstep'] = weeks
    elif label=='EACH MONTH':
        plotparams['xstep'] = months
    elif label=='EACH YEAR':
        plotparams['xstep'] = years
    elif label=='ALL':
        plotparams['xstep'] = all_data

    label = radio.value_selected
    print('plottype:',label)
    if label=='hourly':
        plotparams['df'] = df_hourly
    elif label=='daily':
        plotparams['df'] = df_daily
    elif label=='weekly':
        plotparams['df'] = df_weekly
    elif label=='monthly':
        plotparams['df'] = df_monthly
        
    xstep = plotparams['xstep']
    df = plotparams['df']

    ax['prod'].plot(df['production'], 'g.-', label='production')
    ymax = df['production'].max()
    ax['prod'].set_ylim(0, ymax)
    ax['prod'].legend()

    ax['cons'].plot(df['consumption'], 'r.-', label='consumption')
    # ymax = df['consumption'].max()
    ax['cons'].set_ylim(0,ymax)
    ax['cons'].plot(df['self_consumption'], 'c-', label='self-consumption')
    ax['cons'].plot(df['from_battery'], 'y-', label='from battery')
    ax['cons'].legend()
    
    ax['port'].plot(df['import'], 'r.-', label='import')
    # ymax = df['import'].max()
    ax['port'].set_ylim(0, ymax)
    ax['port'].plot(df['export'], 'g.-', label='export')
    ax['port'].legend()

    # use hourly data for SOC
    ax['SOC'].plot(df_hourly['SOC'], 'y.-', label='State of Charge', 
                   linewidth=1,
                   markersize=2)

    label = radio2.value_selected
    if label == 'EACH YEAR' or label == 'ALL':
        # no line for hourly data
        ll = ax['SOC'].get_lines()
        ll = ll[0]
        ll.set_linestyle('')
        # plot rolling average data
        ax['SOC'].plot(df_soc_7d_roll, 'b-', label='7-day rolling mean', 
                        linewidth=1,
                        markersize=2)
        ax['SOC'].plot(df_soc_30d_roll, 'k--', label='30-day rolling mean', 
                        linewidth=2)

    ax['SOC'].legend()
    ax['SOC'].set_ylim(0, 1)


    # add labels back since axes.clear() removes them
    t_left = ax['prod'].set_title('datestr1', loc='left')
    t_right = ax['prod'].set_title('datestr2', loc='right')
    # t_middle = ax['prod'].set_title('datestr1')
    ax['prod'].set_ylabel('Production (kWh)')
    ax['cons'].set_ylabel('Consumption (kWh)')
    ax['port'].set_ylabel('(kWh)')
    ax['SOC'].set_ylabel('SOC (%)')

    sdt.valmax = len(xstep)-1
    sdt.val=0
    change_dt(0)
    
    # draw and allow to catch up
    plt.draw()
    plt.pause(0.01)

def change_dt(val):
    xstep = plotparams['xstep']
    xmin = xstep[sdt.val]
    xmax = xstep[sdt.val+1]
    xminstr = xmin.strftime('%Y-%m-%d')
    xmaxstr = xmax.strftime('%Y-%m-%d')
    t_left.set_text(xminstr)
    t_right.set_text(xmaxstr)
    # t_middle.set_text(xmin.strftime('%Y-%m-%d'))
    ax['prod'].set_xlim(xmin,xmax)
    ax['cons'].set_xlim(xmin,xmax)
    ax['port'].set_xlim(xmin,xmax)
    ax['SOC'].set_xlim(xmin,xmax)
    # update Energy Sums Summary
    # df = plotparams['df']
    df = df_hourly
    textlist = ['Production: {0: 8.2f} (kWh)\n', 
                'Consumption: {1: 8.2f} (kWh)\n',
                'From Battery: {6: 8.2f} (kWh)\n',
                'Self-consumption: {2: 8.2f} (kWh)\n', 
                'Self-consumption: {5:.1f} (%)\n\n',
                'Imported: {3: 8.2f} (kWh)\n',
                'Exported: {4: 8.2f} (kWh)']
    textstr = ''.join(textlist).format(
        df[xminstr:xmaxstr]['production'].sum(),
        df[xminstr:xmaxstr]['consumption'].sum(),
        df[xminstr:xmaxstr]['self_consumption'].sum(),
        df[xminstr:xmaxstr]['import'].sum(), 
        df[xminstr:xmaxstr]['export'].sum(), 
        100*(df[xminstr:xmaxstr]['self_consumption'].sum()/df[xminstr:xmaxstr]['consumption'].sum()),
        df[xminstr:xmaxstr]['from_battery'].sum()
        )
    text2.set_text(textstr)
    
def prev_dt(val):
    dtidx = int(sdt.val)
    if dtidx>0:
        sdt.set_val(dtidx-1)

def next_dt(val):
    dtidx = int(sdt.val)
    if dtidx+1<sdt.valmax:
        sdt.set_val(dtidx+1)

def start_dt(val):
    dtidx = int(sdt.valmin)
    sdt.set_val(dtidx)

def end_dt(val):
    dtidx = int(sdt.valmax)
    sdt.set_val(dtidx-1)
    
# setup GUI
gui_color='lightgoldenrodyellow'
ax['plottype'].set_facecolor(gui_color)
ax['plottype'].set_title('Energy (kWh) Sums')
ax['xstep'].set_facecolor(gui_color)
ax['xstep'].set_title('Time Ranges')

radio = RadioButtons(
    ax['plottype'], ('hourly','daily','weekly','monthly'))
radio.on_clicked(update_plots)

radio2 = RadioButtons(
    ax['xstep'], ('EACH DAY','EACH WEEK','EACH MONTH','EACH YEAR','ALL'))
radio2.on_clicked(update_plots)


# Date slider
sdt = Slider(ax['date_slider'], '', valmin=0, valmax=31, valinit=0, valfmt='%d')
sdt.on_changed(change_dt)

# Date prev button
bdtprev = Button(ax['prev'], '<')
bdtprev.on_clicked(prev_dt)
# Date next button
ax['next'].set_title('Time Range Steps')
bdtnext = Button(ax['next'], '>')
bdtnext.on_clicked(next_dt)
# Date start button
bdtstart = Button(ax['start'], '|<')
bdtstart.on_clicked(start_dt)
# Date end button
bdtend = Button(ax['end'], '>|')
bdtend.on_clicked(end_dt)

   
def init_plot():
    """ initialize plots, finish setting up, and set slider limits
    """
    # global js,jsmap,jsvec,cf1,cf2,cs11,cs12,cs13,cs2
    dtidx = 0

    sdt.valinit = dtidx
    sdt.valmin = 0
    sdt.valmax = len(days)-1
    
    update_plots(0)


init_plot()
plt.draw()