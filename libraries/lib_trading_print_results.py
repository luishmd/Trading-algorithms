__author__ = "Luis Domingues"


#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import lib_excel_ops_openpyxl as lib_excel

#----------------------------------------------------------------------------------------
# INPUTS
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def write_results_to_excel(params_dic, wb, table=None, write_params=True, write_table=True):
    # Get worksheet for parameters and execution/backtesting
    if write_params:
        ws_params = lib_excel.get_worksheet(wb, 'Parameters')
        assert ws_params != None
    if write_table:
        if params_dic['Mode'] == 'Analysis':
            ws_name = 'Execution'
        if params_dic['Mode'] == 'Backtesting':
            ws_name = 'Backtesting'
        ws = lib_excel.get_worksheet(wb, ws_name)
        assert ws != None

    # Write parameters
    if write_params:
        function_name = 'write_parameters_' + params_dic['Algorithm name']
        eval(function_name)(params_dic, ws_params)
    # Write results for execution/backtesting
    if write_table:
        function_name = 'write_table_' + params_dic['Algorithm name']
        eval(function_name)(params_dic, table, ws)

    return 0

def write_parameters_algorithm_1(params_dic, ws_params):
    # Write parameters
    row_i = 8
    for param in params_dic.keys():
        ws_params.cell(row=row_i, column=1, value=param)
        try:
            ws_params.cell(row=row_i, column=2, value=params_dic[param])
        except:
            ws_params.cell(row=row_i, column=2, value=str(params_dic[param]))
        row_i = row_i + 1
    return 0

# Write algorithm-specific functions below
# They will automatically be used by the main function 'write_results_to_excel'
#------------------------------------------------------------------------------
def write_table_algorithm_1(params_dic, table, ws):
    # Write results
    if params_dic['Mode'] == 'Analysis':
        # Write orders
        orders_table = table
        orders_list = orders_table.get_orders_list()
        row_i = lib_excel.determine_first_empty_row(ws, row_start=8)
        for order in orders_list:
            st = order.get_stock()
            id = row_i - 8 + 1
            ws.cell(row=row_i, column=1, value=id)
            ws.cell(row=row_i, column=2, value=order.get_name())
            ws.cell(row=row_i, column=3, value=order.get_position_type())
            ws.cell(row=row_i, column=4, value=order.get_order_type())
            ws.cell(row=row_i, column=5, value=order.get_amount())
            ws.cell(row=row_i, column=6, value=order.get_stop_loss())
            ws.cell(row=row_i, column=7, value=order.get_date())
            ws.cell(row=row_i, column=8, value=order.get_price())
            ws.cell(row=row_i, column=11, value=order.get_ta_indicator())
            ws.cell(row=row_i, column=12, value=st.get_ADX())
            ws.cell(row=row_i, column=13, value=st.get_DI_positive())
            ws.cell(row=row_i, column=14, value=st.get_DI_negative())
            ws.cell(row=row_i, column=15, value=st.get_MA_5())
            ws.cell(row=row_i, column=16, value=st.get_MA_20())
            ws.cell(row=row_i, column=17, value=st.get_MA_50())
            ws.cell(row=row_i, column=18, value=st.get_MA_200())
            ws.cell(row=row_i, column=19, value=st.get_STOCH_S()[0])
            ws.cell(row=row_i, column=20, value=st.get_STOCH_S()[1])
            ws.cell(row=row_i, column=21, value=st.get_MA_turnover())
            ws.cell(row=row_i, column=22, value=st.get_MA_price())

            row_i = row_i + 1

    if params_dic['Mode'] == 'Backtesting':
        positions_table = table
        positions_list = positions_table.get_positions_list()
        row_i = lib_excel.determine_first_empty_row(ws, row_start=8)
        if params_dic['Backtesting print positions'] == True:
            for position in positions_list:
                id = row_i - 8 + 1
                ws.cell(row=row_i, column=1, value=id)
                ws.cell(row=row_i, column=2, value=position.get_name())
                ws.cell(row=row_i, column=3, value=position.get_position_type())
                ws.cell(row=row_i, column=4, value=position.get_state())
                ws.cell(row=row_i, column=5, value=position.get_amount())
                ws.cell(row=row_i, column=6, value=position.get_stop_loss())
                ws.cell(row=row_i, column=7, value=position.get_date_entry())
                ws.cell(row=row_i, column=8, value=position.get_price_entry())
                ws.cell(row=row_i, column=9, value=position.get_ta_indicator_entry())
                if position.get_state() == 'closed':
                    ws.cell(row=row_i, column=12, value=position.get_date_exit())
                    ws.cell(row=row_i, column=13, value=position.get_price_exit())
                    ws.cell(row=row_i, column=14, value=position.get_ta_indicator_exit())
                    ws.cell(row=row_i, column=15, value=position.get_money_entry())
                    ws.cell(row=row_i, column=16, value=position.get_money_exit())
                    ws.cell(row=row_i, column=17, value=position.get_profit_losses())
                    ws.cell(row=row_i, column=18, value=position.get_profit_losses_pct())
                row_i = row_i + 1

        else:
            id = row_i - 8 + 1
            ws.cell(row=row_i, column=1, value=id)
            ws.cell(row=row_i, column=2, value=positions_table.get_name())
            ws.cell(row=row_i, column=3, value=positions_table.get_positions_type())
            ws.cell(row=row_i, column=15, value=positions_table.get_total_money_entry())
            ws.cell(row=row_i, column=17, value=positions_table.get_profit_losses())
            ws.cell(row=row_i, column=18, value=positions_table.get_profit_losses_pct())
    return 0
