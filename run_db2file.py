#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" run_db2file is a tool to migrate a labeled dataset in a mongo database to
    pickle file.

    It must be invoked using

        python run_db2file.py <project_folder>

    Created on Dec, 2016
    @autor: Jesus Cid.
"""

import ast
import time
import sys
import os
import ipdb

# Local imports
from labelfactory.ConfigCfg import ConfigCfg as Cfg
from labelfactory.Log import Log
from labelfactory.labeling.datamanager import DataManager

CF_FNAME = "config.cf"
CF_DEFAULT_PATH = "./config.cf.default"


def main():

    # To complete the migration to python 3, I should replace all "raw_input"
    # by "input". Transitorily, to preserve compatibility with python 2, I
    # simply rename inut to raw_input
    if sys.version_info.major == 3:
        raw_input2 = input
    else:
        raw_input2 = raw_input

    #######
    # Start

    # Check if project folder exists. Otherwise exit.
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = raw_input2("Select the (absolute or relative) path to" +
                                  " the labeling project folder: ")
    if not project_path.endswith('/'):
        project_path = project_path + '/'

    # Check if project folder exists. This is necessary to follow
    if not os.path.isdir(project_path):
        sys.exit("Project folder does not exist")

    #########################
    # Read configuration data

    # Check if configuration file existe
    config_path = project_path + CF_FNAME
    if not os.path.isfile(config_path):
        sys.exit("Configuration file does not exist")

    # Read data from the configuation file
    cf = Cfg(config_path)

    # Data source and destination (options: file, mongodb)
    source_type = 'mongodb'
    dest_type = 'file'

    # Mongo DB settings
    db_info = {'name': cf.get('DataPaths', 'db_name'),
               'hostname': cf.get('DataPaths', 'db_hostname'),
               'user': cf.get('DataPaths', 'db_user'),
               'pwd': cf.get('DataPaths', 'db_pwd'),
               'label_coll_name': cf.get('DataPaths', 'db_label_coll_name'),
               'history_coll_name': cf.get('DataPaths',
                                           'db_history_coll_name'),
               'port': cf.get('DataPaths', 'db_port'),
               'mode': cf.get('DataPaths', 'db_mode')}

    # Folder containing the urls to label
    file_info = {'project_path': project_path,
                 'input_folder': cf.get('DataPaths', 'input_folder'),
                 'output_folder': cf.get('DataPaths', 'output_folder'),
                 'used_folder': cf.get('DataPaths', 'used_folder'),
                 'dataset_fname': cf.get('DataPaths', 'dataset_fname'),
                 'labelhistory_fname': cf.get(
                    'DataPaths', 'labelhistory_fname'),
                 'labels_endname': cf.get('DataPaths', 'labels_endname'),
                 'preds_endname': cf.get('DataPaths', 'preds_endname'),
                 'urls_fname': cf.get('DataPaths', 'urls_fname')}

    # Type of wid: if 'yes', the wid is computed as a transformed url.
    #              if 'no', the wid is taken equal to the url.
    compute_wid = cf.get('Labeler', 'compute_wid')

    # List of categories to label.
    categories = ast.literal_eval(cf.get('Labeler', 'categories'))
    parentcat = ast.literal_eval(cf.get('Labeler', 'parentcat'))

    # Possible labels for each category
    yes_label = cf.get('Labeler', 'yes_label')
    no_label = cf.get('Labeler', 'no_label')
    unknown_label = cf.get('Labeler', 'unknown_label')
    error_label = cf.get('Labeler', 'error_label')
    alphabet = {'yes': yes_label, 'no': no_label, 'unknown': unknown_label,
                'error': error_label}

    # In multiclass cases, the reference class is the class used by the active
    # learning algorithm to compute the sample scores.
    ref_class = cf.get('ActiveLearning', 'ref_class')

    ##########
    # Log file

    # Create the log object
    log = Log(project_path + 'log')
    log.info('*****************************')
    log.info('****** WEB LABELER: *********')

    #####################
    # Create main objects

    # Data manager object
    data_mgr = DataManager(source_type, dest_type, file_info, db_info,
                           categories, parentcat, ref_class, alphabet,
                           compute_wid)

    ##############
    # Read dataset

    # Load data from the standard dataset.
    log.info('Carga de datos')
    df_labels, df_preds, labelhistory = data_mgr.loadData(source_type)

    ###############
    # Migrate to DB

    # Save data and label history into db
    log.info("-- Saving data in file")
    start = time.clock()
    ipdb.set_trace()
    data_mgr.saveData(df_labels, df_preds, labelhistory, dest='file')
    log.info(str(time.clock() - start) + ' seconds')

if __name__ == "__main__":
    main()
