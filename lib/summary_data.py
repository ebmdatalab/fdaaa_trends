import pandas as pd
from datetime import date

def get_summary_data(df, scrape_date, grouped):
    if scrape_date <= date(2018,5,11):
        when_submitted = grouped[grouped['submitted_to_regulator'] <= pd.Timestamp(scrape_date)]
        merged = df.merge(when_submitted, left_on = 'nct_id', right_on = 'registry_id', how='left')
        denominator = len(merged[merged.results_due == 1])
        num_df = merged[(merged.results_due == 1) & ((merged.has_results == 1) | (merged.submitted_to_regulator.notnull()))]
        numerator = len(num_df)
        number_on_time = len(num_df[(num_df.due_date > num_df.results_first_submitted_date) | (num_df.due_date > num_df.submitted_to_regulator)])
    elif scrape_date > date(2018,5,11):
        denominator = len(df[df.results_due == 1])
        num_df = df[(df.results_due == 1) & ((df.has_results ==1) | (df.pending_results ==1))]
        numerator = len(num_df)
        number_on_time = len(num_df[(num_df.due_date >= num_df.first_results_submission_any)])
    return numerator, denominator, number_on_time