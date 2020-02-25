from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import json

def is_interventional(study_type):
    return study_type == 'Interventional'

def is_covered_phase(phase):
    return phase in ['Phase 1/Phase 2', 'Phase 2', 'Phase 2/Phase 3' , 'Phase 3', 'Phase 4', 'N/A']

def is_not_withdrawn(study_status):
    return study_status != 'Withdrawn'

def is_not_device_feasibility(primary_purpose):
    return primary_purpose != 'Device Feasibility'

def is_covered_intervention(intervention_type_list):
    covered_intervention_type = ['Drug','Device','Biological','Genetic','Radiation','Combination Product','Diagnostic Test']
    a_set = set(covered_intervention_type)
    b_set = set(intervention_type_list)
    if (a_set & b_set):
        return True
    else:
        return False

def is_fda_reg(fda_reg_drug, fda_reg_device):
    if fda_reg_drug == 'Yes' or fda_reg_device == 'Yes':
        return True
    else:
        return False

def is_old_fda_regulated(is_fda_regulated, fda_reg_drug, fda_reg_device):
    if ((fda_reg_drug is None and fda_reg_device is None) and
        is_fda_regulated is not False):
        return True
    else:
        return False

def has_us_loc(locs):
    us_locs = ['United States','American Samoa','Guam','Northern Mariana Islands','Puerto Rico','Virgin Islands (U.S.)']
    if locs:
        for us_loc in us_locs:
            if us_loc in locs:
                return True
    return False

def does_it_exist(data, x):
    try:
        data[x]
        return True
    except KeyError:
        return False

def dict_or_none(data, keys):
    for k in keys:
        try:
            data = data[k]
        except KeyError:
            return None
    return json.dumps(data)

def text_or_none(data, keys):
    for k in keys:
        try:
            data = data[k]
        except KeyError:
            return None
    return data

def variable_levels(data, level):  
    try:
        return data[level]['text']
    except TypeError:
        try: 
            return data[level]
        except KeyError:
            return None
    except KeyError:
        try: 
            return data[level]
        except KeyError:
            return None

def str_to_date(datestr):  
    is_defaulted_date = False
    if datestr is not None:   
        try:
            parsed_date = datetime.strptime(datestr, '%B %d, %Y').date()
        except ValueError:
            parsed_date = datetime.strptime(datestr, '%B %Y').date() + relativedelta(months=+1) - timedelta(days=1)
            is_defaulted_date = True
    else:
        parsed_date = None
    return (parsed_date, is_defaulted_date)

def convert_bools_to_ints(row):
    for k, v in row.items():
        if v is True:
            v = 1
            row[k] = v
        elif v is False:
            v = 0
            row[k] = v
    return row

def contains_int(intervention, int_list):
    if intervention in int_list:
        x = True
    else:
        x = False
    return x

def loc_counter(locs):
    us_locs = ['United States','American Samoa','Guam','Northern Mariana Islands','Puerto Rico','Virgin Islands (U.S.)']
    counter = 0
    if locs:
        for us_loc in us_locs:
            if us_loc in locs:
                counter += 1
    return counter