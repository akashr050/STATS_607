# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 20:21:20 2016
This program does an analysis of physical activity captured by the sensor
@author: Akash Rastogi
"""

import os
import numpy as np
import pandas as pd
from urllib import request
import zipfile
import matplotlib as mpl

pd.set_option('max_rows', 20)

# Download the file from the requisite location
webpath = 'http://wwwn.cdc.gov/Nchs/Nhanes/2003-2004/PAXRAW_C.ZIP'
request.urlretrieve(webpath, "tmp.zip")

# Unzip the downloaded file and remove the zipped file
zf = zipfile.ZipFile("tmp.zip")
zf.extractall()
zf.close()
os.remove("tmp.zip")

# File handler to read the sas file
df = pd.read_sas("paxraw_c.xpt", chunksize=10000000)

# paxi_min and paxi_max to store the maximum value and minimum value in
# paxinten
paxi_max = []
paxi_min = []
for line_num, data in enumerate(df):
    paxi_max.append([data.PAXINTEN.max()])
    paxi_min.append([data.PAXINTEN.min()])

paxi_max = max(paxi_max)
paxi_min = min(paxi_min)

# File handler to read the sas file
df = pd.read_sas("paxraw_c.xpt", chunksize=10000000)
data_summary = pd.DataFrame()

for line_num, data in enumerate(df):
    # data.PAXSTAT.value_counts()
    # data.PAXCAL.value_counts()
    data = data[(data['PAXCAL'] != 2) & (data['PAXSTAT'] != 2)]
#    # data_1.info()
    data.PAXINTEN = pd.to_numeric(data.loc[:, 'PAXINTEN'], errors='coerce')
    data.PAXINTEN = (data.PAXINTEN - paxi_min) * 100 / paxi_max
    data["PAXI_squared"] = data.PAXINTEN * data.PAXINTEN
    data_2 = data.groupby(["SEQN", "PAXHOUR"]).agg({'PAXINTEN': [np.sum, len],
                                                    'PAXI_squared': np.sum})
    if data_summary.empty:
        data_summary = data_2
    else:
        data_summary = data_summary.add(data_2, fill_value=0)

data_summary.columns = ['PAXI_sum', 'PAXI_len', 'PAXI_squared_sum']
data_summary['variance'] = (data_summary['PAXI_squared_sum'] /
                            data_summary['PAXI_len'] -
                            (data_summary['PAXI_sum'] /
                            data_summary['PAXI_len'])**2)

# Removing rows with zero or near zero variability
data_summary_2 = data_summary[data_summary.variance >= 0.01]
data_summary_2['Mean'] = data_summary_2.PAXI_sum / data_summary_2.PAXI_len
data_summary_2['std'] = data_summary_2.variance ** 0.5

data_summary_2 = data_summary_2.sort_values(['Mean'])
data_summary_2['log_std'] = np.log(data_summary_2['std'])
data_summary_2['log_mean'] = np.log(data_summary_2['Mean'])

# Plotting the log of standard deviation vs. log of mean of PAXINTEN
fig = mpl.pyplot.figure()
mpl.pyplot.scatter(data_summary_2['log_std'], data_summary_2['log_mean'])
mpl.pyplot.xlabel('log(mean of PAXINTEN)')
mpl.pyplot.ylabel('log(std of PAXINTEN)')
