import csv

def fda_reg(path):
    fda_reg_dict = {}
    with open(path) as old_fda_reg:
        reader = csv.DictReader(old_fda_reg)
        for d in reader:
            fda_reg_dict[d['nct_id']] = d['is_fda_regulated']
    return fda_reg_dict

def get_data(path):
    with open(path, 'r') as ctgov:
        lines = ctgov.readlines()
        return lines