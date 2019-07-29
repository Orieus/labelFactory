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


def main():

    #######
    # Start
    #######

    # Set of available options from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_path', type=str, default=None,
                        help='Path to the labelling project')
    parser.add_argument('--url', type=str, default=None,
                        help='Label the specified url address only')
    parser.add_argument('--tm', type=str, default='expand',
                        help='Mode to transfer the new data: expand ' +
                        '(default) | project | contract')
    parser.add_argument('--user', type=str, default=None,
                        help='Use the specified name to identify the labeler')
    parser.add_argument('--export_labels', type=str, default=None,
                        help='Export labels. Options: all|rs|al (all labels' +
                        ' | only random sampling | only active learning)')

    parser.add_argument('--num_urls', type=int, default=10,
                        help='Number of examples to be labeled during a ' +
                        'single labelling session (default 10)')
    parser.add_argument('--type_al', type=str, default='random',
                        help='Type of active learning algorithm. Options: ' +
                        'tourney | random (default)')

    parser.add_argument('--ref_class', type=str, default=None,
                        help='Name of the category used by the active ' +
                        'learning algorithm to compute the sample scores')
    parser.add_argument('--alth', type=float, default=0.0,
                        help='Active learning theshold [0]')
    parser.add_argument('--p_al', type=float, default=0.0,
                        help='Active learning probability [0]')
    parser.add_argument('--p_relabel', type=float, default=0.0,
                        help='Probability of resampling an already labeled ' +
                        'sample [0]')
    parser.add_argument('--tourneysize', type=int, default=40,
                        help='Size of each active learning tournament [40]')

    # Read variables from the commmand line.
    args = parser.parse_args()

    # Launch labelling application
    labelfactory.run_labeler(
        args.project_path,
        args.url,
        args.tm,
        args.user,
        args.export_labels,
        args.num_urls,
        args.type_al,
        args.ref_class,
        args.alth,
        args.p_al,
        args.p_relabel,
        args.tourneysize)


if __name__ == "__main__":
    main()
