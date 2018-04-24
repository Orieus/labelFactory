#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" run_labeller is the main script for the labelling application.

    It must be invoked using

        python run_labeler.py [project_folder]

    Created on July, 2015
    Last update: Jan, 2017

    @autor: Jesus Cid.
"""

import ast
import sys
import os
import shutil

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
    #######

    # Check if project folder exists. Otherwise create a default one.
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = raw_input2("Select the (absolute or relative) path to" +
                                  " the labeling project folder: ")
    if not project_path.endswith('/'):
        project_path = project_path + '/'

    # Check if project folder exists. This is necessary to follow
    if not os.path.isdir(project_path):
        createfolder = raw_input2("Folder " + project_path +
                                  "does not exist. Create? (y/n)")

        if createfolder == "y":
            os.makedirs(project_path)    # Create folder
        else:
            sys.exit("A route to the project folder must be provided.\n")

    #########################
    # Read configuration data
    #########################

    # Check if configuration file existe
    config_path = project_path + CF_FNAME
    if not os.path.isfile(config_path):
        shutil.copy(CF_DEFAULT_PATH, config_path)
        print("The project folder must contain a configuration file.")
        print("A default configuration file has been copied.")
        print("Please check and modify it if necessary before continuing.")

    # Read data from the configuation file
    cf = Cfg(config_path)

    # Data source and destination (options: file, mongodb)
    source_type = cf.get('DataPaths', 'source_type')
    dest_type = cf.get('DataPaths', 'dest_type')
    # This is for backward compatibility
    if source_type is None:
        source_type = 'file'
    if dest_type is None:
        dest_type = 'file'

    # Mongo DB settings
    if source_type == 'mongodb' or dest_type == 'mongodb':
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

    # Read file and folder names related to the dataset files.
    if source_type == 'file' or dest_type == 'file':
        file_info = {'project_path': project_path,
                     'input_folder': cf.get('DataPaths', 'input_folder'),
                     'output_folder': cf.get('DataPaths', 'output_folder'),
                     'used_folder': cf.get('DataPaths', 'used_folder'),
                     'dataset_fname': cf.get('DataPaths', 'dataset_fname'),
                     'labelhistory_fname': cf.get('DataPaths',
                                                  'labelhistory_fname'),
                     'labels_endname': cf.get('DataPaths', 'labels_endname'),
                     'preds_endname': cf.get('DataPaths', 'preds_endname'),
                     'urls_fname': cf.get('DataPaths', 'urls_fname')}
        # 'recycle_endname': cf.get('DataPaths', 'recycle_endname')
    else:
        # The prediction file is stored in files, so this is still required
        file_info = {'project_path': project_path,
                     'input_folder': cf.get('DataPaths', 'input_folder'),
                     'dataset_fname': cf.get('DataPaths', 'dataset_fname'),
                     'preds_endname': cf.get('DataPaths', 'preds_endname')}

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
    log.info('*****************************')
    log.info('****** WEB LABELER **********')

    ############################
    # Pre-processing config data
    ############################

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
    data_mgr = DataManager(source_type, dest_type, file_info, db_info,
                           categories, parentcat, ref_class, alphabet,
                           compute_wid, unknown_pred)

    ###################
    # Read all datasets
    ###################

    log.info('Carga de datos')

    # Load data from the standard datasets.
    df_labels, df_preds, labelhistory = data_mgr.loadData(source_type)

    # Read dataset
    log.info("-- Cargando datos del repositorio")
    preds, labels, urls, markers, relabels, weights, userIds = \
        data_mgr.getDataset(df_labels, df_preds)

    if len(preds) == 0 and len(labels) == 0:
        log.error(u"El repositorio de datos está vacío")
        sys.exit()

    if len(urls) == 0:
        log.error(u"El repositorio de datos no tiene urls. Añada un fichero " +
                  file_info['urls_fname'] + ".csv a la subcarpeta " +
                  file_info['input_folder'] + " del proyecto")
        sys.exit()

    #############
    # Select URLs
    #############
    for w in df_labels.index:
        # Write your selection condition here:
        if df_labels.loc[w]['label', 'Holding-'] == yes_label:
            date = df_labels.loc[w]['info', 'date']
            try:
                if date.year == 2017:
                    print('www.' + w)
            except:
                print("Error in {0}".format(w))
                print(date)

if __name__ == "__main__":
    main()
