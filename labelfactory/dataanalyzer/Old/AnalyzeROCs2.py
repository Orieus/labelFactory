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
import os.path
import ipdb

""" Load a set of predictions, labels and labeling metadata and computes
    different ROCs to estiamte different thresholds.

    This is a version of AnalyzeROCs.py that takes all data from dataset.pkl. 
    This is not desirable, because the predict values may have been compute 
    using all labels and, thus, there is some training bias in the error
    estimates.
"""


def compute_ROC(y_sorted):

    nFN = np.cumsum([max(ys, 0) for ys in y_sorted])
    nTN = np.cumsum([max(-ys, 0) for ys in y_sorted])

    y_sorted0 = np.append(y_sorted, 0)
    nFP = np.cumsum([max(-ys, 0) for ys in y_sorted0[::-1]])[:0:-1]
    nTP = np.cumsum([max(ys, 0) for ys in y_sorted0[::-1]])[:0:-1]

    TPR = nTP.astype(float)/(nTP + nFN)
    FPR = nFP.astype(float)/(nTN + nFP)

    return nFP, nFN, nTN, nTP, TPR, FPR


def compute_tpfn(p, NFP, NFN):

    """ Given two arrays with the cumulative sum of false positive (NFP) and
        false negatives (NFN), compute the threshold
    """

    DIFF = np.abs(NFP - NFN)
    pos = np.argmin(DIFF)
    th = p[pos]

    return th, pos


def plotROCs(p, y, w, rs0al1, relabels):

    """ Plot three possible decision thresholds for a classifier with
        predictions p for samples with labels y, depending on the use of
        labeling information.

        ARGS:
           :p      :Preditions in the range [-1, 1]
           :y      :Labels in {-1, 1}
           :w      :Non-negative weights.
           :rs0al1 :Type of labelling indicator.
                     = 0 for samples taken with random sampling
                     = 1 for samples taken with active learning
                     None for samples with unknown labeling method.
    """

    # Sort all input arrays according to preds.
    orden = np.argsort(np.array(p))
    p_sorted = [p[i] for i in orden]
    y_sorted = [y[i] for i in orden]
    rs0al1_sorted = [rs0al1[i] for i in orden]
    w_sorted = [w[i] for i in orden]

    # Unweighted complete averaging.
    NFP, NFN, NTN, NTP, TPR, FPR = compute_ROC(y_sorted)
    umbral_tpfn, pos = compute_tpfn(p_sorted, NFP, NFN)

    # Averaging with Random Sampling labels only
    ind_rs = np.nonzero([r == 0 for r in rs0al1_sorted])[0]
    p_sorted2 = [p_sorted[i] for i in ind_rs]
    y_sorted2 = np.array([y_sorted[i] for i in ind_rs])
    NFPrs, NFNrs, NTNrs, NTPrs, TPRrs, FPRrs = compute_ROC(y_sorted2)
    umbral_tpfn_rs, pos_rs = compute_tpfn(p_sorted2, NFPrs, NFNrs)

    # Weighted averaging
    wy_sorted = [w_sorted[i] * y_sorted[i] for i in xrange(len(w_sorted))]
    NFPw, NFNw, NTNw, NTPw, TPRw, FPRw = compute_ROC(wy_sorted)
    umbral_tpfn_w, pos_w = compute_tpfn(p_sorted, NFPw, NFNw)

    # # NFP vs NFN 
    # plt.figure()
    # plt.plot(NFP, NFN, 'r', NFPrs, NFNrs, 'g', NFPw, NFNw, 'b')
    # plt.xlabel('Number of False Negatives')
    # plt.ylabel('Number of False Positives')
    # plt.show(block=False)

    # ROC: TPR vs FPR
    plt.figure()
    plt.plot(FPR, TPR, 'r', label='Unweighted')
    plt.plot(FPRrs, TPRrs, 'g', label='Random Sampling')
    plt.plot(FPRw, TPRw, 'b', label='Weighted')
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.title('Estimated ROC curve')
    plt.legend(loc=4)
    plt.plot(FPR[pos], TPR[pos], 'r.', markersize=10)
    plt.plot(FPRrs[pos_rs], TPRrs[pos_rs], 'g.', markersize=10)
    plt.plot(FPRw[pos_w], TPRw[pos_w], 'b.', markersize=10)
    plt.show(block=False)

    # ROC based on sklearn (the results are assentially the same)
    # from sklearn.metrics import roc_curve
    # FPR2, TPR2, tt = roc_curve(y_sorted, p_sorted)
    # FPRrs2, TPRrs2, tt = roc_curve(y_sorted2, p_sorted2)
    # FPRw2, TPRw2, tt = roc_curve(y_sorted, p_sorted, sample_weight=w_sorted)
    # plt.figure()
    # plt.plot(FPR2, TPR2, 'r', label='Unweighted')
    # plt.plot(FPRrs2, TPRrs2, 'g', label='Random Sampling')
    # plt.plot(FPRw2, TPRw2, 'b', label='Weighted')
    # plt.xlabel('FPR')
    # plt.ylabel('TPR')
    # plt.title('Estimated ROC curve (sklearn)')
    # plt.legend(loc=4)
    # plt.show(block=False)

    # Weights
    plt.figure()
    ws2 = np.sort(np.array(w))
    plt.plot(ws2)
    plt.xlabel('Sorted weight index')
    plt.ylabel('Weight value')
    plt.ylim([0, 0.3])
    plt.show(block=False)

    print "============================================="
    print "*** DATASET:"
    n_samples = len(y)
    print "--- Total size: {0} samples".format(n_samples)
    n_old = np.count_nonzero([r is None for r in rs0al1])
    print "------ Old labels:  {0} samples".format(n_old)
    n_recent = n_samples - n_old
    print "------ Recent labels:  {0} samples".format(n_recent)
    flags = zip(relabels, rs0al1)
    n_rec_rs = np.count_nonzero([x == (1, 0) for x in flags])
    n_rec_al = np.count_nonzero([x == (1, 1) for x in flags])
    n_new_rs = np.count_nonzero([x == (0, 0) for x in flags])
    n_new_al = np.count_nonzero([x == (0, 1) for x in flags])
    n_rs = n_rec_rs + n_new_rs
    n_al = n_rec_al + n_new_al
    n_new = n_new_rs + n_new_al
    n_rec = n_rec_rs + n_rec_al

    print "--------- Total Random Sampling: {0} samples".format(n_rs)
    print "--------- Total Active Learning: {0} samples".format(n_al)
    print "--------- Total Recycled: {0} samples".format(n_rec)
    print "--------- Total New:      {0} samples".format(n_new)
    print "-----------------------------------------------"
    print "------------ Recycled, Random Sampling: {0} samples".format(
        n_rec_rs)
    print "------------ Recycled, Active Learning: {0} samples".format(
        n_rec_al)
    print "------------ New, Random Sampling:      {0} samples".format(
        n_new_rs)
    print "------------ New, Active Learning:      {0} samples".format(
        n_new_al)

    print "*** THRESHOLD:"
    print "--- All samples: {0}".format(umbral_tpfn)
    print "--- RS:          {0}".format(umbral_tpfn_rs)
    print "--- W:           {0}".format(umbral_tpfn_w)
    print "*** B2C ESTIMATION:"
    print "--- Based on LABELS ONLY:"
    b2c_y_all = float((y == 1).sum())/n_samples
    y_recent = np.array(
        [y[n] for n in xrange(n_samples) if rs0al1[n] in {0, 1} or
         relabels[n] == 1])
    b2c_y_recent = float((y_recent == 1).sum())/n_recent
    b2c_y_rs = float((y_sorted2 == 1).sum())/n_rs
    b2c_y_w = sum([wy for wy in wy_sorted if wy > 0])/np.array(w_sorted).sum()

    print "------ All labels:      {0}".format(b2c_y_all)
    print "------ Recent labels: {0}".format(b2c_y_recent)
    print "------ Random sampling: {0}".format(b2c_y_rs)
    print "------ Weighted: {0}".format(b2c_y_w)

    print "--- Based on DECISIONS:"
    print pos_rs
    print FPRrs[pos_rs]
    print TPRrs[pos_rs]
    print pos_w
    print FPRw[pos_w]
    print TPRw[pos_w]

    return umbral_tpfn, umbral_tpfn_rs, umbral_tpfn_w


# def compute_threshold_tpfn(p, y, w_tr, rs0al1):

#     """ Compute three possible decision thresholds for a classifier with
#         predictions p for samples with labels y, depending on the use of
#         labeling information.

#         ARGS:
#            :p      :Preditions in the range [-1, 1]
#            :y      :Labels in {-1, 1}
#            :w      :Non-negative weights.
#            :rs0al1 :Type of labelling indicator.
#                      = 0 for samples taken with random sampling
#                      = 1 for samples taken with active learning
#                      None for samples with unknown labeling method.
#     """

#     orden = np.argsort(-1 * np.array(p))

#     # Sort all input arrays according to preds.
#     p_sorted = [preds_loo[i] for i in orden]
#     y_sorted = [int(y[i]) for i in orden]
#     rs0al1_sorted = [rs0al1[i] for i in orden]
#     w_sorted = [w_tr[i] for i in orden]

#     # Unweighted complete averaging.
#     NFP = np.cumsum([ys == 1 for ys in y_sorted])
#     NFN = np.cumsum([ys == -1 for ys in y_sorted[::-1]])[::-1]
#     DIFF = np.abs(NFP - NFN)
#     pos = np.argmin(DIFF)
#     umbral_tpfn = p_sorted[pos]

#     # Averaging with Random Sampling labels only
#     ind_rs = np.nonzero([r == 0 for r in rs0al1_sorted])[0]
#     p_sorted2 = [p_sorted[i] for i in ind_rs]
#     y_sorted2 = [y_sorted[i] for i in ind_rs]
#     NFP = np.cumsum([ys == 1 for ys in y_sorted2])
#     NFN = np.cumsum([ys == -1 for ys in y_sorted2[::-1]])[::-1]
#     DIFF = np.abs(NFP - NFN)
#     pos = np.argmin(DIFF)
#     umbral_tpfn_rs = p_sorted2[pos]

#     # Weighted averaging
#     wy_sorted = [w_sorted[i] * y_sorted[i] for i in range(len(w_sorted))]
#     NFP = np.cumsum([max(wy, 0) for wy in wy_sorted])
#     NFN = np.cumsum([max(-wy, 0) for wy in wy_sorted[::-1]])[::-1]
#     DIFF = np.abs(NFP - NFN)
#     pos = np.argmin(DIFF)
#     umbral_tpfn_w = p_sorted[pos]

#     return umbral_tpfn, umbral_tpfn_rs, umbral_tpfn_w


# ##########################
# 0. Configurable parameters
# ##########################

# Data file path
data_folder = './Data201605/'
labels_fpath = data_folder + 'dataset.pkl'

# ############
# 1. Data load
# ############

# Load labels and labeling mtadata from the labels file
with open(labels_fpath, 'r') as handle:
    data = pickle.load(handle)

wids = [w for w in data.keys() if data[w]['pred']['b2c_ready'] is not None]
wids_tr = [w for w in data.keys() if data[w]['pred']['b2c_ready'] is not None
           and data[w]['label']['b2c_ready'] in {'-1', '1'}]

y_all = np.array([int(data[w]['label']['b2c_ready']) for w in wids])
p_all = np.array([data[w]['pred']['b2c_ready'] for w in wids])

y_tr = np.array([int(data[w]['label']['b2c_ready']) for w in wids_tr])
p_tr = np.array([data[w]['pred']['b2c_ready'] for w in wids_tr])
w_tr = np.array([data[w]['weight'] for w in wids_tr])
rs0al1 = np.array([data[w]['marker'] for w in wids_tr])
relabels = np.array([data[w]['relabel'] for w in wids_tr])


# #####################
# 2. Compute thresholds
# #####################

umbral_tpfn, umbral_tpfn_rs, umbral_tpfn_w = plotROCs(
    p_tr, y_tr, w_tr, rs0al1, relabels)

# umbral_tpfn, umbral_tpfn_rs, umbral_tpfn_w = compute_threshold_tpfn(
#    preds_loo, y_tr, w_tr, rs0al1)

print 'umbral_tpfn = {0}'.format(umbral_tpfn)
print 'umbral_tpfn_rs = {0}'.format(umbral_tpfn_rs)
print 'umbral_tpfn_w = {0}'.format(umbral_tpfn_w)


# ##########################
# Plot predict distributions

plt.figure()
plt.subplot(121)
plt.hist(p_all, bins=40, label='All predict values')
plt.title('Distribution of all predict values')
plt.subplot(122)
plt.hist(p_tr, bins=40, label='Labeled data', color='g')
plt.title('Distribution of labeled predict values')
plt.show(block=False)


ipdb.set_trace()

