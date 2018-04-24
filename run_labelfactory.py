# -*- coding: utf-8 -*-
""" run_labeller is the main script for the labelling application.

    It must be invoked using

        python run_labeler.py [project_folder]

    Created on July, 2015
    Last update: Jan, 2017

    @autor: Jesus Cid.
"""

import argparse


import labelfactory.labelfactory as labelfactory

CF_FNAME = "config.cf"
CF_DEFAULT_PATH = "./config.cf.default"


def main():

    #######
    # Start
    #######

    # settings
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default=None,
                        help='Path to the labelling project')
    parser.add_argument('--url', type=str, default=None,
                        help='Label the specified url address only')
    parser.add_argument('--tm', type=str, default='expand',
                        help='Mode to transfer the new data: expand ' +
                        '(default), project or contract')
    parser.add_argument('--user', type=str, default=None,
                        help='Use the specified name to identify the labeler')
    parser.add_argument('--export_labels', type=str, default=None,
                        help='Export labels. Options: all|rs|al (all labels ' +
                        ' | only random sampling | only active learning')
    args = parser.parse_args()

    project_path = args.project_path
    url = args.url
    tm = args.tm
    user = args.user
    export_labels = args.export_labels

    # Launch labelling application
    labelfactory.run_labeler(project_path, url, tm, user, export_labels)


if __name__ == "__main__":
    main()
