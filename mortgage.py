"""Calculate my mortgage

Usage: mortgage.py [--filename=<str>]
       mortgage.py [--help | --version]

Options:
  -h --help                           Show this screen.
  --filename=<str>                    Where to get data from [default: inputs.yml]

"""

import re
import os
import yaml
import decimal
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from docopt import docopt
from matplotlib.pylab import rcParams
from datetime import datetime, timedelta
from collections import OrderedDict
from dateutil.relativedelta import relativedelta

MONTHS_IN_YEAR = 12

__version__ = '0.1'

args = docopt(__doc__, options_first=True, version=__version__)

def add_time_to_market(dict_time_series, planned_mortgages, idx, start_timestamp):
    last_timestamp = (start_timestamp - relativedelta(months=1))strftime('%m-%Y')


def get_past_mortgage_rents(planned_mortgages, idx):
    rent = 0
    for mortgage in planned_mortgages[0:idx-1]:
        rent += (mortgage['monthly_rent'] - (mortgage['monthly_rent'] - mortgage['invoices_and_taxes'] / MONTHS_IN_YEAR)
    return rent


def get_sorted_dates_datetime_dict(dictionary, date_format = '%m-%Y'):
    dates = [datetime.strptime(ts, date_format) for ts in dictionary.keys()]
    dates.sort()
    sorteddates = [datetime.strftime(ts, date_format) for ts in dates]
    return sorteddates

def generate_time_series(months, start_dt = datetime.now() + relativedelta(months=1)):
    dates = [start_dt.strftime('%d-%m-%y'), (start_dt + relativedelta(months=months)).strftime('%d-%m-%y')]
    start, end = [datetime.strptime(_, "%d-%m-%y") for _ in dates]
    return OrderedDict(((start + timedelta(_)).strftime(r"%m-%Y"), None) for _ in xrange((end - start).days)).keys()

def calculate_when_first_mortgage(planned_mortgage, initial_savings,
                                  monthly_net_salary,
                                  savings_no_mortgage):
    current_money = initial_savings
    statuses = []
    months = 0

    while current_money < ( planned_mortgage['cost'] * (100 - planned_mortgage['mortgage_percent']) / 100 ) +\
                            planned_mortgage['set_up_cost'] + planned_mortgage['conditioning'] + planned_mortgage['leftover'] :
        current_money += ( monthly_net_salary * savings_no_mortgage / 100 )
        statuses.append(current_money)
        months += 1

    statuses[-1] = statuses[-1] - (planned_mortgage['cost'] *\
                   (100 - planned_mortgage['mortgage_percent']) / 100) -\
                   planned_mortgage['set_up_cost'] - planned_mortgage['conditioning']

    return generate_time_series(months), statuses, (datetime.now() + relativedelta(months=months)).strftime('%d-%m-%y')

def run_mortgage(dict_time_series, planned_mortgages, monthly_net_salary, idx, vacancy_unemployment_roundup):
    start_timestamp = datetime.strptime(get_sorted_dates_datetime_dict(dict_time_series)[-1], '%m-%Y') + relativedelta(months=1)
    add_time_to_market(dict_time_series, planned_mortgages, idx, start_timestamp, monthly_net_salary, vacancy_unemployment_roundup)
    start_timestamp += relativedelta(months=planned_mortgages[idx]['time_to_market_months'])

    base_income = (monthly_net_salary*vacancy_unemployment_roundup)/100 + get_past_mortgage_rents(planned_mortgages, idx)
    import ipdb;ipdb.set_trace()

rcParams['figure.figsize'] = 15, 6
stream = open(args['--filename'], 'r')

try:
    dict_time_series = {}
    input_yml = yaml.load(stream)
    planned_mortgages = input_yml['planned_mortgages']

    if len(planned_mortgages) < 1:
        raise Exception("No mortgages found")

    initial_savings =  input_yml['initial_savings']
    monthly_net_salary =  input_yml['monthly_net_salary']
    recurring_monthly_costs = input_yml['recurring_monthly_costs']
    vacancy_unemployment_roundup = input_yml['vacancy_unemployment_roundup']

    mortgage_downpayment_percent = input_yml['mortgage_downpayment_percent']
    mortgage_savings_percent = input_yml['mortgage_savings_percent']

    rental_downpayment_percent = input_yml['rental_downpayment_percent']
    rental_savings_percent = input_yml['rental_downpayment_percent']
    savings_no_mortgage = input_yml['savings_no_mortgage']

    monthly_series_no_mortgage,statuses,date_first_mortgage  = calculate_when_first_mortgage(
                                                                 planned_mortgages[0],
                                                                 initial_savings,
                                                                 (monthly_net_salary*vacancy_unemployment_roundup)/100,
                                                                 savings_no_mortgage)

    spendability_first = ((monthly_net_salary*vacancy_unemployment_roundup)/100) - (monthly_net_salary * savings_no_mortgage / 100) - recurring_monthly_costs
    dict_time_series = dict(zip(monthly_series_no_mortgage, statuses))

    for idx, mortgage in enumerate(planned_mortgages):
        run_mortgage(dict_time_series, planned_mortgages, monthly_net_salary, idx, vacancy_unemployment_roundup)


    print("Spendability during waiting for 1st mortgage: {}".format(spendability_first))
    print("You can buy your 1st flat on: {}".format(date_first_mortgage))



except yaml.YAMLError as exc:
    print(exc)
