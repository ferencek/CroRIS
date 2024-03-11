# CroRIS tool

A tool for uploading article entries to CroRIS database. The instructions below were tested on Ubuntu 20.04 but might also work on other Linux distributions.

## Getting started

### Installation

```
virtualenv -p python3.8 croris-env
source croris-env/bin/activate
git clone https://gitlab.cern.ch/CMS-IRB/CroRIS.git
cd CroRIS
pip install -r requirements.txt
```

The next time you will need to work with the repository, you will just need to source the environment

```
source croris-env/bin/activate
cd CroRIS
```

## Running the code

### Getting the list of articles

1. Go to the [Inspire HEP](https://inspirehep.net) database

2. Get the list of articles by using the following command (2023 is used here just as an example)

```
find a brigljevic, v and cn cms and jy 2023 and ps p
```

**NOTE:** Change the author (`a`), the collaboration name (`cn`) and the journal year (`jy`) fields as appropriate.

Place the pointer above the "cite all" button and select BibTeX in the drop-down list as the output format. Save the output to `list_of_papers.bib`

Please note that the returned list of articles could contain errata published in 2023 for otherwise older articles. Please remove any articles for which the `year` field is older than 2023. In addition, check if there are any articles with more than one DOI string. These are typically the already-mentioned errata articles but it is nevertheless good to double-check the reason for more than one DOI string. Either way, you will need to decide how to handle such articles, exclude them altogether or keep them but with just one DOI string (we generally do not upload errata articles).

3. Run the following command

```
python prepare_input.py -i list_of_papers.bib -o CroRIS_input.json |& tee prepare_input_`date "+%Y%m%d_%H%M%S"`.log
```

**NOTE:** Piping the output to the `tee` command will both print it to the screen and save it in a log file containing a time stamp in its name. Before running the script, please check that the `keywords`, `authors`, `journals`, and `issn` are correctly defined in [`configuration.py`](https://gitlab.cern.ch/CMS-IRB/CroRIS/blob/master/configuration.py)

In the above example command `prepare_input.py` takes `list_of_papers.bib` as input and collects all the information needed as input for CroRIS and stores it in the `CroRIS_input.json` file.

**NOTE:** The format of the output JSON file does not yet fully conform to the specifications of the [CroRIS API](https://wiki.srce.hr/display/CRORIS/CROSBI+API). This is on the to-do list.
