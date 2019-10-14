Raw data files available at: https://osf.io/x8nbv/?view_only=bb862b2519224d2b92d5f166d290103b

You process these using the "Raw Data Processing" directory. These then produce the processed CSVs. The processed CSVs used in this specific analysis are available in the "Processed CSVs" directory.

The "FDAAA Trends Noteboook - Final" notebook contains all the analysis for the paper conducted in Python.

The STATA Analysis directory contains code to prepare the raw data specifically for analysis in STATA as well as all STATA files for the analysis.

"fdaaa_regulatory_snapshot.csv" is our archive of the old "is_fda_regulated" field from ClinicalTrials.gov used in our pACT identificaiton logic.

"qa.csv" is our scrape of QC data used for QC data prior to it being made available in the public XML data.

"lifelines_fix.py" applied some cosmetic fixes to the Kaplan-Meier curves generated using the Lifelines Modules.

The "Programs" directory contains helper programs for processing and analyzing the data.
