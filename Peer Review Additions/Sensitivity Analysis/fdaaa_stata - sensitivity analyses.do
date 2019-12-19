*housekeeping
clear all
cd "C:\Users\ndevito\Dropbox\Python projects\FDAAA Projects\FDAAA Trends Paper\STATA Analysis"
set more off
capture log using output_for_tables, replace

import delimited "fdaaa_stata_dataset.csv"

cd "C:\Users\ndevito\Dropbox\Python projects\FDAAA Projects\FDAAA Trends Paper\Peer Review Additions\Sensitivity Analysis"
save bigworking, replace

use bigworking

* labels
label define noyes 0 "no" 1 "yes"
label values results_due noyes
label values any_results noyes
label values overdue noyes
label values reported_late noyes
label values industry_collab noyes
label values us_gov_collab noyes
label values terminated noyes
label values full_completion noyes
label values contains_drug noyes
label values contains_biological noyes
label values contains_device noyes
label values contains_diagnostic noyes
label values contains_radiation noyes
label values contains_combi_product noyes
label values contains_genetic noyes
label define sponsorclasslabels 0 "noncommercial" 1 "commercial" 2 "us_gov"
label values sponsor_class sponsorclasslabels
label define phaselabels 0 "Phase 1/2" 1 "Phase 2" 2 "Phase 2/3" 3 "Phase 3" 4 "Phase 4" 5 "N/A"
label values phase_cat phaselabels
label define usloclabels 0 "US-Only" 1 "US and Other" 2 "No US Location" 3 "No Location Provided"
label values contains_us_loc usloclabels

gen compliant = 0
replace compliant = 1 if results_due == 1 & any_results == 1 & reported_late == 0
label values compliant noyes

*creating out ACT variable for sensitivity analyses
gen act = 0
replace act = 1 if act_flag == 1
label values act noyes

* identify trials done by institutions that do a lot of trials
sort sponsored_trials
xtile quartile = sponsored_trials, nq(4)
bysort quartile: summ sponsored_trials

save working, replace

* YOU NOW HAVE A DATASET READY TO DESCRIBE
 
* Creating Analysis Dataset
* This dataset contains all trials identified as covered under the FDAAA 2007, due or not
count

* keep only trials where results are due
keep if results_due==1
count
save duecohort, replace

*safety net to make sure you now reload data!
clear all

* Now the tables
clear all
use duecohort

count

* getting count of ACTs/pACTs
tab compliant
tab any_results
tab act

* results % - getting compliance and reporting by ACTs/pACTs
tab compliant, missing
proportion compliant, missing cformat(%5.3f) 

tab act compliant
proportion compliant, over(act) missing cformat(%5.3f)

tab any_results, missing
proportion any_results, missing cformat(%5.3f) 

tab act any_results
proportion any_results, over(act) missing cformat(%5.3f)


* logistic regression - doing crude and adjusted regression with
*ACT/pACT as a variable in the model

logistic compliant i.act

logistic compliant start_year i.sponsor_class i.industry_collab i.us_gov_collab ib3.phase_cat i.terminated i.full_completion i.contains_drug i.contains_biological i.contains_device i.contains_diagnostic i.contains_radiation i.contains_combi_product i.contains_genetic i.contains_us_loc i.quartile i.act, allbaselevels

logistic any_results i.act

logistic any_results start_year i.sponsor_class i.industry_collab i.us_gov_collab ib3.phase_cat i.terminated i.full_completion i.contains_drug i.contains_biological i.contains_device i.contains_diagnostic i.contains_radiation i.contains_combi_product i.contains_genetic i.contains_us_loc i.quartile i.act, allbaselevels

*now creating a dataset of just due ACTs
keep if act==1
count
save actduecohort, replace

*safety net to make sure you now reload data!
clear all

use actduecohort

count

*  Counts for the ACT only cohort
tab compliant
tab any_results
tab sponsor_class
tab industry_collab
tab us_gov_collab
tab phase_cat
tab terminated
tab start_year
tab full_completion
tab contains_drug
tab contains_biological
tab contains_device
tab contains_diagnostic
tab contains_radiation
tab contains_combi_product
tab contains_genetic
tab contains_us_loc
tab quartile

* ACT only cohort tabs
tab compliant, missing
proportion compliant, missing cformat(%5.3f) 

tab start_year compliant
proportion compliant, over(start_year) missing cformat(%5.3f) 
tab sponsor_class compliant
proportion compliant, over(sponsor_class) missing cformat(%5.3f) 
tab industry_collab compliant
proportion compliant, over(industry_collab) missing cformat(%5.3f) 
tab us_gov_collab compliant
proportion compliant, over(us_gov_collab) missing cformat(%5.3f) 
tab phase_cat compliant
proportion compliant, over(phase_cat) missing cformat(%5.3f) 
tab terminated compliant
proportion compliant, over(terminated) missing cformat(%5.3f)
tab full_completion compliant
proportion compliant, over(full_completion) missing cformat(%5.3f)
tab contains_drug compliant
proportion compliant, over(contains_drug) missing cformat(%5.3f)
tab contains_biological compliant
proportion compliant, over(contains_biological) missing cformat(%5.3f)
tab contains_device compliant
proportion compliant, over(contains_device) missing cformat(%5.3f)
tab contains_diagnostic compliant
proportion compliant, over(contains_diagnostic) missing cformat(%5.3f)
tab contains_radiation compliant
proportion compliant, over(contains_radiation) missing cformat(%5.3f)
tab contains_combi_product compliant
proportion compliant, over(contains_combi_product) missing cformat(%5.3f)
tab contains_genetic compliant
proportion compliant, over(contains_genetic) missing cformat(%5.3f)
tab contains_us_loc compliant
proportion compliant, over(contains_us_loc) missing cformat(%5.3f)
tab quartile compliant
proportion compliant, over(quartile) missing cformat(%5.3f)

tab any_results, missing
proportion any_results, missing cformat(%5.3f) 

tab start_year any_results
proportion any_results, over(start_year) missing cformat(%5.3f) 
tab sponsor_class any_results
proportion any_results, over(sponsor_class) missing cformat(%5.3f) 
tab industry_collab any_results
proportion any_results, over(industry_collab) missing cformat(%5.3f) 
tab us_gov_collab any_results
proportion any_results, over(us_gov_collab) missing cformat(%5.3f) 
tab phase_cat any_results
proportion any_results, over(phase_cat) missing cformat(%5.3f) 
tab terminated any_results
proportion any_results, over(terminated) missing cformat(%5.3f)
tab full_completion any_results
proportion any_results, over(full_completion) missing cformat(%5.3f)
tab contains_drug any_results
proportion any_results, over(contains_drug) missing cformat(%5.3f)
tab contains_biological any_results
proportion any_results, over(contains_biological) missing cformat(%5.3f)
tab contains_device any_results
proportion any_results, over(contains_device) missing cformat(%5.3f)
tab contains_diagnostic any_results
proportion any_results, over(contains_diagnostic) missing cformat(%5.3f)
tab contains_radiation any_results
proportion any_results, over(contains_radiation) missing cformat(%5.3f)
tab contains_combi_product any_results
proportion any_results, over(contains_combi_product) missing cformat(%5.3f)
tab contains_genetic any_results
proportion any_results, over(contains_genetic) missing cformat(%5.3f)
tab contains_us_loc any_results
proportion any_results, over(contains_us_loc) missing cformat(%5.3f)
tab quartile any_results
proportion any_results, over(quartile) missing cformat(%5.3f)

* Act only logistic regression
*regress!
logistic compliant start_year
logistic compliant i.sponsor_class
logistic compliant i.industry_collab
logistic compliant i.us_gov_collab
logistic compliant ib3.phase_cat
logistic compliant i.terminated
logistic compliant i.full_completion
logistic compliant i.contains_drug
logistic compliant i.contains_biological
logistic compliant i.contains_device
logistic compliant i.contains_diagnostic
logistic compliant i.contains_radiation
logistic compliant i.contains_combi_product
logistic compliant i.contains_genetic
logistic compliant i.contains_us_loc
logistic compliant i.quartile
logistic compliant start_year i.sponsor_class i.industry_collab i.us_gov_collab ib3.phase_cat i.terminated i.full_completion i.contains_drug i.contains_biological i.contains_device i.contains_diagnostic i.contains_radiation i.contains_combi_product i.contains_genetic i.contains_us_loc i.quartile, allbaselevels

logistic any_results start_year
logistic any_results i.sponsor_class
logistic any_results i.industry_collab
logistic any_results i.us_gov_collab
logistic any_results ib3.phase_cat
logistic any_results i.terminated
logistic any_results i.full_completion
logistic any_results i.contains_drug
logistic any_results i.contains_biological
logistic any_results i.contains_device
logistic any_results i.contains_diagnostic
logistic any_results i.contains_radiation
logistic any_results i.contains_combi_product
logistic any_results i.contains_genetic
logistic any_results i.contains_us_loc
logistic any_results i.quartile
logistic any_results start_year i.sponsor_class i.industry_collab i.us_gov_collab ib3.phase_cat i.terminated i.full_completion i.contains_drug i.contains_biological i.contains_device i.contains_diagnostic i.contains_radiation i.contains_combi_product i.contains_genetic i.contains_us_loc i.quartile, allbaselevels
