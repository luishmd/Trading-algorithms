# Metadata
#=========
__author__ = 'Luis Domingues'

# Description
#============
# Library that provides general operations

# Notes
#======
#

# Known issues/enhancements
#==========================
#

#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import sys
import bisect as bisect
import datetime
import pandas as pd



#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def append_list(list_main, list_append):
    """
    Function that appends a list to another list
    """
    for element in list_append:
        list_main.append(element)
    return list_main


def convert_list_to_set(input_list):
    """
    Function that converts a list to a set. The return type is a list
    """
    output = list(set(input_list))
    return output


def convert_list_to_lowercase(input_list):
    """
    Function that converts all elements in a list of strings to lower_case
    """
    output = [element.lower() for element in input_list]
    return output


def get_duplicates(input_list):
    """
    Function that returns the duplicates in input_list
    """
    duplicates = []
    input_set = convert_list_to_set(input_list)
    if len(input_list) != len(input_set):
        duplicates = list(set([x for x in input_list if input_list.count(x) > 1]))
    return duplicates


def get_list_difference(main_list, list_to_subtract):
    """
    Function that returns the list that is the difference between a main list and a list_to_subtract (result = main_list - list_to_subtract)
    """
    result = []
    for element in main_list:
        if not element in list_to_subtract:
            result.append(element)
    return result


def print2file(file_path):
    """
    Function that resets stdout to write to file
    """
    sys.stdout = open(file_path,"w")


def get_index_in_list(ordered_list, value):
    """
    Function that returns the index in the ordered_list of the element before value
    """
    index = bisect.bisect_left(ordered_list, value)
    return index


def get_last_date(dataset):
    """
    Function that returns a date object of the last date in the dataset
    :param dataset:
    :return date_obj:
    """
    return pd.to_datetime(dataset.tail(1).index).date


def get_first_date(dataset):
    """
    Function that returns a date object of the first date in the dataset
    :param dataset:
    :return date_obj:
    """
    return pd.to_datetime(dataset.head(1).index).date


def get_previous_date(dataset, date_obj):
    """
    Function that returns the previous date
    :param dataset, date_obj:
    :return date_obj:
    """
    try:
        return pd.to_datetime(dataset[:date_obj].tail(2).index).date
    except:
        print("Could not find previous day (%s) in dataset.")
        return None


def increment_date(dataset, current_date_obj, n_days=1):
    """
    Function that increments the current date
    :param dataset, current_date_obj:
    :return date_obj:
    """
    last_date = get_last_date(dataset)
    new_date = current_date_obj + datetime.timedelta(days=n_days)
    test = True
    while test and last_date - new_date >= datetime.timedelta(days=0):
        try:
            dataset[new_date] # try to access that element in the dataset. If element is not there it will cause a KeyError
            test = False
        except KeyError:
            new_date = new_date + datetime.timedelta(days=1)
    return new_date



def get_analysis_time_interval(dataset, start_date_obj=None, end_date_obj=None, last_n_points=None):
    try:
        if start_date_obj==None and last_n_points==None:
            start_date_obj = get_first_date(dataset)
        if start_date_obj==None and last_n_points != None:
            start_date_obj = dataset.tail(last_n_points).index.to_pydatetime()[0].date()
        if end_date_obj==None:
            if not check_validity(dataset, start_date_obj):
                start_date_obj = increment_date(dataset, start_date_obj)
            end_date_obj = get_last_date(dataset)
        return [start_date_obj, end_date_obj]
    except:
        print("Could not determine time start and end dates.")
        return None


def get_dataset_time_interval(dataset):
    start_date = get_first_date(dataset)
    end_date = get_last_date(dataset)
    return [start_date, end_date]


def check_validity(dataset, date_obj):
    valid = False
    try:
        dataset[date_obj] # try to access that element in the dataset. If element is not there it will cause a KeyError
        valid = True
    except KeyError:
        pass
    return valid



def has_crossed(fast_older_val, fast_newer_val, slow_older_val, slow_newer_val):
    cross_test = False
    direction = ''
    if (fast_newer_val - slow_newer_val)*(fast_older_val - slow_older_val) < 0:
        cross_test = True
        if (fast_newer_val - slow_newer_val) > 0:
            direction = '+'
        else:
            direction = '-'
    return [cross_test, direction]


def contains_nan(values_list):
    test = False
    for val in values_list:
        if str(val).lower() == 'nan'.lower():
            test = True
            break
    return test


#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------
if __name__ == "__main__":
    pass