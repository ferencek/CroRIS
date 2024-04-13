# CroRIS tool

A tool for uploading publication entries to the [CroRIS](https://www.croris.hr/) database. The instructions below were tested on Ubuntu 20.04 but might also work on other Linux distributions. The tool has been derived from an older [CROSBI tool](https://gitlab.cern.ch/CMS-IRB/crosbi) which is no longer in use.

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

### Getting the list of publications

1. Go to the [Inspire HEP](https://inspirehep.net) database

2. Get the list of publications by using the following command

```
find a brigljevic, v and cn cms and jy 2023 and ps p
```

where the author (`a`), the collaboration name (`cn`) and the journal year (`jy`) fields should be changed as appropriate.

Place the pointer above the "cite all" button and select BibTeX in the drop-down list as the output format. Save the output to `list_of_papers.bib`

Please note that the returned list of publications could contain errata published in 2023 for otherwise older publications. Please remove any publications for which the `year` field is older than 2023. In addition, check if there are any publications with more than one DOI string. These are typically the already-mentioned errata publications but it is nevertheless good to double-check the reason for more than one DOI string. A convenient way to get a quick overview of this type of information is to run the following two commands

```
cat list_of_papers.bib | grep -i year | grep -v 2023
cat list_of_papers.bib | grep -i doi
```

Either way, you will need to decide how to handle such publications, exclude them altogether or keep them but with just one DOI string (we generally do not upload errata publications).

3. Check that the content of [`configuration.py`](https://gitlab.cern.ch/CMS-IRB/CroRIS/blob/master/configuration.py) is correctly defined. Next, run the following command

```
python prepare_input.py -c cms -i list_of_papers.bib -o CroRIS_input.json |& tee prepare_input_`date "+%Y%m%d_%H%M%S"`.log
```

where the `-c` argument should be set as appropriate. For more information about the available command-line options, run

```
python prepare_input.py -h
```

**NOTE:** Piping the script output to the `tee` command will print it to the screen and save it in a log file containing a time stamp in its name.

In the above example `prepare_input.py` takes `list_of_papers.bib` as input, collects all the needed information and stores it in the `CroRIS_input.json` file.

The format of the output JSON file conforms to the specifications of the [CroRIS API](https://wiki.srce.hr/display/CRORIS/CROSBI+API).

## Importing publications to CroRIS

Send the output JSON file `CroRIS_input.json` to croris-app@srce.hr and system admins will take care of the import. In case the JSON would contain any publications that are already in the CroRIS database, those publications will be skipped during the import based on their DOI identifiers.

## Advanced options

### Linking publications with projects

To link project(s) to a specific publication, an additional `projects` field containing a comma-separated list of project CroRIS IDs needs to be added to that publication's entry in the input BibTeX file as shown in the following example

```
@article{CMS:2022suh,
    author = "Tumasyan, Armen and others",
    collaboration = "CMS",
    title = "{Search for a massive scalar resonance decaying to a light scalar and a Higgs boson in the four b quarks final state with boosted topology}",
    eprint = "2204.12413",
    archivePrefix = "arXiv",
    primaryClass = "hep-ex",
    reportNumber = "CMS-B2G-21-003, CERN-EP-2022-034",
    doi = "10.1016/j.physletb.2022.137392",
    journal = "Phys. Lett. B",
    volume = "842",
    pages = "137392",
    projects = "3419",
    year = "2023"
}
```
