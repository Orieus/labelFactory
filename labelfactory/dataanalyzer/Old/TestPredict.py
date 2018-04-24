# -*- coding: utf-8 -*-
"""
Created on March, 08 2016
@author: Jesus Cid.
"""

import sys
import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt
# import pickle
import cPickle as pickle
import ipdb


""" A quick peace of code to visualize the histogram of predicts....
"""


# with open('./Data201601/project_2016_01_19_predicts.pkl', 'r') as f:
with open('./Data201507/project_2015_07_predicts.pkl', 'r') as f:
    data = pickle.load(f)

preds_all = [data[w]['pred'] for w in data.keys()]
preds_all = [p for p in preds_all if p is not None]
plt.figure()
plt.hist(preds_all, bins=40, label='All predict values')
plt.title('Distribution of all predict values')
plt.show(block=False)

ipdb.set_trace()
