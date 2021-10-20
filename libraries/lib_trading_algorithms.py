__author__ = "Luis Domingues"


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
import pandas as pd

#----------------------------------------------------------------------------------------
# INPUTS
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def alg_trading_indicators(alg_name, eq, p_dic):
    ti_df = pd.DataFrame(eq.get_dataset().index)
    ti_df.set_index('Date')
    hist = eq.get_dataset()
    if alg_name == "algorithm_1":
        ti_df["ADX_14"] = talib.ADX(hist['High'], hist['Low'], hist['Close'], 14)
        ti_df["DI_plus_14"] = talib.PLUS_DI(hist['High'], hist['Low'], hist['Close'], 14)
        ti_df["DI_minus_14"] = talib.MINUS_DI(hist['High'], hist['Low'], hist['Close'], 14)
        ti_df["MA_50"] = talib.SMA(hist['Close'], 50)
        ti_df["MA_100"] = talib.SMA(hist['Close'], 100)
        ti_df["MA_200"] = talib.SMA(hist['Close'], 200)
        ti_df["MA_50_turnover"] = talib.SMA(hist['Turnover'], 50)
        ti_df["MA_50_price"] = talib.SMA(hist['Low'], 50)
        if p_dic['Trending indicator'] == 'MA5/20':
            ti_df["MA_5"] = talib.SMA(hist['Close'], 5)
            ti_df["MA_20"] = talib.SMA(hist['Close'], 20)
        if p_dic['Non-trending indicator'] == 'STOCH-S':
            [ti_df["STOCH_K_10_3_3"], ti_df["STOCH_D_10_3_3"]] = talib.STOCH(hist['High'], hist['Low'], hist['Close'],
                                                                             fastk_period=10, slowk_period=3, slowk_matype=0,
                                                                             slowd_period=3, slowd_matype=0)
    if alg_name == "Algorithm 2":
        pass
    return ti_df


#----------------------------------------------------------------------------------------
# ALGORITHMS
#----------------------------------------------------------------------------------------
def algorithm_1(p_dic, eq, hist, ti_df, day, last_day):

    nan_in_data = False

    if not nan_in_data:
        # Determine trend direction
        if ti_df["ADX_14"][day] > p_dic["Trending threshold"]:
            if ti_df["DI_plus_14"][day] > ti_df["DI_minus_14"][day]:
                eq.set_trend(1)
            else:
                eq.set_trend(-1)
        else:
            eq.set_trend(0)

        medium_term_trend = '+ or -'
        if p_dic['MT trend TA indicator'] == 'MA20':
            if ti_df["MA_20"][day] - ti_df["MA_20"][previous_day]>0:
                medium_term_trend = '+'
            else:
                medium_term_trend = '-'
        if p_dic['MT trend TA indicator'] == 'MA50':
            if ti_df["MA_50"][day] - ti_df["MA_50"][previous_day]>0:
                medium_term_trend = '+'
            else:
                medium_term_trend = '-'
        if p_dic['MT trend TA indicator'] == 'MA100':
            if ti_df["MA_100"][day] - ti_df["MA_100"][previous_day]>0:
                medium_term_trend = '+'
            else:
                medium_term_trend = '-'
        if p_dic['MT trend TA indicator'] == 'MA200':
            if ti_df["MA_200"][day] - ti_df["MA_200"][previous_day]>0:
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
        if eq.get_trend() == 1 or eq.get_trend() == -1:
            if p_dic['Trending indicator'] == 'MA5/20':
                [cross_test, cross_direction] = lib_general_ops.has_crossed(ti_df["MA_5"][previous_day], ti_df["MA_5"][day], ti_df["MA_20"][previous_day], ti_df["MA_20"][day])

            if p_dic['Trending indicator'] == 'MA20/50':
                [cross_test, cross_direction] = lib_general_ops.has_crossed(ti_df["MA_20"][previous_day], ti_df["MA_20"][day], ti_df["MA_50"][previous_day], ti_df["MA_50"][day])

            if cross_test and cross_direction == '+' and ('+' in medium_term_trend):
                ta_indicator = p_dic['Trending indicator']
                trading_signal_long = 'buy'
                trading_signal_short = 'sell'

            if cross_test and cross_direction == '-' and ('-' in medium_term_trend):
                ta_indicator = p_dic['Trending indicator']
                trading_signal_long = 'sell'
                trading_signal_short = 'buy'

        # Use stochastics if not trending
        if eq.get_trend() == 0:
            if p_dic['Non-trending indicator'] == 'STOCH-S':
                if ((ti_df["STOCH_K_10_3_3"][day] < p_dic["STOCH-S Oversold"]) and (ti_df["STOCH_D_10_3_3"][day] < p_dic["STOCH-S Oversold"])) or ((ti_df["STOCH_K_10_3_3"][day] > p_dic["STOCH-S Overbought"]) and (ti_df["STOCH_D_10_3_3"][day] > p_dic["STOCH-S Overbought"])):
                    previous_day = lib_general_ops.get_previous_date(hist, day)
                    [cross_test, cross_direction] = lib_general_ops.has_crossed(ti_df["STOCH_K_10_3_3"][previous_day], ti_df["STOCH_K_10_3_3"][day], ti_df["STOCH_D_10_3_3"][previous_day], ti_df["STOCH_D_10_3_3"][day])

            if cross_test and cross_direction == '+' and (ti_df["STOCH_K_10_3_3"][day] < p_dic["STOCH-S Oversold"] or (ti_df["STOCH_D_10_3_3"][day]) < p_dic["STOCH-S Oversold"]):
                ta_indicator = p_dic['Non-trending indicator']
                trading_signal_long = 'buy'
                trading_signal_short = 'sell'

            if cross_test and cross_direction == '-' and (ti_df["STOCH_K_10_3_3"][day] > p_dic["STOCH-S Overbought"] or (ti_df["STOCH_D_10_3_3"][day]) > p_dic["STOCH-S Overbought"]) :
                ta_indicator = p_dic['Non-trending indicator']
                trading_signal_long = 'sell'
                trading_signal_short = 'buy'

        # Open/close positions
        if cross_test:
            eq.set_DI_negative(ti_df["DI_minus_14"][day])
            eq.set_ADX(ti_df["ADX_14"][day])
            eq.set_MA_turnover(ti_df["MA_50_turnover"][day])
            eq.set_MA_price(ti_df["MA_50_price"][day])
            eq.set_MA_50(ti_df["MA_50"][day])
            eq.set_MA_100(ti_df["MA_100"][day])
            eq.set_MA_200(ti_df["MA_200"][day])
            if p_dic['Trending indicator'] == 'MA5/20':
                eq.set_MA_5(ti_df["MA_5"][day])
                eq.set_MA_20(ti_df["MA_20"][day])
            if p_dic['Non-trending indicator'] == 'STOCH-S':
                eq.set_STOCH_S(ti_df["STOCH_K_10_3_3"][day], ti_df["STOCH_D_10_3_3"][day])
                eq.set_DI_positive(ti_df["DI_plus_14"][day])

        [ot, pt_long, pt_short] = alg.manage_orders_positions(p_dic, eq, ta_indicator, trading_signal_long, trading_signal_short, stock_ds, day)

    return [ot, pt_long, pt_short]