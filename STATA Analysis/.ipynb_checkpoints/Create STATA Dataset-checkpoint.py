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
import pandas as pd
from datetime import date
import os
import sys
from pathlib import Path

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

# +
from programs.data_functions import fda_reg
from programs.data_functions import get_data

old_fda = 'C:/Users/ndevito/Dropbox/Python projects/FDAAA Projects/FDAAA Trends Paper/fdaaa_regulatory_snapshot.csv'
path = 'C:/Users/ndevito/Desktop/FDAAA Implementation Data/Raw JSON/clinicaltrials_raw_clincialtrials_json_2019-09-16.csv'

fda_reg_dict = fda_reg(old_fda)
lines = get_data(path)

headers = ['nct_id', 'results_due', 'has_results', 'pending_results', 'any_results', 'overdue', 'reported_late',
          'available_completion_date', 'due_date', 'first_results_submission', 'sponsor', 'sponsor_type', 'sponsor_class', 
          'industry_collab', 'us_gov_collab', 'phase_cat', 'phase', 'terminated', 'start_year', 'full_completion',
          'contains_drug', 'contains_biological', 'contains_device', 'contains_diagnostic', 'contains_radiation',
          'contains_combi_product', 'contains_genetic', 'contains_us_loc', 'act_flag', 'included_pact_flag']
# -

from programs.make_stata_data import make_row
from programs.make_stata_data import make_dataframe

df = make_dataframe(tqdm(lines), fda_reg_dict, headers, act_filter = False, scrape_date = date(2019,9,16))

group = df[['nct_id', 'sponsor']].groupby('sponsor', as_index = False).count()
group.columns = ['sponsor', 'sponsored_trials']
merged = df.merge(group, how='left', on='sponsor')

final_df = merged[(merged.act_flag == 1) | (merged.included_pact_flag == 1)].reset_index(drop=True)

final_df.to_csv('fdaaa_stata_dataset.csv', index=False)


