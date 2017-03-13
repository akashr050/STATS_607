# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 17:46:55 2016

@author: Akash Rastogi
"""

import os
import gzip
import re

os.chdir("C:/Users/Akash Rastogi/Desktop/UMich study material/Fall 2016/STATS 607/Assignments/Assignment 2")

# Timestamp_list contains all the timestamp
# ip1_list contains all the ips occuring at first position
# ip2_list contains all the ips occuring at second position

timestamp_list = []
ip1_list = []
ip2_list = []
fid = gzip.open("maccdc2012_00016.txt.gz", "rt")
# 4107662 lines
for line_num, line in enumerate(fid):
    line_element = line.rsplit()[:5]
    if len(line_element) == 5 and line_element[1] == "IP":
        a = re.split(":", line_element[0])
        timestamp_list.append(":".join(a[0:2]))
        ip1_list.append(line_element[2])
        ip2_list.append(line_element[4][:-1])


# comb_dict is the dictionary of all ip address occuring for the particular
# timestamp
comb_dict = {}
for i in set(timestamp_list):
    l1 = [item for j, item in enumerate(ip1_list) if timestamp_list[j] == i]
    l2 = [item for j, item in enumerate(ip2_list) if timestamp_list[j] == i]
    comb_dict[i] = l1 + l2


ans_1 = {k: len(set(v)) for k, v in comb_dict.items()}
ans_1_sorted = sorted(ans_1.values())
ans_1_sorted[int(155 * .10)]  # 4233
ans_1_sorted[int(155 * .25)]  # 4402
ans_1_sorted[int(155 * .75)]  # 4843
ans_1_sorted[int(155 * .90)]  # 39980

ip_list = ip1_list + ip2_list
ip_dict = {}
for item in ip_list:
    if(item in ip_dict.keys()):
        ip_dict[item] += 1/155
    else:
        ip_dict[item] = 1/155

distinct_ip = list(ip_dict.values())
sum(distinct_ip) / (len(distinct_ip))  # 0.05040
distinct_ip = sorted(distinct_ip)
distinct_ip[int(len(distinct_ip) * .10)]  # 0.00645
distinct_ip[int(len(distinct_ip) * .25)]  # 0.01290
distinct_ip[int(len(distinct_ip) * .75)]  # 0.01290
distinct_ip[int(len(distinct_ip) * .90)]  # 0.08387
