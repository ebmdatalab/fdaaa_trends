import csv
import json
import pandas as pd
import numpy as np
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from time import time
from time import sleep
from io import StringIO

from lib.helper_functions import is_interventional
from lib.helper_functions import is_covered_phase
from lib.helper_functions import is_not_withdrawn
from lib.helper_functions import is_not_device_feasibility
from lib.helper_functions import is_covered_intervention
from lib.helper_functions import is_fda_reg
from lib.helper_functions import is_old_fda_regulated
from lib.helper_functions import has_us_loc
from lib.helper_functions import does_it_exist
from lib.helper_functions import dict_or_none
from lib.helper_functions import text_or_none
from lib.helper_functions import variable_levels
from lib.helper_functions import str_to_date
from lib.helper_functions import convert_bools_to_ints

def make_row(jcs, fda_reg_dict, scrape_date=date.today()):
    effective_date = date(2017, 1, 18)
    scrape_date = scrape_date
    td = {}
    td['nct_id'] = text_or_none(jcs, ['id_info','nct_id'])
    
    #Everything you need for ACT/PACT Selection and Results Due and Reporting Starts here:
    td['study_type'] = text_or_none(jcs, ['study_type'])
    td['has_certificate'] = does_it_exist(jcs, 'disposition_first_submitted')
    td['phase'] = text_or_none(jcs,['phase'])
    td['fda_reg_drug'] = text_or_none(jcs,['oversight_info', 'is_fda_regulated_drug'])
    td['fda_reg_device'] = text_or_none(jcs,['oversight_info', 'is_fda_regulated_device'])
    td['primary_purpose'] = text_or_none(jcs, ['study_design_info','primary_purpose'])

    try:
        if fda_reg_dict[td['nct_id']] == 'false':
            td['is_fda_regulated'] = False
        elif fda_reg_dict[td['nct_id']] == 'true':
            td['is_fda_regulated'] = True
        else:
            td['is_fda_regulated'] = None
    except KeyError:
        td['is_fda_regulated'] = None

    td['study_status'] = text_or_none(jcs, ['overall_status'])
    td['start_date'] = str_to_date(variable_levels(jcs, 'start_date'))[0]
    td['primary_completion_date'], td['defaulted_pcd_flag'] = str_to_date(variable_levels(jcs, 'primary_completion_date'))
    td['completion_date'], td['defaulted_cd_flag'] = str_to_date(variable_levels(jcs, 'completion_date'))

    if not td['primary_completion_date'] and not td['completion_date']:
        td['available_completion_date'] = None
    elif td['completion_date'] and not td['primary_completion_date']:
        td['available_completion_date'] = td['completion_date']
        td['used_primary_completion_date'] = False
    else:
        td['available_completion_date'] = td['primary_completion_date']
        td['used_primary_completion_date'] = True

    if (
        is_interventional(td["study_type"])
        and is_fda_reg(td["fda_reg_drug"], td["fda_reg_device"])
        and is_covered_phase(td["phase"])
        and is_not_device_feasibility(td["primary_purpose"])
        and td["start_date"]
        and td["start_date"] >= effective_date
        and is_not_withdrawn(td["study_status"])
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
        is_interventional(td["study_type"])
        and is_covered_intervention(trial_intervention_types)
        and is_covered_phase(td["phase"])
        and is_not_device_feasibility(td["primary_purpose"])
        and td["available_completion_date"]
        and td["available_completion_date"] >= effective_date
        and td["start_date"]
        and td["start_date"] < effective_date
        and is_not_withdrawn(td["study_status"])
        and (
            is_fda_reg(td["fda_reg_drug"], td["fda_reg_device"])
            or is_old_fda_regulated(
                td["is_fda_regulated"], td["fda_reg_drug"], td["fda_reg_device"]
            )
        )
        and has_us_loc(locs)
    ):
        old_pact_flag = True
    else:
        old_pact_flag = False

    if (
        is_interventional(td["study_type"])
        and is_fda_reg(td["fda_reg_drug"], td["fda_reg_device"])
        and is_covered_phase(td["phase"])
        and is_not_device_feasibility(td["primary_purpose"])
        and td["start_date"]
        and td["start_date"] < effective_date
        and td["available_completion_date"]
        and td["available_completion_date"] >= effective_date
        and is_not_withdrawn(td["study_status"])
    ):
        new_pact_flag = True
    else:
        new_pact_flag = False

    if old_pact_flag == True or new_pact_flag == True:
        td["included_pact_flag"] = True
    else:
        td["included_pact_flag"] = False

    td["location"] = dict_or_none(jcs, ["location_countries"])

    td["has_results"] = does_it_exist(jcs, 'results_first_submitted')

    td["pending_results"] = does_it_exist(jcs, 'pending_results')

    td["pending_data"] = dict_or_none(jcs, ["pending_results"])

    if td["pending_data"]:
        x = json.loads(td["pending_data"])
        if isinstance(x['submitted'], list):
            first_submitted_pending = datetime.strptime(x['submitted'][0], '%B %d, %Y').date()
        else:
            first_submitted_pending = datetime.strptime(x['submitted'], '%B %d, %Y').date()
    else:
        first_submitted_pending = None

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
            td["has_certificate"] == 0
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
    
    td['documents'] = dict_or_none(jcs, ['provided_document_section', 'provided_document'])

    td['results_first_submitted_date'] = str_to_date(variable_levels(jcs, 'results_first_submitted'))[0]
    
    td['results_submitted_date_qc'] = str_to_date(variable_levels(jcs, 'results_first_submitted_qc'))[0]
    
    td['results_first_posted_date'] = str_to_date(variable_levels(jcs, 'results_first_posted'))[0]

    if td["pending_data"]:
        td['first_results_submission_any'] = first_submitted_pending
    elif td['results_first_submitted_date']:
        td['first_results_submission_any'] = td['results_first_submitted_date']
    else:
        td['first_results_submission_any'] = None  

    td["last_updated_date"] = str_to_date(jcs['last_update_submitted'])[0]

    td["certificate_date"] = str_to_date(variable_levels(jcs, 'disposition_first_submitted'))[0]

    if (
        td["certificate_date"] is not None
        and td["available_completion_date"] is not None
    ):
        if td["certificate_date"] > (
            td["available_completion_date"] + relativedelta(years=1)
        ):
            td["late_cert"] = True
        else:
            td["late_cert"] = False
    else:
        td["late_cert"] = False
        
    if does_it_exist(jcs, 'sponsors'):
        td['sponsor'] = text_or_none(jcs, ['sponsors','lead_sponsor','agency'])
        td['sponsor_type'] = text_or_none(jcs, ['sponsors','lead_sponsor','agency_class'])
    else:
        td["sponsor"] = td["sponsor_type"] = None
    

    td["collaborators"] = dict_or_none(jcs, ["sponsors", "collaborator"])

    not_ongoing = [
        "Unknown status",
        "Active, not recruiting",
        "Not yet recruiting",
        "Enrolling by invitation",
        "Suspended",
        "Recruiting",
    ]
    if (
        (td['primary_completion_date'] is None or td['primary_completion_date'] < scrape_date)
        and td['completion_date'] is not None
        and td['completion_date'] < scrape_date
        and td["study_status"] in not_ongoing
    ):
        td["discrep_date_status"] = True
    else:
        td["discrep_date_status"] = False

    if (
        td.get("used_primary_completion_date", False)
        and td.get("defaulted_pcd_flag", False)
    ) or (
        not td.get("used_primary_completion_date", False)
        and td.get("defaulted_cd_flag", False)
    ):
        td["defaulted_date"] = True
    else:
        td["defaulted_date"] = False
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