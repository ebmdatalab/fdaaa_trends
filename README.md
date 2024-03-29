# Data Processing and Analysis Code for Results Reporting Trends on ClinicalTrials.gov under FDAAA 2007

![status](https://github.com/ebmdatalab/fdaaa_trends/workflows/Notebook%20checks/badge.svg)

## Overview

This repository contains everything you need to recreate our analysis published in [The Lancet](https://doi.org/10.1016/S0140-6736(19)33220-9). This code can also be easily adapted for future analyses of interest using ClinicalTrials.gov data.

## Data Sources

Each working day we download the full data from ClinicalTrials.gov as part of our [FDAAA TrialsTracker](https://fdaaa.trialstracker.net/) project. The data is [available in XML format](https://clinicaltrials.gov/ct2/resources/download) that we convert to JSON strings. We store these in CSV format, delimited by the `þ` character for ease of use with tools like BigQuery, however they are also able to be parsed as ndjson files. The code for that downloading and processing is located as part of our TrialsTracker ["clinicaltrials-act-converter" repo](https://github.com/ebmdatalab/clinicaltrials-act-converter). Additional code for the FDAAA TrialsTracker is located [here](https://github.com/ebmdatalab/clinicaltrials-act-tracker).

Adapting the code used to identify applicable trials for the TrialsTracker, we are able to take the raw data of the entirety of ClinicalTrials.gov on a given day and convert it to CSVs with the relevant data necessary for the analysis. Due to their size, the raw "CSV" files that inform this analysis are available separately in an open [OSF repository](https://doi.org/10.17605/OSF.IO/X8NBV). We are happy to freely share any additional full archives of ClinicalTrials.gov from our database. Please email us at [ebmdatalab@phc.ox.ac.uk](mailto:ebmdatalab@phc.ox.ac.uk) and we can discuss the best way to get you the data.

## Data Processing and Analysis

### *Raw Data Processing*

Each raw data file used for this analysis is processed using the code in the `Raw Data Processing` directory. This code takes one of our CSVs of JSON as an input and extracts the necessary data fields to identify ACTs/pACTs and any additional data needed for the analysis to a CSV. The processed data files for this analysis are available both in the `Processed CSVs` directory in the Data directory of this repository as well as our [OSF](https://doi.org/10.17605/OSF.IO/X8NBV) page.

### *STATA Analysis*

Similarly, the `STATA Analysis` directory contains separate processing code that extracts only the data necessary for the statistical analysis conducted in STATA along with our .do file and additional STATA output and log files.

### *notebooks*

The `notebooks` directory contains all the remaining primary analysis code and results for this project in the `FDAAA Trends Noteboook - Final.ipynb` notebook.

### *Figures*

All figures from the `FDAAA Trends Notebook - Final.ipynb` notebook are available in the `Figures` directory in vector (.svg and .eps) formats.

### *Peer Review Additions*

`Peer Review Additions` contains some additional statistics and analysis that were added to the paper at the request of peer reviewers.

### *lib*

The `lib` directory contains .py files with functions to import for the processing and analysis of the data including `lifelines_fix.py`  which cosmetically patches the `lifelines` module used for the survival analysis to better display at risk counts.

### *Data*

Files necessary for both the raw data processing and the overall analysis:

>`fdaaa_regulatory_snapshot.csv` is our archive of the old "is_fda_regulated" field from ClinicalTrials.gov used in our pACT identification logic. This data is taken from the 5 January 2017 archive of ClinicalTrials.gov available from the [Clinical Trials Transformation Initiative](https://aact.ctti-clinicaltrials.org/snapshots).

>`qa.csv` is our scrape of QC data used for QC data prior to it being made available in the public XML data.

>We also include a folder of the processsed CSV files `Processed CSVs` and a placeholder directory in which you can place the raw data from [here](https://doi.org/10.17605/OSF.IO/X8NBV)

Additional files and directories in the repository are for use with Docker as described below.

## How to view the notebooks and use the repository with Docker

The analysis Notebooks live in the `notebooks/` folder (with an `ipynb` extension). You can most easily view them [on nbviewer](https://nbviewer.jupyter.org/github/ebmdatalab/fdaaa_trends/tree/master/notebooks/), though looking at them in Github should also work.

The repository has also been set up to run in Docker to ensure a compatible environment. While the notebook should be able to run in the current directory without Docker (assuming the environment specified in `requirements.txt`) you can follow the directions in the `Developers.md` file to clone this repository and run any code of interest within a Docker container on your machine.

## How to cite

You can cite our Lancet paper for the methods and results of this analysis:

>DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet 2020; 395: 361–9.

Static DOI: [10.1016/S0140-6736(19)33220-9](https://doi.org/10.1016/S0140-6736(19)33220-9)

You can cite our code directly via Zenodo: 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3603491.svg)](https://doi.org/10.5281/zenodo.3603491)

Please note, the version of the repository at this DOI on Zenodo is the version as it stood at publication of the paper. All data and analysis code remains unchanged compared to this repository, however non-analysis portions of the code may have been updated or refactored, the structure of the directory may have changed, and Docker compatibility has been added.
