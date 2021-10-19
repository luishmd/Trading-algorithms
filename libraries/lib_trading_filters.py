__author__ = "Luis Domingues"


#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import talib
import numpy as np
import datetime


#----------------------------------------------------------------------------------------
# INPUTS
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def turnover(stock_obj, start_date_obj, end_date_obj, params_dic):
    # turnover values in Currency ( turnover = SUM((Amount_per_transaction * price_transation)
    stock_ds = stock_obj.get_dataset()
    stock_ds['Turnover'] = stock_ds['Volume'] * stock_ds['Close']
    analyze_stock = True
    try:
        MA_50_turnover = talib.SMA(stock_ds['Turnover'], 50)
        if str(MA_50_turnover[end_date_obj]).lower() != 'nan':
            max_turnover = np.nanmax(MA_50_turnover)
            if max_turnover < params_dic['Min turnover']:
                analyze_stock = False
        else:
            analyze_stock = False
    except:
        analyze_stock = False
    return analyze_stock

def price(stock_obj, start_date_obj, end_date_obj, params_dic):
    # Price
    stock_ds = stock_obj.get_dataset()
    analyze_stock = True
    try:
        MA_50_price = talib.SMA(stock_ds['Low'], 50)
        if str(MA_50_price[end_date_obj]).lower() != 'nan':
            low_price = np.nanmax(MA_50_price[start_date_obj:end_date_obj])
            if low_price > params_dic['Max price']:
                analyze_stock = False
        else:
            analyze_stock = False
    except:
        analyze_stock = False
    return analyze_stock

def dataset_size(stock_obj, start_date_obj, end_date_obj, params_dic):
    analyze_stock = True
    try:
        if (end_date_obj - start_date_obj < datetime.timedelta(days=params_dic['Min dataset size'])):
            analyze_stock = False
    except:
        analyze_stock = False
    return analyze_stock

def dataset_old(stock_obj, start_date_obj, end_date_obj, params_dic):
    analyze_stock = True
    if (datetime.date.today() - end_date_obj > datetime.timedelta(days=params_dic['Max days since update'])):
        analyze_stock = False
    return analyze_stock

def stock_list(stock_obj, start_date_obj, end_date_obj, params_dic):
    stock_name = stock_obj.get_name()
    analyze_stock = True
    stock_list = list(params_dic['Stock list'])
    if stock_list != None:
        if not (stock_name in stock_list):
            analyze_stock = False
    return analyze_stock