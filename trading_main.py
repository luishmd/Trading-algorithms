__author__ = "Luis Domingues"
__maintainer__ = "Luis Domingues"
__email__ = "luis.hmd@gmail.com"

#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import lib_data_quandl
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
def get_params_dic(root_dir):
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

        filter_params_dic = cfg['filter_params']
        backtesting_params_dic = cfg['backtesting_params']
        exec_params_dic = cfg['exec_params']
        print("Loaded inputs successfully.")
    except:
        print("Failed to load inputs. Exiting...")
        sys.exit(1)


    # Get quandl API key
    try:
        api_key_file = lib_path_ops.join_paths(root_dir, 'inputs/quandl_api_key.yaml')
        with open(api_key_file, 'r') as ymlfile:
            cfg_api_key = yaml.load(ymlfile, Loader=yaml.FullLoader)

        api_key = cfg_api_key['api_key']
        print("Using quandl API key: {}".format(api_key))
    except:
        print("Failed to get quandl API key. Exiting...")
        sys.exit(1)

    assert api_key

    additional_params_dic = {
        "api_key": api_key,
        "Excel output dir": lib_path_ops.join_paths(root_dir, 'outputs/'),
        "Excel template file": lib_path_ops.join_paths(root_dir, lib_path_ops.join_paths('outputs/', exec_params_dic['Output template'])),
        "Database directory": lib_path_ops.join_paths(root_dir, 'databases/Euronext'),
        "Euronext datasets codes csv file": lib_path_ops.join_paths(root_dir,'databases/Euronext/EURONEXT-datasets-codes.csv')
    }

    # Start building single params_dic. Start with exec_params
    d = exec_params_dic
    d.update(backtesting_params_dic)
    d.update(additional_params_dic)
    # Check stock list
    if d['Stock list']:
        d['Stock list'] = list(cfg[d['Stock list']])
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
            s = 'lib_filters.{}'.format(filter)
            aux.append(eval(s))
        filter_params_dic['Filters list'] = aux
        d.update(filter_params_dic)
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
def main(params_dic):
    """
    Main function that executes all the steps of the analysis in sequence
    :param params_dic: dictionary with execution parameters
    :return: the 'output.xlsx' file
    """
    #  Update data from quandl
    if params_dic['Update data']:
        lib_data_quandl.update_euronext_data(params_dic['api_key'],
                                             params_dic['Euronext datasets codes csv file'],
                                             params_dic['Database directory'],
                                             params_dic['Stock list'])

    # Run algorithm
    if params_dic['Run algorithm']:
        print("\nStarting data analysis...")
        # Get stock files
        try:
            database_dir = params_dic['Database directory']
            if params_dic['Stock list'] != None:
                file_names=[]
                stock_list = list(params_dic['Stock list'])
                for stock in stock_list:
                    s = 'EURONEXT_{}'.format(stock)
                    file_names.append(s)
                stock_ds_files = lib_file_ops.get_files_complete_names_with_extensions(database_dir, file_names=file_names, file_extensions=['.file'])
            else:
                stock_ds_files = lib_file_ops.get_files_complete_names_with_extensions(database_dir, file_extensions=['.file'])
        except:
            print("No stocks to analyze. Exiting...")
            sys.exit(1)

        # Orders and positions tables
        pt_long_dic = {}
        pt_short_dic = {}
        ot_dic = {}

        # Create results directory and create output file from template
        dir_name = datetime.datetime.now().strftime("%d%m%Y_%H%M%S")
        output_dir = lib_directory_ops.create_dir(params_dic['Excel output dir'], dir_name)
        assert output_dir != None
        new_file = 'output_' + dir_name + '.xlsx'
        output_file = lib_path_ops.join_paths(output_dir, new_file)
        r = lib_file_ops.copy_file(params_dic['Excel template file'], output_file)
        params_dic['Excel output file'] = output_file
        assert r != None

        # Open output file and write parameters
        wb = lib_excel.open_workbook(params_dic['Excel output file'])
        lib_write.write_results_to_excel(params_dic, wb, write_params=True, write_table=False)
        lib_excel.save_workbook(wb, output_file)
        assert wb != None

        # For every stock...
        n_total_stocks = len(stock_ds_files)
        n_stocks_analyzed = 0
        for stock_ds_file in stock_ds_files:
            # Get stock data
            is_in_database = True
            try:
                st = lib_data_quandl.unpickle_object(stock_ds_file)
                stock_name = st.get_name()
            except AttributeError:
                is_in_database = False

            if is_in_database:
                stock_ds = st.get_dataset()
                stock_database = st.get_database_code()
                quandl_code = st.get_quandl_code()

                # Determine start and end dates for analysis and dataset
                [start_date_ds_obj, end_date_ds_obj] = lib_general_ops.get_dataset_time_interval(stock_ds)

                # Apply filters only to analysis interval
                analyze_stock = True
                filters_function_list = params_dic['Filters list']
                if analyze_stock:
                    for filter in filters_function_list:
                        # if a stock does not pass a single filter it will not be analyzed
                        if not filter(st, start_date_ds_obj, end_date_ds_obj, params_dic):
                            analyze_stock = False
                            print('%s triggered filter <%s>.' % (stock_name, filter.__name__))
                            break
                del st

                # Only for adequate stocks is the trading algorithm applied
                if analyze_stock:
                    n_stocks_analyzed = n_stocks_analyzed + 1
                    if params_dic['Mode'] == 'Analysis':
                        print('%s is being analyzed...' % stock_name)
                    if params_dic['Mode'] == 'Backtesting':
                        print('%s is being backtested...' % stock_name)

                    [ot, pt_long, pt_short] = params_dic['Algorithm function'](params_dic, stock_name, stock_database, quandl_code, stock_ds)

                    # Add to dictionary
                    if not ot.is_empty():
                        ot_dic[stock_name] = ot
                    if not pt_long.is_empty():
                        pt_long_dic[stock_name] = pt_long
                    if not pt_short.is_empty():
                        pt_short_dic[stock_name] = pt_short

                    # Write results
                    if params_dic['Mode'] == 'Analysis':
                        lib_write.write_results_to_excel(params_dic, wb, ot, write_params=False, write_table=True)
                    if params_dic['Mode'] == 'Backtesting':
                        lib_write.write_results_to_excel(params_dic, wb, pt_long, write_params=False, write_table=True)
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
    main(get_params_dic(root_dir))

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

#    d=get_params_dic(root_dir)
#    for el in d.keys():
#        print('{}: {}'.format(el,d[el]))