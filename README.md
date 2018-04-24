# labelFactory
A generic application for labelling a subset of sites in a web site collection, or a subset of docs in a text collection.  I can be potentially used for classification and labelling problems over hierarchies of categories.

**run_labeler** is a labelling application that can be potentially used for classification and labelling problems over hiearchies of categories.

# User Manual

## 1. Usage:

Run the application with

    python run_labeler.py [--project_path PROJECT_PATH] [--url URL] [--user USER] [--tm TM]

Options are:

   + `--project_path`: The path to the labeling project folder. If it is not specified, the application will ask for it.
   + `--url`: A single url to be labeled. This option can be used to revise urls that have been wrongly labeled in a previous labeling session.
   + `--user`: Name identifying the labelling user. To use this option, you must select `track_user: yes` in the configuration file.
   + `--tm`: Transfer mode. Specifies the criterium used to import new data from the input folder. Available options are:   
       * `expand`  : All urls existing in the input folder are integrated into the dataset. This is the default option.
       * `project` : New URLs cannot be added to the dataset, but only information about labels or predictions. 
       * `contract`: Only urls in the input folder are preserved in the data structure.

If the project folder does not exist, the application will create a new one, adding a copy of the default configuration file, and the execution stops so that the user can edit the configuration file (if applicable) and add some input file with urls to label.

If the project folder already exists, the following actions are executed:

### Step 1. Load the database.

Initially, load the tags, predictions and other data from the database (dataset.pkl).

### Step 2. Data import.

The application reads the new tags and predictions of the files in the `input` folder. Tags with unknown value are replaced by `unknown_label`. Once read, the files in the `input` folder are moved to the` used` folder.

### Step 3. Data integration.

In this step, the application merges the incoming labels and predictions (through the `input` folder) with the existing ones in the database.

This merger is made following the principle of considering that the incoming labels are more reliable than the old ones. Therefore, in general, all the `yes_label` and` no_label` incoming labels overwrite the old ones. The rest of the old tags are kept unless they are inconsistent with the old ones according to the hierarchical structure of categories, in which case they are deleted and replaced with the value that can be inferred, according to the following:

   + Any `yes_label` label of a category is propagated to all its predecessors (since if a url belongs to a certain subcategory, it will also belong to its parent category, and all its sister categories (which share the same parent) will receive a` no_label `
   + Any label `no_label` of a category is propagated to all its descendants (since if a url does not belong to a certain category, it can not belong to any of its subcategories).

If after all this process all the categories are `no_label`, all `no_label` values that do not come from the incoming labels are replaced by `unknown_label` values.

Finally, if at least one category in `Label_In` takes value` error_label`, all categories are re-labeled as `unknown`. This means that the error tags are not imported into the dataset (which would imply excluding their urls from the training sets) but they do override all the previous tags.

### Step 4. Selection of labels.

At this point an active learning algorithm is applied to select a subset of urls to tag.

### Step 5. Labeling

From this moment, a web browser will open, displaying the page that you want to tag, and a tagging window. Execution ends when the window has been manually closed, or after completing the labeling of the maximum number of urls to be scanned, specified in the variable `num_urls` of the configuration file.

The follosing is an example of the appearanc of the labeling window:

![Labeling window.](http://www.tsc.uc3m.es/~jcid/baul/VentanaEtiquetado.jpg)

As explained above, the following buttons always appear in the tagging window:

* One button for each of the categories specified in `categories`
* An `Other` button for the NO-category of the first level.
* An "Error" button

#### Labeling process.

The labeling of each url is multiple: each time a window button is pressed, the application generates a label for each of the categories specified in `categories`.

Any url that has not been previously tagged has the default `unknown_label` tag, indicating that the category is unknown.

The effect of labeling a url depends on whether the url is new (it has not been previously labeled) or not (that is, it has a previous label). We will distinguish the two cases below:

##### Tagging new urls.

The effect of pressing a button is as follows:

* Erronea button: this button must be pressed when the URL display has failed for some reason that could be temporary (server failures, page service interruption due to maintenance, etc). The effect of this pulsation is that all categories are labeled as `unknown_label`.

* Category button (e.g., `birds`, `primates`, or `Other`). The selected category is labeled `yes_label` and the value of other categories of the tree is inferred, when possible.


##### Tagging prelabeled urls

When the url has been previously tagged, in addition to the processing described for the new urls, the projection of the new tags on the old ones is done, following the same criteria that has been described for the merging of labels of the `input` folder.

### Step 6. Close.

When the tagging window is closed, the new tags are incorporated into the dataset, the `dataset.pkl` and` label_history.pkl` files are updated, and the execution finishes. In the `log` file of the project folder, an event log of the successive executions of the application is saved on this project.

##  2. Folder Structure
The application is integrated in the following folder structure

    run_labeler.py
    config.cf.default
    common/__init__.py
    common/lib/__init__.py
              /ConfigCfg.py
              /Log.py
              /labeler/__init__.py
                      /activelearning/__init__.py
                                     /activelearner.py
                      /labeling/__init__.py
                               /datamanager.py
                               /LabelGUIController.py
                               /labelprocessor.py
                               /LabelViewGeneric.py
                               /urlsampler.py

These are the minimal files required to run de labelling application. Besides of them, the application contains two data managmment tools,

    run_db2file.py
    run_file2db.py
    run_pkl2json.py

and, also, a tool for analyzing the labeled dataset

    run_analizer.py
    common/lib/__init__.py
              /dataanalyzer/__init__.py
                           /ROCanalyzer.py

## 2. Databases and data files.

The input data and the results of the labelling application are usually stored in a mongo database or in a set of files.

### 2.1. Complete project file struture

The complete data structure for a labelling project is the following:

        project_path/.
                    /dataset_labels.pkl     # Label dataset 
                    /dataset_predicts.pkl   # Dataset of urls and predictions 
                    /labelhistory.pkl   # Label event history
                    /config.cf     # Configuration file
                    /log           # Running event records
                    /input/.
                          /urls.csv
                          /[cat1]_labels.csv  # File of new labels
                          /[cat1]_preds.pkl  # File of new predictions
                          /[cat2]_labels.csv  # File of new labels
                          /[cat2]_preds.pkl  # File of new predictions
                          ...
                    /output/.
                           /labelhistory.csv  # Label history record
                           /[cat1]_labels.csv  # Label record about category cat1
                           /[cat2]_labels.csv  # Label record about category cat2
                           ...
                           /labelhistory.csv.old  # Old labelling events record
                           /[cat1]_labels.csv.old  # Old label record
                           /[cat2]_labels.csv.old  # Old label record
                           ...
                    /used/.
                         /[cat1]_[labels|pred][codigo1].pkl
                         /[cat2]_[labels|pred][codigo2].pkl
                         /[cat3]_[labels|pred][codigo3].pkl
                         ...

The content of these files is explained in the following sections

### 2.2 Main working folder

We will call `project_path` to the path to the folder containing the labelling project (the name of this path can be specified in a configuration file, that is explained later). All data files related to the labelling process will be located in this folder.

### 2.3 Subfolders

The main project folder contains three subfolders:

   * `input`: It contains all input data
   * `output`: It contains all output files
   * `used`: It stores copies of all input files

(the name of these folders can be specified in the configuration file).

During each execution, the application reads the files in folder `input`, saves a copy in `used` and removes them from the input folder.

The two files from the main folder contain the "internal state" of the application, i.e., all relevant information about the labelling process resulting from succesive executions of the application over this project.

   * `dataset_labels.pkl`: This file contains updated information about the labels. After each execution of the application, this file is modified in order to integrate the new labels. This file should be never modified, at the risk of loosing all labeling information.
   * `dataset_predicts.pkl`: This file contains the whole set of urls that can be potentially labeled. For each url, it may containg predictions computed from an external application (tipically, an automatic web classifier).
   * `label_history.pkl`: This file records all labelling events from the first execution of this project.

#### Input subfolder (`input`)

Before each execution of `run_labeler`, a new set of labels, input predictions or urls (obtained outside of the application) can be added to the dataset, by locating the files containing them in folder `project_path/labeling/input/`. The name and route of this files must follow the fomat

        project_path/input/[cat]_labels.csv

or

        project_path/input/[cat]_predict.pkl

depending on they are label or prediction files, respectively, where [cat] must be replaced by the name of the category corresponding to the labels or predictions contained in the files.

Also, it is possible to introduce a list of urls by means of a file

        project_path/input/urls.csv

with one single url address per line.

During each execution, the application reads the files in folder `/input/`, process them (integrating the new input information into the dataset) and removes them from the folder, saving a copy in folder `/used/`. The path and format of the copy is

        project_path/used/urls[code].csv
        project_path/used/[cat]_labels_in[code].csv
        project_path/used/[cat]_predict_in[code].pkl

where `[code]` is a number specifying the exact date (up to fractions of a second) when the file was processed, according to format

        [code] = [year][mond][day][hour][minute][second][fraction of second]

As stated above, the application has two running modes, that are specified in the configuration file:

    * `expand`  : All urls existing in the input folder are integrated into the dataset
    * `project` : New URLs cannot be added to the dataset, but only information about labels or predictions. 
                  All urls to label must be present in `dataset.pkl`.
                  The new urls in csv files are ignored by the application.
    * `contract`: Only urls in the input folder are preserved in the data structure

##### Format of the input files

The format of the input files must be the following:

* **File of urls** (`project_path/input/urls.csv`): A csv file with one url per line. The url can omit prefix `http://www.` or  `https://www.`
* **File of labels** (`project_path/input/[cat]_labels.csv`): A csv file. Each line must follow format `[url], [label]` where `[url]` is a url address with the same format than the file of urs, and `[label]` is the label, that can take any of the following values:
    * `yes_label` (default '1'), if the url belongs to category `[cat]` (specified in the name of the file)
    * `no_label` (def. '-1'), if the url does not belong to category `[cat]`
    * `unknown_label` (def. '0'), if the category is unknown
    * `error_label` (def. '-99'), if the url has any type of error.
    * Any other label is ignored (and treated in the same way than `unknown_label`). The default values can be modified from the configuration file (as explained later).
* **File of predictions** (`project_path/input/[cat]_predict.pkl`): The file of predictions is a dictionary of "wid's". A "wid" (web identifier) is a possibly simplified form or url address. 
    * The wid associated to a url can be identical to the url or, alternatively, a simplified form that is computed as follows:
        * Change capital letters to lower-case letters.
        * Remove prefixes "http://", "//", "www."
        * Replace points "." by "_"
        * Replace chracters "/" by "__".
    * The dictionary value for a given wid es in turn a dictionary in the form: `{'url': [url], 'pred': [pred]}` where  `[url]` is the url associated to the wid, and `[pred]` is a prediction of the degree of membership of such url to categoría `[cat]` specified in the file name. 

The prediction values are expected to be in the interval [-1, 1]. Actually, labelling is possible no mater whate the range of this predictions is, or even if no predictions are available. However, the behavior of the active learning algorithm could not be as expected if predictions do not lie in this margin.

#### Output subfolder.

During each execution, `run_labeler.py` changes the file structure as follows:

* Save into `project_path/used` a copy of the existing files in `project_path/input`
* Update `dataset_predicts.pkl` and `dataset_labels.pkl` with the information of the new predictions and the new labeling events, respectively
* Update file `project_path/label_history.pkl` (or create if it does not exist), with the record of the new labeling evengs.
* Generate the csv output files in folder `project_path/output/`. 

##### Output file format

Output csv files can be of two types:

* **Label files** (`[cat]_labels.csv`). These files, one per category, contain the label corresponding to each category, for all urls. The format of these files is identical to that of the files in folder `input`.
* **Label history file** (`labelshistory.csv`): a csv file recording all labeling evente generated in all executions of the software with this project. Each line records a labeling event, with the following format:
    * `date, [date], label, [label], marker, [marker], relabel, [relabel], url, [url]`, where
        * `[date]`: date of the labeling event 
        * `[label]`:  label assignd to the url
        * `[marker]`: type of labeling indicator: randon sampling: (0) or active learnig (1). 
        * `[relabel]`: indicate is the label is new (0) or if it is a revision of a pre-existing label (1). 
        * `[url]`: url address

## 3. Configuration file:

The configuration file is

    config.cf

and must be located at the project folder. If it does not exist, the application creates one by copying a default configuration file  (namely, file `config.cf.default` from the aplication folder structure). This file must be edited and adapted to the current labeling task.

This file contains several field, whose contents can be modified. The are described in the following secctions.

### 3.1. [DataPaths] Rutas de ficheros de datos

In this field the names of all the subfolders and files of the data folder can be modified

    # Labelling subfolders
    labeling_folder: labeling
    input_folder: input
    output_folder: output
    used_folder: used

    # Filenames
    dataset_fname: dataset.pkl
    labelhistory_fname: labelhistory.pkl
    labels_endname: _labels
    preds_endname: _predict.pkl

### 3.2. [Labeler] Categories

In this field, you define the categories you want to label, and the relationships between them. The set of categories must satisfy that, for each pair of categories, either they are disjoint to each other or one of them is a subcategory of the other. This allows the labeling of urls on category trees.

The set of categories is defined below. For example:

    # List of categories. Every pair of categories A and B must satisfy 
    # A in B, B in A, or intersection(A, B) = emptyset
    categories: ['mammals', 'birds', 'primates']

The relationship between categories is specified by a dictionary in which the entry A:B means that A is a subclass of B

    # Dictionary of dependencies between categories
    # {A:B, C:D, E:D } means that A is a subclass of B and C and E are 
    # subclasses of D
    parentcat: {'primates': 'mammals'}

An additional field allows specifying if the categories of the first level are exhaustive or not

    # If the categories are complete (i.e. they fill the observation space) then set
    # fill_with_Other to no. Otherwise, set fill_with_Other to yes, and a category
    # 'Other' will be added to the category set
    fill_with_Other: yes

If they are not, 'yes' must be indicated. In this case, a new category 'Other' will be created in order to label those urls that do not fit into any of the first level categories.

With this definition, the following hierarchy of categories is established:

    - 'mammals'
        - 'primates'
        - 'NO-primates'
    - 'birds'
    - 'Other'

Note that in order for the set of categories or subcategories in each level of the tree to be exhaustive, a "NO-category" is added to each level. However, the system will NOT add a button to the filler subcategories. In the previous example, the application will generate four labeling buttons:

    - 'mammals'
    - 'primates'
    - 'birds'
    - 'Other'

it being understood that those categories labeled as 'mammals' (and therefore, not labeled as 'primates') will be understood from the subcategory 'NO-primates'.

Therefore, during the execution of the application, the labeling window will show a button for each of the categories specified in the variable `categories`, together with (possibly) the category 'Other'. Additionally, a button will appear to label urls as ERROR in the case in which any problem with the access to the page prevents the labeling.

The following configuration parameters specify the values of the 4 possible labels that each category can have. These are the values that will appear in the output files.

    # List of labels
    yes_label: 1
    no_label: -1
    unknown_label = 0
    error_label = -99

If any label with a different value from the previous ones is found in an input file, it will be replaced by an `unknown_label` tag by the application.

Finally, the application allows keeping a record of the user who has created each tagging event.

    # Set the following to True if a user identifies will be requested on order 
    # to track different labelers.
    track_user: yes


### 3.3. [ActiveLearning] Parameters of the active learning algorithm.

    # In multiclass cases, the reference class is the class used by the active
    # learning algorithm to compute the sample scores.
    ref_class: birds

    # Max. no. of urls to be labeled at each labeling step
    num_urls: 10

    # Type of active learning algorithms
    type_al: tourney

    # AL threshold. This is used by the AL algorithm to compute the score
    # of each  sample. A standard choice is to set it equal to the 
    # decision threshold of the classifier model, but there may be good
    # reasons for other choices. For instance, is classes are umbalanced, 
    # we can take self.alth = 1 so as to promote sampling from the 
    # positive class
    alth: 1

    # Probability of AL sampling. Samples are selected using AL with 
    # probability p,
    # and using random sampling otherwise.
    p_al: 0.2

    # Probability of selecting a sample already labelled
    p_relabel: 0.2

    # Size of each tourney (only for 'tourney' AL algorithm)
    tourneysize: 40
