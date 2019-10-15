# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from datetime import date
import pandas as pd
from time import time
import re
import os
from pathlib import Path
import sys

try:
    get_ipython
    from tqdm import tqdm_notebook as tqdm
    %load_ext autoreload
    %autoreload 2
except NameError:
    from tqdm import tqdm

cwd = os.getcwd()
parent = str(Path(cwd).parents[0])
sys.path.append(parent)
# -

from programs.data_functions import get_data
from programs.data_functions import fda_reg
from programs.final_df import make_dataframe

# +
#point to path of this included file as necessary
old_fda = 'fdaaa_regulatory_snapshot.csv'
fda_reg_dict = fda_reg(old_fda)

headers = ['nct_id', 'act_flag', 'included_pact_flag', 'results_due', 'has_results','pending_results', 'pending_data',
           'has_certificate', 'late_cert', 'certificate_date', 'primary_completion_date', 'completion_date',
           'available_completion_date', 'due_date', 'last_updated_date', 'results_first_submitted_date', 
           'results_submitted_date_qc', 'results_first_posted_date', 'first_results_submission_any', 'documents', 
           'sponsor', 'sponsor_type', 'phase', 'location', 'study_status', 'study_type', 'primary_purpose', 'fda_reg_drug', 
           'fda_reg_device', 'is_fda_regulated', 'discrep_date_status', 'defaulted_date', 'collaborators','start_date', 
           'used_primary_completion_date', 'defaulted_pcd_flag', 'defaulted_cd_flag']

# +
start_program = time()
scrape_dates = [date(2018,3,15), date(2018,4,16), date(2018,5,15), date(2018,6,15), date(2018,7,16), date(2018,8,13), 
                date(2018,9,14), date(2018,10,15), date(2018,11,15), date(2018,12,14), date(2019,1,15),
                date(2019,2,15), date(2019,3,15), date(2019,4,15), date(2019,5,15),date(2019,6,13), date(2019,7,15), 
                date(2019,8,15), date(2019,9,16)]


regexp = re.compile('\d{4}-\d{2}-\d{2}')

#These paths need to point to the raw ClinicalTrials.gov data for the relevant dates. These files are 3-4 GB in size and
#therefore cannot easily be shared. They are available at https://osf.io/x8nbv/?view_only=bb862b2519224d2b92d5f166d290103b
path = 'C:/Users/ndevito/Desktop/FDAAA Implementation Data/Raw JSON/'
files = os.listdir(path)
files.sort()

#removing hidden file when analysis is on a Mac
if '.DS_Store' in files:
    files.remove('.DS_Store')

file_number = 0
for file, scrape_date in zip(tqdm(files), scrape_dates):
    file_number += 1
    name = re.findall(regexp,file)[0]
    lines = get_data(os.path.join(path, file))
    df = make_dataframe(tqdm(lines), fda_reg_dict, headers, act_filter=False, scrape_date=scrape_date)
    df.to_csv('applicable_trials_' + name + '.csv')  
end_program = time()
print("This took {} Minutes to Run".format((end_program - start_program) / 60))
