__author__ = "Luis Domingues"


#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# Constants
#----------------------------------------------------------------------------------------
date_format = "%Y-%m-%d"


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import lib_directory_ops
import lib_file_ops
import sys
import lib_general_ops
import datetime as dt
import os
import lib_path_ops
import lib_trading_algorithms as lib_alg
import lib_trading_filters as lib_filters
import lib_trading_print_results as lib_write
import lib_excel_ops_openpyxl as lib_excel
import yaml
import lib_postgresql_ops as lib_pg
import lib_db_equities as lib_db_eq
import pandas as pd
from trading_classes import Stock
from trading_classes import Trading_Manager


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

        db_cred_file = lib_path_ops.join_paths(root_dir, 'inputs')
        db_cred_file = lib_path_ops.join_paths(db_cred_file, exec_p_dic['Equities DB connection parameters file'])
        db_cred_file = db_cred_file.replace('Trading algorithms', 'Data gathering')
        with open(db_cred_file, 'r') as ymlfile:
            db_cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        eq_connection_p_dic = db_cfg['Connection parameters']
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
        d['Start date'] = dt.datetime.strptime(str(d['Start date']), date_format).date()
    if d['End date']:
        d['End date'] = dt.datetime.strptime(str(d['End date']), date_format).date()
    # Add desired algorithm params to dictionary (Need to convert string to function handle)
    f = 'lib_alg.' + d['Algorithm name']
    d['Algorithm function'] = eval(f)
    # Add desired algorithm parameters
    alg_params = d['Algorithm name'] + '_params'
    d.update(cfg[alg_params])
    # Add filters to dictionary
    if d['Filters list'] != []:
        # Need to convert strings to function handles
        aux = []
        for filter in d['Filters list']:
            f = 'lib_filters.{}'.format(filter)
            aux.append(eval(f))
        filter_p_dic['Filters list'] = aux
        d.update(filter_p_dic)

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
        # Create results directory and file (if single file)
        dir_name = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = lib_directory_ops.create_dir(p_dic['Excel output dir'], dir_name)
        assert output_dir != None

        create_file = False
        out_prefix = ''
        if p_dic['Mode'] == 'Analysis':
            out_prefix = 'an'
            create_file = True
        elif p_dic['Mode'] == 'Backtesting' and p_dic['Output file mode'] == 'Single file':
            out_prefix = 'btst'
            create_file = True
        elif p_dic['Mode'] == 'Optimization' and p_dic['Output file mode'] == 'Single file':
            out_prefix = 'opt'
            create_file = True

        if create_file:
            new_file = out_prefix + '_' + dir_name + '.xlsx'
            output_file = lib_path_ops.join_paths(output_dir, new_file)
            r = lib_file_ops.copy_file(p_dic['Excel template file'], output_file)
            assert r != None
            p_dic['Excel output file'] = output_file

            # Initialise tables manager
            mngr = Trading_Manager(p_dic)

        # For every stock...
        n_total_stocks = len(p_dic['Equities list'])
        n_stocks_analyzed = 0
        conn = lib_pg.get_pg_conn(p_dic['host'], p_dic['database'], p_dic['user'], p_dic['port'], p_dic['password'])
        for ticker in p_dic['Equities list']:
            # Get equity data
            # Get module
            query = """SELECT "RetrievalPackage" FROM public."Master" WHERE "Ticker" = '{}' AND "TableType" = 'History';""".format(
                ticker)
            rows = lib_pg.query_pg_database(conn, query)
            ticker_mod_name = ""
            if len(rows) > 1:
                print("[WARNING] More than one retrieval package for ticker: {}".format(ticker))
                print("[WARNING] Using package: {}".format(rows[0][0]))
            if len(rows) == 1:
                ticker_mod_name = rows[0][0]
            if ticker_mod_name and lib_db_eq.exists_pg_master_table(conn, 'History', ticker, ticker_mod_name):
                # Get short name
                query = """SELECT "ShortName" FROM public."Metadata" WHERE "Ticker" = '{}';""".format(ticker)
                rows = lib_pg.query_pg_database(conn, query)
                ticker_sname = rows[0][0]
                # Get historic data
                columns = '"Date", "Open", "High", "Low", "Close", "Volume"'
                query = """SELECT {} FROM public."History-{}-{}";""".format(columns, ticker_mod_name, ticker)
                rows = lib_pg.query_pg_database(conn, query)
                #columns = columns.strip(' ')
                #columns = columns.split(',')
                history_df = pd.DataFrame(rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
                history_df = history_df.set_index('Date')
                assert not(history_df.empty)

                eq = Stock(ticker, ticker_sname, history_df)

                # Determine start and end dates for analysis and dataset
                [start_date_ds_obj, end_date_ds_obj] = lib_general_ops.get_dataset_time_interval(history_df)

                # Apply filters only to analysis interval
                analyze_ticker = True
                filters_function_list = p_dic['Filters list']
                if p_dic['Apply filters'] and analyze_ticker:
                    for filter in filters_function_list:
                        # if a ticker does not pass a single filter it will not be analyzed
                        if not filter(eq, start_date_ds_obj, end_date_ds_obj, p_dic):
                            analyze_stock = False
                            print('%s triggered filter <%s>.' % (eq.get_name(), filter.__name__))
                            break

                # Only for adequate stocks is the trading algorithm applied
                if analyze_ticker:
                    # Start analysis or Backtesting or Optimization....
                    n_stocks_analyzed = n_stocks_analyzed + 1
                    out_prefix = ''
                    create_file = False
                    if p_dic['Mode'] == 'Analysis':
                        print('{} is being analyzed...'.format(eq.get_name()))
                        out_prefix = 'an'
                    if p_dic['Mode'] == 'Backtesting':
                        print('{} is being backtested...'.format(eq.get_name()))
                        out_prefix = 'btst'
                    if p_dic['Mode'] == 'Optimization':
                        print('{} is being backtested through optimization...'.format(eq.get_name()))
                        out_prefix = 'opt'

                    if (p_dic['Mode'] == 'Backtesting' or p_dic['Mode'] == 'Optimization') and p_dic['Output file mode'] == 'Multiple files':
                        new_file = out_prefix + '_' + eq.get_ticker().replace('.', '-') + '_' + dir_name + '.xlsx'
                        output_file = lib_path_ops.join_paths(output_dir, new_file)
                        r = lib_file_ops.copy_file(p_dic['Excel template file'], output_file)
                        assert r != None
                        p_dic['Excel output file'] = output_file
                        mngr = Trading_Manager(p_dic)

                    [sdate, edate] = lib_general_ops.get_analysis_time_interval(eq.get_dataset(), date_format, start_date=p_dic['Start date'], end_date=p_dic['End date'], last_n_points=p_dic['Last N days'])

                    iterations = [1]
                    if p_dic['Mode'] == 'Optimization':
                        #iterations = opt.iterations()
                        pass
                    for i in iterations:
                        pop = [1]
                        if p_dic['Mode'] == 'Optimization':
                            # pop = opt.population()
                            pass
                        for p in pop:

                            curr_date = sdate
                            while edate - curr_date >= dt.timedelta(0):

                                # Run trading algorithm
                                custom_dic = p_dic['Algorithm function'](p_dic, eq, curr_date)

                                # Manage orders and positions
                                mngr.manage_orders_positions(custom_dic, eq, curr_date)

                                # Increment current date
                                curr_date = eq.get_next_day(curr_date)

                del eq

                # Write results
                if (p_dic['Mode'] == 'Backtesting' or p_dic['Mode'] == 'Optimization') and p_dic['Output file mode'] == 'Multiple files':
                    mngr.write_results()
                    del mngr

        # Write results
        if p_dic['Mode'] == 'Analysis' or p_dic['Output file mode'] == 'Single file':
            mngr.write_results()
            del mngr

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