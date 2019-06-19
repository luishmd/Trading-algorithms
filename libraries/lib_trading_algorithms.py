__author__ = "Luis Domingues"
__maintainer__ = "Luis Domingues"
__email__ = "luis.hmd@gmail.com"

#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import talib
import datetime
import lib_general_ops
from trading_classes import Stock, Algorithm

#----------------------------------------------------------------------------------------
# INPUTS
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
# ALGORITHMS
#----------------------------------------------------------------------------------------
def algorithm_1(params_dic, stock_name, stock_database, quandl_code, stock_ds):

    alg = Algorithm(params_dic, stock_name, stock_database, quandl_code, stock_ds)
    ot = alg.ot
    pt_long = alg.pt_long
    pt_short = alg.pt_short

    # Calculate TA indicators
    ADX_14 = talib.ADX(stock_ds['High'], stock_ds['Low'], stock_ds['Last'], 14)
    DI_plus_14 = talib.PLUS_DI(stock_ds['High'], stock_ds['Low'], stock_ds['Last'], 14)
    DI_minus_14 = talib.MINUS_DI(stock_ds['High'], stock_ds['Low'], stock_ds['Last'], 14)
    MA_50 = talib.SMA(stock_ds['Last'], 50)
    MA_100 = talib.SMA(stock_ds['Last'], 100)
    MA_200 = talib.SMA(stock_ds['Last'], 200)
    MA_50_turnover = talib.SMA(stock_ds['Turnover'],50)
    MA_50_price = talib.SMA(stock_ds['Low'], 50)
    if params_dic['Trending indicator'] == 'MA5/20':
        MA_5 = talib.SMA(stock_ds['Last'], 5)
        MA_20 = talib.SMA(stock_ds['Last'], 20)
    if params_dic['Non-trending indicator'] == 'STOCH-S':
        [STOCH_K_10_3_3, STOCH_D_10_3_3] = talib.STOCH(stock_ds['High'], stock_ds['Low'], stock_ds['Last'], fastk_period=10, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

    # Apply algorithm for all days in interval
    day = alg.start_date_anal_obj
    last_day = alg.end_date_anal_obj
    while last_day - day >= datetime.timedelta(0):
        st = Stock(stock_name, stock_database, quandl_code)
        previous_day = lib_general_ops.get_previous_date(stock_ds, day)

        # Protect agains 'NaN' in data for all indicators needed to apply algorithm
        nan_in_data = lib_general_ops.contains_nan([ADX_14[day], DI_plus_14[day], DI_minus_14[day]])
        if params_dic['Trending indicator'] == 'MA5/20':
            nan_in_data = lib_general_ops.contains_nan([MA_5[day], MA_20[previous_day], MA_20[day]])
        if params_dic['Non-trending indicator'] == 'STOCH-S':
            nan_in_data = lib_general_ops.contains_nan([STOCH_K_10_3_3[day], STOCH_D_10_3_3[previous_day], STOCH_D_10_3_3[day]])

        if not nan_in_data:
            # Determine trend direction
            if ADX_14[day] > params_dic["Trending threshold"]:
                if DI_plus_14[day] > DI_minus_14[day]:
                    st.set_trend(1)
                else:
                    st.set_trend(-1)
            else:
                st.set_trend(0)

            medium_term_trend = '+ or -'
            if params_dic['MT trend TA indicator'] == 'MA20':
                if MA_20[day] - MA_20[previous_day]>0:
                    medium_term_trend = '+'
                else:
                    medium_term_trend = '-'
            if params_dic['MT trend TA indicator'] == 'MA50':
                if MA_50[day] - MA_50[previous_day]>0:
                    medium_term_trend = '+'
                else:
                    medium_term_trend = '-'
            if params_dic['MT trend TA indicator'] == 'MA100':
                if MA_100[day] - MA_100[previous_day]>0:
                    medium_term_trend = '+'
                else:
                    medium_term_trend = '-'
            if params_dic['MT trend TA indicator'] == 'MA200':
                if MA_200[day] - MA_200[previous_day]>0:
                    medium_term_trend = '+'
                else:
                    medium_term_trend = '-'

            # Determine buy and sell signals
            cross_test = False
            cross_direction = ''
            trading_signal_long = ''
            trading_signal_short = ''
            ta_indicator = ''
            # Use MA if trending
            if st.get_trend() == 1 or st.get_trend() == -1:
                if params_dic['Trending indicator'] == 'MA5/20':
                    [cross_test, cross_direction] = lib_general_ops.has_crossed(MA_5[previous_day], MA_5[day], MA_20[previous_day], MA_20[day])

                if params_dic['Trending indicator'] == 'MA20/50':
                    [cross_test, cross_direction] = lib_general_ops.has_crossed(MA_20[previous_day], MA_20[day], MA_50[previous_day], MA_50[day])

                if cross_test and cross_direction == '+' and ('+' in medium_term_trend):
                    ta_indicator = params_dic['Trending indicator']
                    trading_signal_long = 'buy'
                    trading_signal_short = 'sell'

                if cross_test and cross_direction == '-' and ('-' in medium_term_trend):
                    ta_indicator = params_dic['Trending indicator']
                    trading_signal_long = 'sell'
                    trading_signal_short = 'buy'

            # Use stochastics if not trending
            if st.get_trend() == 0:
                if params_dic['Non-trending indicator'] == 'STOCH-S':
                    if ((STOCH_K_10_3_3[day] < params_dic["STOCH-S Oversold"]) and (STOCH_D_10_3_3[day] < params_dic["STOCH-S Oversold"])) or ((STOCH_K_10_3_3[day] > params_dic["STOCH-S Overbought"]) and (STOCH_D_10_3_3[day] > params_dic["STOCH-S Overbought"])):
                        previous_day = lib_general_ops.get_previous_date(stock_ds, day)
                        [cross_test, cross_direction] = lib_general_ops.has_crossed(STOCH_K_10_3_3[previous_day], STOCH_K_10_3_3[day], STOCH_D_10_3_3[previous_day], STOCH_D_10_3_3[day])

                if cross_test and cross_direction == '+' and (STOCH_K_10_3_3[day] < params_dic["STOCH-S Oversold"] or (STOCH_D_10_3_3[day]) < params_dic["STOCH-S Oversold"]) :
                    ta_indicator = params_dic['Non-trending indicator']
                    trading_signal_long = 'buy'
                    trading_signal_short = 'sell'

                if cross_test and cross_direction == '-' and (STOCH_K_10_3_3[day] > params_dic["STOCH-S Overbought"] or (STOCH_D_10_3_3[day]) > params_dic["STOCH-S Overbought"]) :
                    ta_indicator = params_dic['Non-trending indicator']
                    trading_signal_long = 'sell'
                    trading_signal_short = 'buy'

            # Open/close positions
            if cross_test:
                st.set_DI_negative(DI_minus_14[day])
                st.set_ADX(ADX_14[day])
                st.set_MA_turnover(MA_50_turnover[day])
                st.set_MA_price(MA_50_price[day])
                st.set_MA_50(MA_50[day])
                st.set_MA_100(MA_100[day])
                st.set_MA_200(MA_200[day])
                if params_dic['Trending indicator'] == 'MA5/20':
                    st.set_MA_5(MA_5[day])
                    st.set_MA_20(MA_20[day])
                if params_dic['Non-trending indicator'] == 'STOCH-S':
                    st.set_STOCH_S(STOCH_K_10_3_3[day], STOCH_D_10_3_3[day])
                    st.set_DI_positive(DI_plus_14[day])

            [ot, pt_long, pt_short] = alg.manage_orders_positions(params_dic, st, ta_indicator, trading_signal_long, trading_signal_short, stock_ds, day)

        day = lib_general_ops.increment_date(stock_ds['Last'], day)
        del st

    return [ot, pt_long, pt_short]