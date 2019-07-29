#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" run_labeller analyzes some statistics about the label dataset

    It must be invoked using

        python run_labeler.py [project_folder]

    Created on Jan, 2017
    @autor: Jesus Cid.
"""

import ast
import sys
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipdb

# Local imports
from labelfactory.ConfigCfg import ConfigCfg as Cfg
from labelfactory.Log import Log
from labelfactory.labeling.dmFiles import DM_Files
from labelfactory.labeling.dmSQL import DM_SQL
# from labelfactory.labeling.datamanager import DataManager
import labelfactory.dataanalyzer.ROCanalyzer as ROCanalyzer

CF_FNAME = "config.cf"
CF_DEFAULT_PATH = "./config.cf.default"


def main():

    #########################
    # Configurable parameters
    #########################
    n_bins = 60   # No. of bins for histogram plots

    #######
    # Start
    #######

    # Check if project folder exists. Otherwise create a default one.
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = input("Select the (absolute or relative) path to the " +
                             "labeling project folder: ")
    if not project_path.endswith('/'):
        project_path = project_path + '/'

    # Check if project folder exists. This is necessary to follow
    if not os.path.isdir(project_path):
        sys.exit("Project folder does not exist")

    # Check if configuration file existe
    config_path = project_path + CF_FNAME
    if not os.path.isfile(config_path):
        sys.exit("Configuration file does not exist")

    #########################
    # Read configuration data
    #########################

    # Read data from the configuation file
    cf = Cfg(config_path)

    # Data source and destination (options: file, mongodb)
    # source_type = cf.get('DataPaths', 'source_type')
    # source_type = 'mongodb'   # 'mongodb'
    # dest_type = 'file'
    # Data source and destination (options: file, mongodb)
    source_type = cf.get('DataPaths', 'source_type')
    dest_type = cf.get('DataPaths', 'dest_type')

    # This is for backward compatibility
    if source_type is None:
        source_type = 'file'
    if dest_type is None:
        dest_type = 'file'

    # Mongo DB settings
    if source_type == 'mongodb':
        db_info = {'name': cf.get('DataPaths', 'db_name'),
                   'hostname': cf.get('DataPaths', 'db_hostname'),
                   'user': cf.get('DataPaths', 'db_user'),
                   'pwd': cf.get('DataPaths', 'db_pwd'),
                   'label_coll_name': cf.get(
                        'DataPaths', 'db_label_coll_name'),
                   'history_coll_name': cf.get(
                        'DataPaths', 'db_history_coll_name'),
                   'port': cf.get('DataPaths', 'db_port'),
                   'mode': cf.get('DataPaths', 'db_mode')}
    else:
        db_info = None

    # File information is required in all cases, because predictions are only
    # saved in files.
    file_info = {'project_path': project_path,
                 'input_folder': cf.get('DataPaths', 'input_folder'),
                 'output_folder': cf.get('DataPaths', 'output_folder'),
                 'used_folder': cf.get('DataPaths', 'used_folder'),
                 'dataset_fname': cf.get('DataPaths', 'dataset_fname'),
                 'labelhistory_fname': cf.get('DataPaths',
                                              'labelhistory_fname'),
                 'labels_endname': cf.get('DataPaths', 'labels_endname'),
                 'preds_endname': cf.get('DataPaths', 'preds_endname'),
                 'urls_fname': cf.get('DataPaths', 'urls_fname'),
                 'export_labels_fname': cf.get('DataPaths',
                                               'export_labels_fname')
                 }

    # Type of wid: if 'yes', the wid is computed as a transformed url.
    #              if 'no', the wid is taken equal to the url.
    compute_wid = cf.get('Labeler', 'compute_wid')

    # List of categories to label.
    categories = ast.literal_eval(cf.get('Labeler', 'categories'))
    parentcat = ast.literal_eval(cf.get('Labeler', 'parentcat'))
    fill_with_Other = cf.get('Labeler', 'fill_with_Other')

    # Possible labels for each category
    yes_label = cf.get('Labeler', 'yes_label')
    no_label = cf.get('Labeler', 'no_label')
    unknown_label = cf.get('Labeler', 'unknown_label')
    error_label = cf.get('Labeler', 'error_label')
    alphabet = {'yes': yes_label, 'no': no_label, 'unknown': unknown_label,
                'error': error_label}

    unknown_pred = int(cf.get('Labeler', 'unknown_pred'))

    # In multiclass cases, the reference class is the class used by the active
    # learning algorithm to compute the sample scores.
    ref_class = cf.get('ActiveLearning', 'ref_class')

    ##########
    # Log file
    ##########

    # Create the log object
    log = Log(project_path + 'log')
    # Starting message for the log output.
    log.info('********************************')
    log.info('****** LABEL ANALYSIS **********')

    ############################
    # Pre-processing config data
    ############################

    # Verify that parentclass names are in the category set
    for c in parentcat:
        if c not in categories or parentcat[c] not in categories:
            log.error("There are unknown categories in the parentcat " +
                      " dictionary")
            sys.exit()

    # Verify that ref_class is one of the given categories
    if ref_class not in categories:
        log.error("The reference class is not in the set of categories. " +
                  "Revise the assignment to ref_class in the config.cf file")
        sys.exit()

    # Include the negative class in the category tree.
    if fill_with_Other.lower() == 'yes':
        extra_class = 'Other'
        while extra_class.lower() in [c.lower() for c in categories]:
            extra_class += 'X'
        categories.append(extra_class)

    # Include categories without parents in the parent dictionary.
    for cat in categories:
        if cat not in parentcat:
            parentcat[cat] = None

    #####################
    # Create main objects
    #####################

    # Data manager object
    if source_type == 'file' or source_type == 'mongodb':
        data_mgr = DM_Files(source_type, dest_type, file_info, db_info,
                            categories, parentcat, ref_class, alphabet,
                            compute_wid, unknown_pred)
    elif source_type == 'sql':
        data_mgr = DM_SQL(source_type, dest_type, file_info, db_info,
                          categories, parentcat, ref_class, alphabet,
                          compute_wid, unknown_pred)

    ###################
    # Read all datasets
    ###################

    log.info('Carga de datos')

    # Load data from the standard dataset.
    df_labels, df_preds, labelhistory = data_mgr.loadData()

    if len(df_preds) == 0 and len(df_labels) == 0:
        log.error(u"El repositorio de datos está vacío")
        sys.exit()

    # ##############
    # Main variables
    # ##############

    # Sets of wids
    wids = df_preds.index                         # wids with predictions
    wids_tr = df_labels.index                     # wids with labels
    wids_ptr = [w for w in wids_tr if w in wids]  # wids with labels and preds.

    # Subset of categories with some preds
    cat_subset = []
    for c in categories:
        preds_c = df_preds[c].values

        # I use pd.notnull to take both None's and nan's into account
        # if np.any(np.not_equal(preds_c, None)):
        if np.any(pd.notnull(preds_c)):
            cat_subset.append(c)

    # Label info arrays
    w_tr = df_labels['info', 'weight'].values
    rs0al1 = df_labels['info', 'marker'].values
    relabels = df_labels['info', 'relabel'].values

    # ###################
    # Analyze predictions
    # ###################

    # ########################################
    # Complete predict distribution histograms

    # Select categories with nontrivial predictions only
    preds = {}
    for c in cat_subset:
        preds_c = df_preds[c].values
        # preds[c] = preds_c[np.not_equal(preds_c, None)]
        preds[c] = preds_c[pd.notnull(preds_c)].tolist()

    # Plot predict distributions for the selected categories
    nc = len(preds)
    f, ax = plt.subplots(nc, sharex=True, sharey=True)
    if nc == 1:
        ax = [ax]

    for i, c in enumerate(preds):
        # The small bias is to avoid an error if all values are equal
        r = (np.min(preds[c]) - 1e-20, np.max(preds[c]) + 1e-20)

        # Plot histogram
        ax[i].hist(preds[c], bins=n_bins, range=r, label='All predict values',
                   density=True)
        ax[i].set_ylabel(c)

    # Remove spaces between plots and set equal x and y axes.
    ax[0].set_title('Pred-distributions')
    f.subplots_adjust(hspace=0)

    # Remove xtick for all but bottom plot.
    plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    plt.show(block=False)
    fig_dir = os.path.join(project_path, 'figures')
    if not os.path.isdir(fig_dir):
        os.makedirs(fig_dir)
    plt.savefig(os.path.join(fig_dir, 'hist_preds.png'))

    # ####################################################
    # Labeled vs unlabeled predict distribution histograms

    nc = len(cat_subset)
    f, ax = plt.subplots(1, nc, sharex=True, sharey=True)
    if nc == 1:
        ax = [ax]
    for i, c in enumerate(cat_subset):

        p_all = df_preds[c].values
        # p_all = p_all[np.not_equal(p_all, None)]
        p_all = p_all[pd.notnull(p_all)].tolist()

        p_ptr = np.array([df_preds.loc[w][c] for w in wids_ptr])
        p_ptr = p_ptr[pd.notnull(p_ptr)]

        # The small bias is to avoid an error if all values are equal
        r_all = (np.min(p_all) - 1e-20, np.max(p_all) + 1e-20)
        r_ptr = (np.min(p_ptr) - 1e-20, np.max(p_ptr) + 1e-20)

        ax[i].hist(p_all, bins=n_bins, range=r_all,
                   label='All predict', alpha=0.5, density=True, linewidth=0)
        ax[i].hist(p_ptr, bins=n_bins, range=r_ptr, label='Labeled data',
                   alpha=0.5, density=True, linewidth=0, color='g')
        ax[i].set_title(c)

    ax[nc - 1].legend(loc='upper right')
    # Remove spaces between plots and set equal x and y axes.
    ax[0].set_ylabel('Distribution of predict values')
    f.subplots_adjust(wspace=0.05)
    # Remove xtick for all but bottom plot.
    plt.setp([a.get_yticklabels() for a in f.axes[1:]], visible=False)
    plt.show(block=False)
    plt.savefig(os.path.join(fig_dir, 'hist_preds_lu.png'))

    # ##############
    # Label analysis
    # ##############

    # Print global statistics about the different kind of labels
    n_samples, n_rs, n_al = ROCanalyzer.compute_globalstats(rs0al1, relabels)

    # Label counts and label proportions per main category
    rs1al0 = rs0al1 == 0
    nW = np.sum(w_tr)
    sumAll = {}
    sumRS = {}
    sumW = {}
    propAll = {}
    propRS = {}
    propW = {}

    for c in categories:
        y = df_labels['label'][c].values == yes_label
        sumAll[c] = np.sum(y)
        sumRS[c] = np.dot(rs1al0, y.astype(float))
        sumW[c] = np.dot(w_tr, y.astype(float))
        propAll[c] = float(sumAll[c]) / n_samples
        propRS[c] = float(sumRS[c]) / n_rs
        propW[c] = float(sumW[c]) / nW

    main_cats = [c for c in categories if parentcat[c] is None]
    sub_cats = [c for c in categories if parentcat[c] is not None]

    # Print label counts
    print("No. of labels per main category:")
    for c in main_cats:
        print(f"    - {c}: {sumAll[c]}")

    # Print label counts
    print("No. of labels in subcategories:")
    for c in sub_cats:
        print(f"    - {c}: {sumAll[c]}")

    # Print label proportions
    print("Label proportions per main category:")
    print(" -- Random Sampling:")
    for c in main_cats:
        print(f"    - {c}: {propRS[c]}")
    print(" -- Active Learning:")
    for c in main_cats:
        print(f"    - {c}: {propW[c]}")

    # Print label proportions
    print("Label proportions per subcategories:")
    print(" -- Random Sampling:")
    for c in sub_cats:
        print(f"    - {c}: {propRS[c]}")
    print(" -- Active Learning:")
    for c in sub_cats:
        print(f"    - {c}: {propW[c]}")

    # ############
    # ROC analysis

    # For this part we must use only those samples with both label and predict.
    w_ptr = np.array([df_labels.loc[w]['info', 'weight'] for w in wids_ptr])
    for c in cat_subset:
        y_aux = np.array([df_labels.loc[w]['label', c] for w in wids_ptr])
        y_ptr = np.array([1 if yk == yes_label else -1 for yk in y_aux])
        p_ptr = np.array([df_preds.loc[w][c] for w in wids_ptr])

        # ##################
        # Compute thresholds
        fpath = os.path.join(fig_dir, f'ROC_{c}.png')
        umbral_tpfn, umbral_tpfn_rs, umbral_tpfn_w = ROCanalyzer.plotROCs(
            p_ptr, y_ptr, w_ptr, rs0al1, relabels, c, fpath=fpath)

    # ###################
    # Plot sorted weights

    # Weight distribution
    plt.figure()
    ws2 = np.sort(np.array(w_tr))
    plt.semilogy(ws2)
    plt.xlabel('Sorted weight index')
    plt.ylabel('Weight value')
    # plt.ylim([0, 60000000000])
    plt.show(block=False)
    plt.savefig(os.path.join(fig_dir, 'hist_weights.png'))

    ipdb.set_trace()

if __name__ == "__main__":
    main()
