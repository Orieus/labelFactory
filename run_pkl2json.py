""" run_pkl2json reads all pkl files in the given folder structure and converts
    them to json
"""

import sys
import os
import pickle
import glob
import json

# ###############
# Get folder path
# ###############

# Checky python version.
# This code should be run using the python version used to create the pkl
# files in the given folder.
if sys.version_info.major == 3:
    raw_input2 = input
else:
    raw_input2 = raw_input

# Check if folder exists. Otherwise create a default one.
if len(sys.argv) > 1:
    f_path = sys.argv[1]
else:
    f_path = raw_input2(
        "Select the (absolute or relative) path to the folder structure " +
        "containing the  working folders: ")
# if not project_path.endswith('/'):
#     project_path = project_path + '/'

# Check if project folder exists. This is necessary to follow
if os.path.isdir(f_path):
    datafiles = glob.glob(f_path + '**/*.pkl')   # , recursive=True)
elif os.path.isfile(f_path):
    datafiles = [f_path]
else:
    exit("Folder " + f_path + "does not exist.")

import ipdb
ipdb.set_trace()
print("Converting the following files: {}".format(datafiles))
x = raw_input2("Proceed [y/n]?")

if x == 'y':

    for fname in datafiles:
        with open(fname, 'rb') as f:
            data = pickle.load(f)

        for url in data:
            for x in data[url]:
                print(data[url][x]['date'])
                data[url][x]['date'] = data[url][x]['date'].isoformat()

        fout = fname.replace('.pkl', '.json')
        with open(fout, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
