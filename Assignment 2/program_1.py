# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 16:39:40 2016

@author: Akash Rastogi
"""

import os
import gzip
from urllib import request
import numpy as np
import re
from scipy import stats


os.chdir("C:/Users/Akash Rastogi/Desktop/UMich study material/Fall 2016/STATS 607/Assignments/Assignment 2")
webpath = "ftp://ftp.ncbi.nlm.nih.gov/geo/datasets/GDS4nnn/GDS4519/soft/GDS4519_full.soft.gz"
print("processing %s..." % webpath)
request.urlretrieve(webpath, "tmp.gz")


def myfloat(x):
    """
    Converts a list of items to their float equivalent
    """
    out = []
    for item in x:
        out.append(float(item))
    return out


def read_soft(fid):
    """
    It reads the fid file handle using the conditions given in the question
    Returns:
    gene_ids: List of the gene ids 
    gene_data: Numpy array of the expression data of genes
    group_id: Numpy array for identification of which column belongs to which 
    categeory of patient(i.e whether uc group or healthly group)
    """
    data_start = 10000
    gene_ids = []
    gene_data = []
    for line_num, line in enumerate(fid):
        line = line.rstrip()
        if(line == '!subset_description = healthy'):
            line = next(fid).rstrip()
            healthy_gp = re.split(',|= ', line)[1:]
        if(line == '!subset_description = ulcerative colitis'):
            line = next(fid).rstrip()
            uc_group = re.split(',|= ', line)[1:]
        if("!dataset_table_begin" in line):
            sample_ids = next(fid).rstrip().split('\t')[2:22]
            data_start = line_num
        if("!dataset_table_end" in line):
            break
        if(line_num > data_start):
            x = line.split('\t')[:22]
            gene_ids.append(x[0:2])
            gene_data.append(myfloat(x[2:]))
    gene_data = np.array(gene_data, dtype=np.float64)

    group_id = []
    for item in sample_ids:
        if item in healthy_gp:
            group_id.append(1)
        elif item in uc_group:
            group_id.append(0)

    group_id = np.array(group_id, dtype=bool)
    return gene_ids, gene_data, group_id


def gen_zstatistic(group_id, gene_data):
    """
    Calculate the zcores for the mean comparison between the two groups
    Input:
    group_id: list of column identifiers for the two groups
    gene_data: gene expression data
    Return:
    zscores for the mean comparison between the two groups for each gene
    """
    healthy_gp_analysis = gene_data[:, group_id]
    uc_gp_analysis = gene_data[:, group_id == False]

    healthy_gp_mean = healthy_gp_analysis.mean(1)
    healthy_gp_var = healthy_gp_analysis.var(1)

    uc_gp_mean = uc_gp_analysis.mean(1)
    uc_gp_var = uc_gp_analysis.var(1)

    uc_gp_mean = uc_gp_analysis.mean(1)
    uc_gp_var = uc_gp_analysis.var(1)

    pooled_std_dev = np.sqrt(healthy_gp_var / 10 + uc_gp_var / 10)
    zscores = (healthy_gp_mean - uc_gp_mean) / pooled_std_dev
    return zscores


def calc_fdr(T):
    """
    Calculates the fdr wrt the normal distribution
    """
    zscores = gen_zstatistic(group_id, gene_data)
    a = sum(zscores > T)/len(zscores)
    b = 1 - stats.norm.cdf(T)
    return a, b, b/a

# Part 1
fid = gzip.open("tmp.gz", "rt")
gene_ids, gene_data, group_id = read_soft(fid)

# Part 2
zscores_2 = gen_zstatistic(group_id, gene_data)

np.percentile(zscores_2, 90)  # 1.7261010448515066
np.percentile(zscores_2, 95)  # 2.2875518103207804
np.percentile(zscores_2, 99)  # 3.3138852272274777

stats.norm.ppf(0.90)  # 1.2815515655446004
stats.norm.ppf(0.95)  # 1.6448536269514722
stats.norm.ppf(0.99)  # 2.3263478740408408

dof = len(zscores_2) - 1
stats.t.ppf(0.90, df=dof)  # 1.2815670499651466
stats.t.ppf(0.95, df=dof)  # 1.6448814975137822
stats.t.ppf(0.99, df=dof)  # 2.3264160815775545

# part 3
perm_avg = []
for i in range(20):
    new_gi = np.random.permutation(group_id)
    new_zscores = gen_zstatistic(new_gi, gene_data)
    perm_avg.append(new_zscores.mean())

# part 4

calc_fdr(2)  # (0.072592592592592597, 0.022750131948179209, 0.3133946747963462)
calc_fdr(2.5)  # (0.036854138088705989, 0.0062096653257761592, 0.1684930281324)
calc_fdr(3)  # (0.017064471879286693, 0.0013498980316301035, 0.079105760856780)
calc_fdr(3.5)  # (0.0071879286694101511, 0.00023262907903554009, 0.03236385469)
