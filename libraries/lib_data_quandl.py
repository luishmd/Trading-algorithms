__author__ = "Luis Domingues"
__maintainer__ = "Luis Domingues"
__email__ = "luis.hmd@gmail.com"

#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import quandl
from math import floor
import csv
import pickle as pickle
import lib_path_ops
import os
from trading_classes import Stock



#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def get_dataset_codes_from_csv(csv_file_name):
    """
    Function that receives a csv file containing the dataset codes and returns them is a list
    See 'https://www.quandl.com/data/EURONEXT-Euronext-Stock-Exchange/usage/export' for an example
    :param csv_file_name:
    :return sataset codes list:
    """
    ds_codes = []
    try:
        with open(csv_file_name, 'r') as csvfile:
            lines = csv.reader(csvfile, delimiter=',', quotechar='|')
            for line in lines:
                ds_codes.append(line[0])
    except:
        print("Could not extract dataset codes from <%s>" %csv_file_name)
    return ds_codes


def split_dataset_code(dataset_code):
    """
    Function that splits a dataset code
    :param dataset_code string:
    :return database code and dataset code:
    """
    [db_code, ds_code] = dataset_code.split('/')
    return [db_code, ds_code]


def get_quandl_data(dataset_code, api_key, rows=0):
    """
    Function that returns the dataset (pandas dataframe) for a given dataset code
    :param dataset_code, rows:
    :return pandas df:
    """
    quandl.ApiConfig.api_key = api_key
    try:
        if rows == 0:
            return quandl.get(dataset_code)
        else:
            return quandl.get(dataset_code, rows=int(rows))
    except:
        print("Could not get data for <{}>".format(dataset_code))
        return 1


def pickle_object(obj, file_name):
    """
    Function that pickles an object to pickle_file
    :param obj, file_name:
    :return:
    """
    try:
        with open(file_name, 'wb') as f:
            pickle.dump(obj, f)
    except:
        print("Could not pickle {}".format(file_name))
    return 0


def unpickle_object(file_name):
    """
    Function that unpickles a pickle file
    :param file_name:
    :return obj:
    """
    return_obj = 0
    try:
        with open(file_name, 'rb') as f:
            return_obj = pickle.load(f)
    except:
        print("Could not unpickle {}".format(file_name))
    return return_obj


def update_euronext_data(api_key, euronext_datasets_codes_csv_file, database_dir, update_list):
    """
    Function that updates/retrieves historical data for the Euronext market and pickles it
    """
    ds_codes_processed = 0
    PRINT_PCT = 1
    pct_target = 1
    ds_codes = get_dataset_codes_from_csv(euronext_datasets_codes_csv_file)
    aux_list = update_list.copy()
    if aux_list != None:
        # Set to the correct format
        for i in range(len(aux_list)):
            aux_list[i] = str('EURONEXT/{}'.format(aux_list[i]))
        ds_codes = list(set(aux_list) & set(ds_codes))
    print("Starting data extraction...\n0%")
    ds_codes_total = float(len(ds_codes))
    for ds_code in ds_codes:
        ds = get_quandl_data(ds_code, api_key)
        [db_code, ds_name] = split_dataset_code(ds_code)
        st = Stock(ds_name, db_code, ds)
        pickle_file = lib_path_ops.join_paths(database_dir, db_code+'_'+ds_name+'.file')
        pickle_object(st, pickle_file)
        del st
        # Printing progression
        ds_codes_processed = ds_codes_processed + 1
        pct_completed = (ds_codes_processed / ds_codes_total) * 100.0
        if floor(pct_completed) >= pct_target:
            print(str(int(pct_completed)) + "%")
            pct_target = pct_target + PRINT_PCT
    return 0


def get_euronext_dataset(ds_name, database_dir):
    """
    Function that unpickles the historical data for a given stock and returns it
    :return dataset:
    """
    db_code = 'EURONEXT'
    st_obj = 0
    try:
        pickle_file = lib_path_ops.join_paths(database_dir, db_code+'_'+ds_name+'.file')
        st_obj = unpickle_object(pickle_file)
    except:
        print("Could not unpickle stock <%s>" % ds_name)
    return st_obj


#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass

#    with open(file_name, 'rb') as f:
#        return_obj = pickle.load(f)

