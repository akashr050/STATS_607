# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 17:14:17 2016
Download the FAERS data, pre-process the files and then calculating
a few desired statistics from the data
@author: Akash Rastogi
"""

import gzip
import shutil
import zipfile
import os
from urllib import request
import math


def myfloat(x):
    """
    It x is a number stored as string then it is converted to float
    otherwise the value of x is replaced by 'nan'
    """
    try:
        return float(x)
    except ValueError:
        return float('nan')

# MappingDict is the mapping of the yyyyQn to the location of its
# file
mappingDict = {'2016q2': 'UCM521951',
               '2016q1': 'UCM509489',
               '2015q3': 'UCM477190',
               '2015q2': 'UCM463272',
               '2015q1': 'UCM458083'}
os.chdir(os.path.join("C://Users//Akash Rastogi//Desktop//",
                      "UMich study material//Fall 2016//STATS 607//",
                      "Assignments//Assignment 1"))


# Here, we iterate through the mapping and download the data. After this,
# create the corresponding yyyyQn folder and unzip the downloaded data
for k, v in mappingDict.items():
    webpath = ("http://www.fda.gov/downloads/Drugs/" +
               "GuidanceComplianceRegulatoryInformation/Surveillance/" +
               "%s.zip" % v)
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
# For the desired year and quarter (denoted by key), gzip the .txt files
dpath = os.path.join(key, 'ascii')
files = os.listdir(dpath)
files = [os.path.join(dpath, x) for x in files if x.endswith('.txt')]
for file in files:
    with open(file, "rt") as f_in, gzip.open(file + ".gz", "wt", encoding="utf8") as f_out:
        shutil.copyfileobj(f_in, f_out)

# Extracting the name of Demographics and drug data files
files = os.listdir(dpath)
fname = [os.path.join(dpath, x) for x in files if x.endswith('.txt.gz')]
fnameDemo = [x for x in fname if 'DEMO' in x]
fnameDrug = [x for x in fname if 'DRUG' in x]

# Creating a dictionary for demographics datafile with primary id as key
demoDict = {}
fid = gzip.open(fnameDemo[0], "rt")
for line_num, line in enumerate(fid):
    if line_num == 0:
        continue
    lC = line.rstrip().split("$")
    age = myfloat(lC[13])
    ageCode = lC[14]
    sex = lC[16]
    if not math.isnan(age) and sex not in ['', 'UNK'] and ageCode != '':
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


# Creating a dictionary for drug datafile with primary id as key
drugDict = {}
fid = gzip.open(fnameDrug[0], "rt")
for line_num, line in enumerate(fid):
    if line_num == 0:
        continue
    lC = line.rstrip().split("$")
    if lC[4] != '':
        drugDict[lC[0]] = [lC[4]]

# Keeping only the entries present in both the files
drugDict = {k: v for k, v in drugDict.items() if k in demoDict.keys()}
demoDict = {k: v for k, v in demoDict.items() if k in drugDict.keys()}

# Combining the two dictionaries created above into one
combDict = {}
for k, v in demoDict.items():
    combDict[k] = v + drugDict[k]

# Creating two dictionaries to store the values for males and females
# separately for each drug
# These lists will have drugName as their key
femaleAge = {}
maleAge = {}

# Iterating through the combDict and generating the separate list for
# males and females
for k, v in combDict.items():
    if v[1] == 'F':
        isFemale = 1
    elif v[1] == 'M':
        isFemale = 0
    age = v[0]
    if v[1] == 'M':
        if v[2] in maleAge.keys():
            maleAge[v[2]].append(age)
        else:
            maleAge[v[2]] = [age]
    if v[1] == 'F':
        if v[2] in femaleAge.keys():
            femaleAge[v[2]].append(age)
        else:
            femaleAge[v[2]] = [age]

# Calculating the average age and number of females and males associated
# with each drugname
femaleAge = {k: [sum(v)/len(v), len(v)] for k, v in femaleAge.items()}
maleAge = {k: [sum(v)/len(v), len(v)] for k, v in maleAge.items()}

# Created a list of all the unique drugName in the combDict
drugList = list(set([v[2] for v in combDict.values()]))
ans = {}

# Generating the required summaries
for item in drugList:
    if item in femaleAge:
        avgFemaleAge = femaleAge[item][0]
        numFemales = femaleAge[item][1]
    else:
        avgFemaleAge = 0
        numFemales = 0
    if item in maleAge:
        avgMaleAge = maleAge[item][0]
        numMales = maleAge[item][1]
    else:
        avgMaleAge = 0
        numMales = 0
    if numFemales != 0:
        femaleProp = numFemales / (numFemales + numMales)
    else:
        femaleProp = 0
    ans[item] = [avgMaleAge, avgFemaleAge, femaleProp]

# Snippet of Ans
# {'1-ALPHA-HYDROXYVITAMIN D3': [0, 74.0, 1.0],
# 'ANTI HYPERTENSIVES': [0, 64.0, 1.0],
# 'Albuterol Inhaler': [0, 20.39699, 1.0],
# 'Asthma Inhalers': [0, 63.0, 1.0],
# 'BENZA': [44.47639, 0, 0.0],
# 'BUPROPION HCI TABLETS EXTENDED-RELEASE': [65.0, 68.0, 0.5],
# 'COENZYME Q-10': [0, 78.69267500000001, 1.0],
# 'DEBRIDAT//TRIMEBUTINE': [0, 68.71697499999999, 1.0],
# 'Dexamethason': [0, 69.27036, 1.0],
# 'GABAPENTIN 100 MG': [52.0, 0, 0.0],
# 'HAVLANE': [0, 59.75599, 1.0],
# 'INSOGEN PLUS': [0, 63.0, 1.0],
# 'MAXIDENE': [0, 67.0, 1.0],
# 'METFOREM': [81.0, 0, 0.0],
# 'MYCOPHENOLATE MOFETIL.': [51.57182344632768,
#  40.07690782407408,
#  0.37894736842105264],
# 'PANTINOL': [0, 82.0, 1.0],
# 'PLASIL - 10 MG COMPRESSE': [0, 88.85421, 1.0],
# 'SEASONIQUE': [0, 43.363185, 1.0],
# 'XYLOCAINE-MPF': [50.0, 84.0, 0.3333333333333333],
# 'teriflunomide': [0, 50.444559999999996, 1.0]}
