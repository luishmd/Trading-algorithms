__author__ = "Luis Domingues"


#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import lib_directory_ops
import lib_file_ops
import sys
import lib_general_ops
import datetime
import os
import lib_path_ops
import lib_trading_algorithms as lib_alg
import lib_trading_filters as lib_filters
import lib_trading_print_results as lib_write
import lib_excel_ops_openpyxl as lib_excel
import yaml
import lib_postgresql_ops as lib_pg
import lib_data_yfinance as lib_yf
import pandas as pd
from trading_classes import Stock
import talib


#----------------------------------------------------------------------------------------
    # PRE-CALCULATIONS
#----------------------------------------------------------------------------------------
# Get inputs
root_dir = os.getcwd()
root_dir = root_dir+'/'


#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def get_p_dic(root_dir):
    """
    Function that reads the yaml config files (inputs + api_key) and returns a dictionary with
    :param root_dir: directory of execution
    :return: dictionary containing all the parameters needed to run the script
    """
    # Get inputs from inputs.yaml
    try:
        input_file = lib_path_ops.join_paths(root_dir, 'inputs/inputs.yaml')
        with open(input_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

        filter_p_dic = cfg['filter_params']
        backtesting_p_dic = cfg['backtesting_params']
        exec_p_dic = cfg['exec_params']
        eq_connection_p_dic = cfg['Equities connection parameters']
        print("Loaded inputs successfully.")
    except:
        print("Failed to load inputs. Exiting...")
        sys.exit(1)


    additional_p_dic = {
        "Excel output dir": lib_path_ops.join_paths(root_dir, 'outputs/'),
        "Excel template file": lib_path_ops.join_paths(root_dir, lib_path_ops.join_paths('outputs/', exec_p_dic['Output template'])),
        "Database directory": lib_path_ops.join_paths(root_dir, 'databases/Euronext')
    }

    # Start building single p_dic. Start with exec_params
    d = exec_p_dic
    d.update(backtesting_p_dic)
    d.update(additional_p_dic)
    d.update(eq_connection_p_dic)
    # Convert dates to datetime.date
    if d['Start date']:
        d['Start date'] = datetime.datetime.strptime(str(d['Start date']), str(d['Format date string'])).date()
    if d['End date']:
        d['End date'] = datetime.datetime.strptime(str(d['End date']), str(d['Format date string'])).date()
    # Add filters to dictionary
    if d['Filters list'] != []:
        # Need to convert strings to function handles
        aux = []
        for filter in d['Filters list']:
            f = 'lib_filters.{}'.format(filter)
            aux.append(eval(f))
        filter_p_dic['Filters list'] = aux
        d.update(filter_p_dic)
    # Add desired algorithm params to dictionary (Need to convert string to function handle)
    f = 'lib_alg.' + d['Algorithm name']
    d['Algorithm function'] = eval(f)
    # Add desired algorithm parameters
    alg_params = d['Algorithm name'] + '_params'
    d.update(cfg[alg_params])

    return d


#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------
def main(p_dic):
    """
    Main function that executes all the steps of the analysis in sequence
    :param p_dic: dictionary with execution parameters
    :return: the 'output.xlsx' file
    """
    # Run algorithm
    if p_dic['Run algorithm']:
        # Orders and positions tables
        pt_long_dic = {}
        pt_short_dic = {}
        ot_dic = {}

        # Create results directory and create output file from template
        dir_name = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        output_dir = lib_directory_ops.create_dir(p_dic['Excel output dir'], dir_name)
        assert output_dir != None
        new_file = 'output_' + dir_name + '.xlsx'
        output_file = lib_path_ops.join_paths(output_dir, new_file)
        r = lib_file_ops.copy_file(p_dic['Excel template file'], output_file)
        p_dic['Excel output file'] = output_file
        assert r != None

        # Open output file and write parameters
        wb = lib_excel.open_workbook(p_dic['Excel output file'])
        lib_write.write_results_to_excel(p_dic, wb, write_params=True, write_table=False)
        lib_excel.save_workbook(wb, output_file)
        assert wb != None

        # For every stock...
        n_total_stocks = len(p_dic['Equities list'])
        n_stocks_analyzed = 0
        conn = lib_pg.get_pg_conn(p_dic['host'], p_dic['database'], p_dic['user'], p_dic['port'], p_dic['password'])
        for ticker in p_dic['Equities list']:
            # Get equity data
            if lib_yf.exists_pg_master_table(conn, 'History', ticker):
                # Get historic data
                columns = '"Date", "Open", "High", "Low", "Close", "Volume"'
                query = """SELECT {} FROM public."History-{}";""".format(columns, ticker)
                rows = lib_pg.query_pg_database(conn, query)
                columns = columns.strip(' ')
                columns = columns.split(',')
                t_ds = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
                t_ds = t_ds.set_index('Date')
                assert not(t_ds.empty)
                # Get short name
                query = """SELECT "ShortName" FROM public."Metadata" WHERE "Ticker" = '{}';""".format(ticker)
                rows = lib_pg.query_pg_database(conn, query)
                ticker_sname = rows[0][0]
                eq = Stock(ticker_sname, t_ds)


                # Determine start and end dates for analysis and dataset
                [start_date_ds_obj, end_date_ds_obj] = lib_general_ops.get_dataset_time_interval(t_ds)

                # Apply filters only to analysis interval
                analyze_ticker = True
                filters_function_list = p_dic['Filters list']
                if p_dic['Apply filters'] and analyze_ticker:
                    for filter in filters_function_list:
                        # if a ticker does not pass a single filter it will not be analyzed
                        if not filter(eq, start_date_ds_obj, end_date_ds_obj, p_dic):
                            analyze_stock = False
                            print('%s triggered filter <%s>.' % (ticker_sname, filter.__name__))
                            break
                del eq

                # Only for adequate stocks is the trading algorithm applied
                if analyze_ticker:
                    n_stocks_analyzed = n_stocks_analyzed + 1
                    if p_dic['Mode'] == 'Analysis':
                        print('%s is being analyzed...' % ticker_sname)
                    if p_dic['Mode'] == 'Backtesting':
                        print('%s is being backtested...' % ticker_sname)

                    [ot, pt_long, pt_short] = p_dic['Algorithm function'](p_dic, ticker_sname, t_ds)

                    # Add to dictionary
                    if not ot.is_empty():
                        ot_dic[ticker_sname] = ot
                    if not pt_long.is_empty():
                        pt_long_dic[ticker_sname] = pt_long
                    if not pt_short.is_empty():
                        pt_short_dic[ticker_sname] = pt_short

                    # Write results
                    if p_dic['Mode'] == 'Analysis':
                        lib_write.write_results_to_excel(p_dic, wb, ot, write_params=False, write_table=True)
                    if p_dic['Mode'] == 'Backtesting':
                        lib_write.write_results_to_excel(p_dic, wb, pt_long, write_params=False, write_table=True)
                    lib_excel.save_workbook(wb, output_file)

                    # Delete unnecessary objects
                    del ot
                    del pt_long
                    del pt_short

        # Close necessary files
        wb.close()

        # Statistics
        if n_total_stocks > 0:
            print("\nFinished !\n%s of %s stocks analyzed (%0.1f %%)" % (str(n_stocks_analyzed), str(n_total_stocks), float(n_stocks_analyzed)/n_total_stocks*100))
        else:
            print("\nFinished ! No stocks analyzed")

        return 0

#----------------------------------------------------------------------------------------
# EXECUTION
#----------------------------------------------------------------------------------------
if __name__ == "__main__":
    main(get_p_dic(root_dir))

# Testing
#    st = lib_data_quandl.get_euronext_dataset("ALMED")
#    ds = lib_data_quandl.get_quandl_data('EURONEXT/ALMED')
#    ds = st.get_dataset()
#    print ds
#    print ds['Last'][datetime.date(2016,06,30)]
#    SMA_200 = talib.SMA(ds['Last'],200)
#    print SMA_200
#    print contains_nan([SMA_200[datetime.date(2014, 03, 31)]])
#    t = datetime.date(2018,6,15)
#    new_t = increment_date(SMA_200,t)
#    print new_t
#    a = str(SMA_200[datetime.date(2018, 06, 12)])
#    print a.lower() == 'nan'.lower()
#    print type(SMA_200[datetime.date(2014,03,31)])

#    d=get_p_dic(root_dir)
#    for el in d.keys():
#        print('{}: {}'.format(el,d[el]))