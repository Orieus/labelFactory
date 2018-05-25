#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python libraries
from __future__ import print_function
import os
import sys
import pandas as pd

import MySQLdb
import sqlite3
from sqlalchemy import create_engine

import ipdb

# Local imports
from labelfactory.labeling import baseDM

# Services from the project
# sys.path.append(os.getcwd())


class DM_SQL(baseDM.BaseDM):

    """
    DataManager is the class providing read and write facilities to access and
    update the dataset of labels and predictions

    It assumes that data will be stored in SQL databases, though it have some
    facilities to import data from files

    It assumes a SQL database structure with 4 tables:

        preds
        label_info
        label_values
        labelhistory

    (the specific name of these tables is read from the configuratio file)

    The class provides facilities to:

        - Read and write data in a SQL database
        - ?
    """

    def __init__(self, source_type, dest_type, file_info, db_info,
                 categories, parentcat, ref_class, alphabet,
                 compute_wid='yes', unknown_pred=0):

        super(DM_SQL, self).__init__(
            source_type, dest_type, file_info, db_info, categories, parentcat,
            ref_class, alphabet, compute_wid='yes', unknown_pred=0)

        # Subclass-specific variables
        self.db_name = self.db_info['name']
        self.server = self.db_info['server']
        self.user = self.db_info['user']
        self.connector = self.db_info['connector']
        self.password = self.db_info['password']
        self.preds_tablename = self.db_info['preds_tablename']
        self.label_values_tablename = self.db_info['label_values_tablename']
        self.label_info_tablename = self.db_info['label_info_tablename']
        self.history_tablename = self.db_info['history_tablename']
        self.ref_name = self.db_info['ref_name']

        # Private variables
        self.__c = None
        self.__conn = None

    def __getTableNames(self):
        """
        Returns a list with the names of all tables in the database
        (taken from a code by Jeronimo Arenas)
        """

        # The specific command depends on whether we are using mysql or sqlite
        if self.connector == 'mysql':
            sqlcmd = ("SELECT table_name FROM INFORMATION_SCHEMA.TABLES " +
                      "WHERE table_schema='" + self.db_name + "'")
        else:
            sqlcmd = "SELECT name FROM sqlite_master WHERE type='table'"

        self.__c.execute(sqlcmd)
        tbnames = [el[0] for el in self.__c.fetchall()]

        return tbnames

    def __getColumnNames(self, tablename):
        """
        Returns a list with the names of all columns in the indicated table
        (taken from a code by Jeronimo Arenas)

        Args:
            tablename: the name of the table to retrieve column names
        """

        # Check if tablename exists in database
        if tablename in self.__getTableNames():
            # The specific command depends on whether we are using mysql or
            #  sqlite
            if self.connector == 'mysql':
                sqlcmd = "SHOW COLUMNS FROM " + tablename
                self.__c.execute(sqlcmd)
                columnnames = [el[0] for el in self.__c.fetchall()]
            else:
                sqlcmd = "PRAGMA table_info(" + tablename + ")"
                self.__c.execute(sqlcmd)
                columnnames = [el[1] for el in self.__c.fetchall()]

            return columnnames

        else:
            print('Error retrieving column names: Table does not exist on ' +
                  'database')
            return []

    def __addTableColumn(self, tablename, columnname, columntype):
        """
        Add a new column to the specified table

        Args:
            tablename    :Table to which the column will be added
            columnname   :Name of new column
            columntype   :Type of new column

        """

        # Check if the table exists
        if tablename in self.__getTableNames():

            # Check that the column does not already exist
            if columnname not in self.__getColumnNames(tablename):

                sqlcmd = ('ALTER TABLE ' + tablename + ' ADD COLUMN ' +
                          columnname + ' ' + columntype)
                self.__c.execute(sqlcmd)

                # Commit changes
                self.__conn.commit()

            else:
                print(
                    'Error adding column to table. The column already exists')
                print(tablename, columnname)

        else:
            print('Error adding column to table. Please, select a valid ' +
                  'table name from the list')
            print(self.__getTableNames())

    def __createDBtable(self, tablenames=None):
        """
        Creates any of the project tables.

            Args:
                tablenames :Name of any of the project tables. If None, all
                            tables required by a labeling project are created.
        """

        for name in tablenames:

            if name == self.preds_tablename:

                # Table for predictions
                # The name 'url' has historical reasons, but it keeps the
                # meaning: it specifies a kind of uniform resource location.
                # sql_cmd = """CREATE TABLE predictions(
                #                 Referencia TEXT,
                #                 url TEXT
                #                 )"""
                sql_cmd = ("""CREATE TABLE tablename(
                                Referencia TEXT,
                                url TEXT
                                )""").replace('tablename', name)
                self.__c.execute(sql_cmd)

                # One prediction column per category
                for cat in self.categories:
                    self.__addTableColumn(name, cat, 'DOUBLE')

            elif name == self.label_values_tablename:

                # Table for the label values
                sql_cmd = ("""CREATE TABLE tablename(
                                Referencia TEXT
                                )""").replace('tablename', name)
                self.__c.execute(sql_cmd)

                # One label column per category
                for cat in self.categories:
                    self.__addTableColumn(name, cat, 'INTEGER')

            elif name == self.label_info_tablename:

                # Table for the label metadata
                sql_cmd = ("""CREATE TABLE tablename(
                                Referencia TEXT,
                                marker INTEGER,
                                relabel INTEGER,
                                weight INTEGER,
                                userId TEXT,
                                datestr TEXT
                                )""").replace('tablename', name)
                self.__c.execute(sql_cmd)

            elif name == self.history_tablename:

                # Table for the historic record of labelling events
                sql_cmd = ("""CREATE TABLE tablename(
                                Referencia TEXT,
                                datestr TEXT,
                                url TEXT,
                                marker INTEGER,
                                relabel INTEGER,
                                label TEXT,
                                userID TEXT
                                )""").replace('tablename', name)
                self.__c.execute(sql_cmd)

            else:
                sys.exit('---- ERROR: Wrong table name')

        # Commit changes
        self.__conn.commit()

    def loadData(self):

        """ Load data and label history from file.
            This is the basic method to read the information about labels, urls
            and predictions from files in the standard format.

            If the dataset file or the labelhistory file does not exist, no
            error is returned, though empty data variables are returned.

            :Args:
                :source_type: type of data source ('file' or 'db')
                    Names of file sources should be stored in
                    two DataMgr attributes: self.dataset_files and
                    self.labelhistory_file

            :Returns:
                :df_labels:  Multi-index Pandas dataframe containing labels.
                             Fields are:
                    'info':  With columns marker', 'relabel', 'weight',
                             'userId', 'date'
                    'label': One column per categorie, containing the labels
                :df_preds: Pandas dataframa indexed by the complete list of
                           wids, with one column of urls and one addicional
                           column per category containing predictions.
                :labelhistory: Dataframe containing, for each wid, a record of
                        the labeling events up to date.

            IMPORTANT NOTE: labelhistory has a different structure in this
                            module than in other subclasses of baseDM, which
                            use a dictionary instead of a pandas dataframe to
                            record the label history.
        """

        # Connect to the database
        try:
            if self.connector == 'mysql':
                self.__conn = MySQLdb.connect(
                    self.server, self.user, self.password, self.db_name)
                self.__c = self.__conn.cursor()
            elif self.connector == 'sqlalchemy':
                engine_name = ('mysql://' + self.user + ':' + self.password +
                               '@' + self.server + '/' + self.db_name)
                print('---- Creating engine {}'.format(engine_name))
                engine = create_engine(engine_name)
                self.__conn = engine.connect()
            else:
                # sqlite3
                # sqlite file will be in the root of the project, we read the
                # name from the config file and establish the connection
                db_path = os.path.join(self.directory,
                                       self.dataset_fname + '.db')
                print("---- Connecting to {}".format(db_path))
                self.__conn = sqlite3.connect(db_path)
                self.__c = self.__conn.cursor()
            self.dbON = True
        except:
            print("---- Error connecting to the database")

        try:

            # #####################
            # Create missing tables

            # Create all tables that do not exist in the database yet.
            tablenames = self.__getTableNames()
            alltables = [self.preds_tablename, self.label_values_tablename,
                         self.label_info_tablename, self.history_tablename]
            missing_tables = [t for t in alltables if t not in tablenames]

            self.__createDBtable(missing_tables)

            # ################
            # Load predictions
            sqlQuery = 'SELECT * FROM ' + self.preds_tablename
            df_preds = pd.read_sql(
                sqlQuery, con=self.__conn, index_col=self.ref_name)

            # ###########
            # Load labels

            # Load label metadata
            sqlQuery = 'SELECT * FROM ' + self.label_info_tablename
            df_labelinfo = pd.read_sql(
                sqlQuery, con=self.__conn, index_col=self.ref_name)
            # Rename column 'datestr' to 'date':
            df_labelinfo.rename(columns={'datestr': 'date'}, inplace=True)
            # Convert column names into tuples
            df_labelinfo.columns = (
                [('info', c) for c in df_labelinfo.columns])

            # Load label values
            sqlQuery = 'SELECT * FROM ' + self.label_values_tablename
            df_labelvalues = pd.read_sql(
                sqlQuery, con=self.__conn, index_col=self.ref_name)
            # Convert column names into tuples
            df_labelvalues.columns = (
                [('label', c) for c in df_labelvalues.columns])

            # Joing label metadata and label values into a single dataframe
            # df_labels = pd.concat([df_labelinfo, df_labelvalues])
            df_labels = df_labelinfo.join(df_labelvalues)

            # Convert tuple column names to multi-index
            df_labels.columns = pd.MultiIndex.from_tuples(
                df_labels.columns)

            # ##################
            # Load label history
            sqlQuery = 'SELECT * FROM ' + self.history_tablename
            # Read dataframe. Note that I do not take any reference columns
            labelhistory = pd.read_sql(sqlQuery, con=self.__conn)
            # Rename columns datestr to date
            # (this is required because 'date' is a reserved word in sql)
            labelhistory.rename(
                columns={'datestr': 'date', self.ref_name: 'wid'},
                inplace=True)

        except Exception as E:
            print('Exception {}'.format(str(E)))

        return df_labels, df_preds, labelhistory

    def get_df(self, data, labelhistory):

        """ Converts the data dictionary used in former versions of the web
            labeler into the label and prediction dataframes.

            THERE IS NO VERSION OF THIS METHOD FOR SQL DATAMANAGER.

            The version of get_df in the base clase doesw not work for dmSQL
            because it uses a dicionary form of labelhistory.

            I do not create a versio nof this function for SQL because it is
            likely unnecesary
        """

        sys.exit(
            '---- ERROR: There is no version of get_df method for sql data')

        return

    def saveData(self, df_labels, df_preds, labelhistory, dest='file'):

        """ Save label and prediction dataframes and labelhistory pickle files.
            If dest='mongodb', they are also saved in a mongo database.

            If dest='mongodb', the dataframes are store in the mode specified
            in self.db_info['mode'].
                'rewrite' :The existing db collection is removed and data are
                           saved in a new one
                'update'  :The data are upserted to the existing db.

            :Args:
                :df_labels: Pandas dataframe of labels
                :df_preds:  Pandas dataframe of predictions
                :labelhistory:
                :dest: Type of destination: 'file' (data is saved in files) or
                 'mongodb'
        """

        # Connect to the database
        try:
            ipdb.set_trace()
            if self.connector == 'mysql':
                # self.__conn = MySQLdb.connect(
                #     self.server, self.user, self.password, self.db_name)
                # self.__c = self.__conn.cursor()
                engine_name = ('mysql://' + self.user + ':' + self.password +
                               '@' + self.server + '/' + self.db_name)
                ipdb.set_trace()
                print('---- Creating engine {}'.format(engine_name))
                engine = create_engine(engine_name)
                self.__conn = engine.connect()
            else:
                # sqlite3
                # sqlite file will be in the root of the project, we read the
                # name from the config file and establish the connection
                db_path = os.path.join(self.directory,
                                       self.dataset_fname + '.db')
                print("---- Connecting to {}".format(db_path))
                self.__conn = sqlite3.connect(db_path)
                self.__c = self.__conn.cursor()
            self.dbON = True
        except:
            print("---- Error connecting to the database")

        # Save predictions.
        # WARINING: the Predictions dataframe changes only when predictions
        # have been imported. Thus, it should be not saved systematically.
        # Save let see if replace works, and later we can test append.
        # Note that column 'date' is rename 'columns 'datestr'
        # (this is required because 'date' is a reserved word in sql)
        df_preds.to_sql(
            self.preds_tablename, self.__conn, if_exists='replace',
            index=True, index_label=self.ref_name)

        # Save labels

        # Drop tables
        # Let's see if to_sql works.  If so, dropping tables is not necessary.
        # self.__c.execute("DROP TABLE " + self.label_values_tablename)
        # self.__createDBtable(self.label_values_tablename)
        # self.__c.execute("DROP TABLE " + self.label_info_tablename)
        # self.__c.execute("DROP TABLE " + self.label_history_tablename)

        # let see if replace works, and later we can test append.
        # Note that column 'date' is rename 'columns 'datestr'
        # (this is required because 'date' is a reserved word in sql)
        df_labels['info'].rename(columns={'date': 'datestr'}).to_sql(
            self.label_info_tablename, self.__conn, if_exists='replace',
            index=True, index_label=self.ref_name)

        df_labels['label'].to_sql(
            self.label_values_tablename, self.__conn, if_exists='replace',
            index=True, index_label=self.ref_name)
        # Note that column 'date' is rename 'columns 'datestr'
        # (this is required because 'date' is a reserved word in sql)
        labelhistory.rename(
            columns={'date': 'datestr', 'wid': self.ref_name}).to_sql(
            self.history_tablename, self.__conn, if_exists='replace',
            index=False, index_label=None)

        self.__conn.commit()
