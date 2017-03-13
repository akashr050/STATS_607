# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:14:17 2016

@author: Akash Rastogi
"""

import gzip
import shutil
import zipfile
import os
from urllib import request
import math


def myfloat(x):
    try:
        return float(x)
    except ValueError:
        return float('nan')
        

os.chdir("C://Users//Akash Rastogi//Desktop//UMich study material//Fall 2016//STATS 607//Assignments//Assignment 1")
mappingDict = {'2016q2': 'UCM521951',
               '2016q1': 'UCM509489',
               '2015q3': 'UCM477190',
               '2015q2': 'UCM463272',
               '2015q1': 'UCM458083'}
               
   

for k,v in mappingDict.items():
    webpath = "http://www.fda.gov/downloads/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/%s.zip" % v
    print("processing %s..." % webpath)
    request.urlretrieve(webpath, "tmp.zip")
    try:
        shutil.rmtree(k, ignore_errors=True)
    except:
        pass
    try:
        os.mkdir(k)
    except:
        pass
    zf = zipfile.ZipFile("tmp.zip")
    zf.extractall(k)
    zf.close()
    os.remove("tmp.zip")

key = '2016q2'
dpath = os.path.join(key, 'ascii')
files = os.listdir(dpath)
files = [os.path.join(dpath, x) for x in files if x.endswith('.txt')]
for file in files:
    with open(file, "rt") as f_in, gzip.open(file + ".gz", "wt", encoding="utf8") as f_out:
        shutil.copyfileobj(f_in, f_out) 
files = os.listdir(dpath)
fname = [os.path.join(dpath, x) for x in files if x.endswith('.txt.gz')]
fnameDemo = [x for x in fname if 'DEMO' in x]
fnameDrug = [x for x in fname if 'DRUG' in x]

demoDict = {}
fid = gzip.open(fnameDemo[0], "rt")
for line_num, line in enumerate(fid):
    if line_num == 0:
        continue
    lC = line.rstrip().split("$")
    age     = myfloat(lC[13])
    ageCode = lC[14]
    sex     = lC[16]
    if math.isnan(age) == False and sex not in ['', 'UNK'] and ageCode != '':
        if ageCode == 'DEC':
            age = age * 10
        elif ageCode == 'YR':
            age = age
        elif ageCode == 'MON':
            age = age/12
        elif ageCode == 'WK':
            age = age/52.14
        elif ageCode == 'DY':
            age = age/365
        elif ageCode == 'HR':
            age = age/8760
    else:
        continue
    if age <= 0 or age >= 150:
        continue
    demoDict[lC[0]] = [age, sex]   

drugDict = {}
fid = gzip.open(fnameDrug[0], "rt")
for line_num, line in enumerate(fid):
    if line_num == 0:
        continue
    lC = line.rstrip().split("$")
    if lC[4] != '':
        drugDict[lC[0]] = [lC[4]]   

drugDict = {k:v for k,v in drugDict.items() if k in demoDict.keys()}
demoDict = {k:v for k,v in demoDict.items() if k in drugDict.keys()}

combDict = {}
for k,v in demoDict.items():
    combDict[k] = v + drugDict[k]

drugList = list(set([v[2] for v in combDict.values()]))
t = {v[2]:v[1] for k,v in combDict.items()}



ans = {}
i = 0
for item in drugList:
    print(i)
    i = i +1
    numMales = sum([v[1] == 'M' for v in combDict.values() if v[2] == item])
    numFemales = sum([v[1] == 'F' for v in combDict.values() if v[2] == item])
    MaleAge = sum([v[0] for v in combDict.values() if v[2] == item and v[1] == 'M'])
    FemaleAge = sum([v[0] for v in combDict.values() if v[2] == item and v[1] == 'F'])
    
    if numMales > 0:
        AvgMaleAge = MaleAge/ float(numMales)
    else:
        AvgMaleAge = 0
    
    if numFemales > 0:
        AvgFemaleAge = FemaleAge/ float(numFemales)
    else:
        AvgFemaleAge = 0
    percFemale = numFemales / float(numMales + numFemales)
    ans[item] = [AvgMaleAge, AvgFemaleAge, percFemale]
    