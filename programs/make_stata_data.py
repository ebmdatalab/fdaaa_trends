import csv
import json
import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from datetime import datetime
from time import time
from time import sleep
from io import StringIO

from programs.helper_functions import is_interventional
from programs.helper_functions import is_covered_phase
from programs.helper_functions import is_not_withdrawn
from programs.helper_functions import is_not_device_feasibility
from programs.helper_functions import is_covered_intervention
from programs.helper_functions import is_fda_reg
from programs.helper_functions import is_old_fda_regulated
from programs.helper_functions import has_us_loc
from programs.helper_functions import does_it_exist
from programs.helper_functions import dict_or_none
from programs.helper_functions import text_or_none
from programs.helper_functions import variable_levels
from programs.helper_functions import str_to_date
from programs.helper_functions import convert_bools_to_ints
from programs.helper_functions import contains_int
from programs.helper_functions import loc_counter

def make_row(jcs, fda_reg_dict, scrape_date=date.today()):
    effective_date = date(2017, 1, 18)
    scrape_date = scrape_date
    td = {}
    
    td['nct_id'] = text_or_none(jcs, ['id_info','nct_id'])
    
    #Everything you need for ACT/PACT Selection and Results Due and Reporting Starts here:
    study_type = text_or_none(jcs, ['study_type'])
    has_certificate = does_it_exist(jcs, 'disposition_first_submitted')
    td['phase'] = text_or_none(jcs,['phase'])
    fda_reg_drug = text_or_none(jcs,['oversight_info', 'is_fda_regulated_drug'])
    fda_reg_device = text_or_none(jcs,['oversight_info', 'is_fda_regulated_device'])
    primary_purpose = text_or_none(jcs, ['study_design_info','primary_purpose'])

    try:
        if fda_reg_dict[td['nct_id']] == 'false':
            is_fda_regulated = False
        elif fda_reg_dict[td['nct_id']] == 'true':
            is_fda_regulated  = True
        else:
            is_fda_regulated  = None
    except KeyError:
        is_fda_regulated = None

    study_status = text_or_none(jcs, ['overall_status'])
    start_date = str_to_date(variable_levels(jcs, 'start_date'))[0]
    primary_completion_date, defaulted_pcd_flag = str_to_date(variable_levels(jcs, 'primary_completion_date'))
    completion_date, defaulted_cd_flag = str_to_date(variable_levels(jcs, 'completion_date'))

    if not primary_completion_date and not completion_date:
        td['available_completion_date'] = None
    elif completion_date and not primary_completion_date:
        td['available_completion_date'] = completion_date
    else:
        td['available_completion_date'] = primary_completion_date

    if (
        is_interventional(study_type)
        and is_fda_reg(fda_reg_drug, fda_reg_device)
        and is_covered_phase(td["phase"])
        and is_not_device_feasibility(primary_purpose)
        and start_date
        and start_date >= effective_date
        and is_not_withdrawn(study_status)
    ):
        td["act_flag"] = True
    else:
        td["act_flag"] = False

    trial_intervention_types = []
    try:
        if isinstance(jcs['intervention'], list):
            for j in jcs['intervention']:
                trial_intervention_types.append(j['intervention_type'])
        else:
            trial_intervention_types.append(jcs['intervention']['intervention_type'])
    except KeyError:
        trial_intervention_types = []

    try:
        locs = jcs['location_countries']['country']
    except KeyError:
        locs = None

    if (
        is_interventional(study_type)
        and is_covered_intervention(trial_intervention_types)
        and is_covered_phase(td["phase"])
        and is_not_device_feasibility(primary_purpose)
        and td["available_completion_date"]
        and td["available_completion_date"] >= effective_date
        and start_date
        and start_date < effective_date
        and is_not_withdrawn(study_status)
        and (
            is_fda_reg(fda_reg_drug, fda_reg_device)
            or is_old_fda_regulated(
                is_fda_regulated, fda_reg_drug, fda_reg_device
            )
        )
        and has_us_loc(locs)
    ):
        old_pact_flag = True
    else:
        old_pact_flag = False

    if (
        is_interventional(study_type)
        and is_fda_reg(fda_reg_drug, fda_reg_device)
        and is_covered_phase(td["phase"])
        and is_not_device_feasibility(primary_purpose)
        and start_date
        and start_date < effective_date
        and td["available_completion_date"]
        and td["available_completion_date"] >= effective_date
        and is_not_withdrawn(study_status)
    ):
        new_pact_flag = True
    else:
        new_pact_flag = False

    if old_pact_flag == True or new_pact_flag == True:
        td["included_pact_flag"] = True
    else:
        td["included_pact_flag"] = False

    location = dict_or_none(jcs, ["location_countries"])

    td["has_results"] = does_it_exist(jcs, 'results_first_submitted')

    td["pending_results"] = does_it_exist(jcs, 'pending_results')
    
    td['any_results'] = td["has_results"] or td["pending_results"]

    pending_data = dict_or_none(jcs, ["pending_results"])
    
    if pending_data:
        x = json.loads(pending_data)
        if isinstance(x['submitted'], list):
            first_submitted_pending = datetime.strptime(x['submitted'][0], '%B %d, %Y').date()
        else:
            first_submitted_pending = datetime.strptime(x['submitted'], '%B %d, %Y').date()
    else:
        first_submitted_pending = None
    
    results_first_submitted_date = str_to_date(variable_levels(jcs, 'results_first_submitted'))[0]
        
    if pending_data:
        td['first_results_submission'] = first_submitted_pending
    elif results_first_submitted_date:
        td['first_results_submission'] = results_first_submitted_date
    else:
        td['first_results_submission'] = None   
    
    #official due date is at 1 year, however we do not officially call a trial due until 30 days late
    #this conservatively allows for any delays to the posting process
    #however for certain analyses, we need the actual due date
    if (td["act_flag"] == True or td["included_pact_flag"] == True):
        td['due_date'] = td["available_completion_date"] + relativedelta(years=1)
    else:
        td['due_date'] = None
    
    if (
        (td["act_flag"] == True or td["included_pact_flag"] == True)
        and scrape_date
        > td['due_date']
        and (
            has_certificate == 0
            or (
                scrape_date
                > td["available_completion_date"]
                + relativedelta(years=3)
                + timedelta(days=30)
            )
        )
    ):
        td["results_due"] = True
    else:
        td["results_due"] = False
    ###And ends here    
    
    if not td['any_results'] and td['results_due']:
        td['overdue'] = True
    else:
        td['overdue'] = False
    
    if td['first_results_submission'] and td['due_date'] and td['first_results_submission'] > td['due_date']:
        td['reported_late'] = True
    else:
        td['reported_late'] = False
            
    if does_it_exist(jcs, 'sponsors'):
        td['sponsor'] = text_or_none(jcs, ['sponsors','lead_sponsor','agency'])
        td['sponsor_type'] = text_or_none(jcs, ['sponsors','lead_sponsor','agency_class'])
    else:
        td["sponsor"] = td["sponsor_type"] = None
    
    if td['sponsor_type'] == 'Other':
        td['sponsor_class'] = 0
    elif td['sponsor_type'] == 'Industry':
        td['sponsor_class'] = 1
    elif td['sponsor_type'] == 'U.S. Fed' or td['sponsor_type'] == 'NIH':
        td['sponsor_class'] = 2
    else:
        td['sponsor_class'] = 3
    
    collaborators = dict_or_none(jcs, ["sponsors", "collaborator"])
    gov = ['"agency_class": "NIH"', '"agency_class": "U.S. Fed"']
    if collaborators and any(x in collaborators for x in gov):
        td['us_gov_collab'] = True
    else:
        td['us_gov_collab'] = False
    
    if collaborators and '"agency_class": "Industry"' in collaborators:
        td['industry_collab'] = True
    else:
        td['industry_collab'] = False
    
    if td['phase'] == "Phase 1/Phase 2":
        td['phase_cat'] = 0
    elif td['phase'] == "Phase 2":
        td['phase_cat'] = 1
    elif td['phase'] == "Phase 2/Phase 3":
        td['phase_cat'] = 2
    elif td['phase'] == "Phase 3":
        td['phase_cat'] = 3
    elif td['phase'] == "Phase 4":
        td['phase_cat'] = 4
    elif td['phase'] == "N/A":
        td['phase_cat'] = 5
    else:
        td['phase_cat'] = None
    
    if study_status == 'Terminated':
        td['terminated'] = True
    else:
        td['terminated'] = False
    
    if start_date:
        td['start_year'] = start_date.year
    else:
        td['start_year'] = None
        
    if completion_date and completion_date < scrape_date:
        td['full_completion'] = True
    else:
        td['full_completion'] = False
    
    td['contains_drug'] = contains_int('Drug', trial_intervention_types)
    
    td['contains_biological'] = contains_int('Biological', trial_intervention_types)
    
    td['contains_device'] = contains_int('Device', trial_intervention_types)
    
    td['contains_diagnostic'] = contains_int('Diagnostic Test', trial_intervention_types)
    
    td['contains_radiation'] = contains_int('Radiation', trial_intervention_types)
    
    td['contains_combi_product'] = contains_int('Combination Product', trial_intervention_types)
    
    td['contains_genetic'] = contains_int('Genetic', trial_intervention_types)
    
    if isinstance(locs, list):
        locs = locs
    elif isinstance(locs, str):
        locs = [locs]

    if has_us_loc(locs) and len(locs) == loc_counter(locs):
        td['contains_us_loc'] = 0
    elif has_us_loc(locs) and len(locs) != loc_counter(locs):
        td['contains_us_loc'] = 1
    elif locs and not has_us_loc(locs):
        td['contains_us_loc'] = 2
    elif not locs:
        td['contains_us_loc'] = 3
        
    return td

def make_dataframe(lines, fda_reg_dict, headers, act_filter=False, scrape_date=date.today()):
    fda_reg_dict = fda_reg_dict
    writer_time = time()
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    c = 0
    sleep(1)
    for line in lines:
        c+=1
        j = json.loads(line)
        jcs = j['clinical_study']
        td = make_row(jcs, fda_reg_dict, scrape_date)
        if act_filter == True:
            if td["act_flag"] or td["included_pact_flag"]:
                writer.writerow(convert_bools_to_ints(td))
        elif act_filter == False:
            writer.writerow(convert_bools_to_ints(td))
        trial_time = time() - writer_time
    output.seek(0)
    elapsed_time = time() - writer_time
    df = pd.read_csv(output)
    print("Finished. {} Trials Processed; Ran in {} Minutes".format(len(df), round(elapsed_time/60.0)))
    return df