"""
Download data files from the National Bridge Inventory and extract
them into directories for each year. Then gzip the individual files.
"""

import os
import math
import zipfile
import gzip
import shutil
from urllib import request

#functions
def myfloat(x):
    try:
        return float(x)
    except ValueError:
        return float('nan')

def inputVariables(x):
    structure_number      = x[3:18]
    state                 = myfloat(x[0:3])
    year_built            = myfloat(x[156:160])
    year_reconstructed    = myfloat(x[361:365])
    structure_length      = myfloat(x[222:228])
    average_daily_traffic = myfloat(x[164:170])        
    lst = [structure_number, state, year_built, year_reconstructed, structure_length,
           average_daily_traffic]
    return lst
    
#Scrapping the data from web
years = [2000, 2005, 2010]
os.chdir("C:/Users/Akash Rastogi/Desktop/UMich study material/Fall 2016/STATS 607/Assignments")


for year in years:
    webpath = "https://www.fhwa.dot.gov/bridge/nbi/%d.zip" % year
    print("processing %s..." % webpath)
    request.urlretrieve(webpath, "tmp.zip")
    try:
        shutil.rmtree(str(year), ignore_errors=True)
    except:
        pass
    try:
        os.mkdir(str(year))
    except:
        pass
    zf = zipfile.ZipFile("tmp.zip")
    zf.extractall(str(year))

    files = os.listdir(str(year))
    for file in files:
        fname = os.path.join(str(year), file)
        with open(fname, "rt", encoding="latin1") as f_in, gzip.open(fname + ".gz", "wt", encoding="utf8") as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(fname)

os.getcwd()

# File maniputation
dpath = "C:/Users/Akash Rastogi/Desktop/UMich study material/Fall 2016/STATS 607/Assignments"
folders = os.listdir(dpath)
folders = [x for x in folders if x.startswith('20')]


#Extracting all the values for year = 2000 (i.e the 0th element in folders list)
yearDict= {}
for folder in folders:
    folderName = os.path.join(dpath, folder)
    fnl_list = []
    fname = [os.path.join(folderName, f) for f in os.listdir(folderName)]
    fname = [x for x in fname if x.endswith("txt.gz")]
    for file in fname:
        fid = gzip.open(file, "rt")
        for line_num, line in enumerate(fid):
            if (myfloat(line[18]) == 1 and myfloat(line[222:228]) >= 6.1 and 
                line[373] == 'Y' and 
                myfloat(line[199]) in [1,4,5,6,7,8]):
                    fnl_list.append(inputVariables(line))
    yearDict[folder] = fnl_list

# Note: Question 1 to 3 is done for year 2000 only

lYear2000 = yearDict['2000']
#Question 1 
#Which state has the most bridges?
stateDict = {}
for item in lYear2000:
    if not math.isnan(item[1]):
        str_item = str(int(item[1]))
        if(str_item in stateDict.keys()):
            stateDict[str_item] += 1
        else:
            stateDict[str_item] = 1

maxState = [k for (k, v) in stateDict.items() if v == max(stateDict.values())]

print(maxState) #['486'] i.e Texas

#Determine the average length of bridges in each state, and determine which 
#states have the shortest and longest averages.
lenOfBridgeDict = {}
for item in lYear2000:
    if math.isnan(item[4]) == False and math.isnan(item[1]) == False:
        str_item = str(int(item[1]))
        if(str_item in lenOfBridgeDict.keys()):
            lenOfBridgeDict[str_item] += item[4]
        else:
            lenOfBridgeDict[str_item] = item[4]

avgLenBridgeDict = {}    
for key in lenOfBridgeDict.keys():
    avgLenBridgeDict[key] = lenOfBridgeDict[key] / stateDict[key]
    
shortestAverageLength = [k for (k, v) in avgLenBridgeDict.items() if 
                         v == min(avgLenBridgeDict.values())]
# 317 Nebraska

longestAverageLength = [k for (k, v) in avgLenBridgeDict.items() if 
                         v == max(avgLenBridgeDict.values())]
#113 District of Columbia


#For bridges that were rebuilt, determine the average duration between the 
#original construction and the reconstruction.

avgDuration = [] 
for item in lYear2000:
    if math.isnan(item[2]) == False and math.isnan(item[3]) == False and item[3] != 0.0:
        Duration = item[3] - item[2]
        if(Duration >= 0):
            avgDuration.append(Duration)

sum(avgDuration)/len(avgDuration) #37.250

# Comparing the average daily traffic values from 2000 to 2010, what proportion 
# of bridges saw increased traffic? What was the average percentage change in 
# average daily traffic over all bridges?
yr2000dT = {i[0]:i[5] for i in yearDict['2000'] if math.isnan(i[5]) == False}
yr2010dT = {i[0]:i[5] for i in yearDict['2010'] if i[0] in yr2000dT.keys() and math.isnan(i[5]) == False}
yr2000dT = {k: v for (k,v) in yr2000dT.items() if k in yr2010dT.keys()}
dailyTraffic = []
for k,v in yr2000dT.items():
    dailyTraffic.append([yr2010dT[k], v])

count = 0
#What proportion of bridges saw increased traffic
for item in dailyTraffic:
    if(item[1] - item[0]):
        count+= 1

# Proportion of bridges showing an increase in traffic is:
count/len(dailyTraffic) #0.6908

#What was the average percentage change in average daily traffic over all bridges
(sum(yr2010dT.values()) - sum(yr2000dT.values()))/ sum(yr2000dT.values()) #0.1359

