__author__ = "Luis Domingues"


#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import lib_general_ops

#----------------------------------------------------------------------------------------
# INPUTS
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# ALGORITHMS
#----------------------------------------------------------------------------------------
def algorithm_1(p_dic, eq, day):
    # Get technical indicators
    ti_df = eq.get_technical_indicators()
    s_ADX = "ADX_{}".format(p_dic["ADX period"])
    ti_df[s_ADX] = eq.get_ADX(int(p_dic["ADX period"]))
    s_DI_plus = "DI_plus_{}".format(p_dic["ADX period"])
    s_DI_minus = "DI_minus_{}".format(p_dic["ADX period"])
    ti_df[s_DI_plus] = eq.get_DI_positive(p_dic["ADX period"])
    ti_df[s_DI_minus] = eq.get_DI_negative(p_dic["ADX period"])
    if p_dic["Trending indicator"] == "SMA":
        (p_fast, p_slow) = eval(p_dic["Trending indicator parameters"])
        s_SMA_fast = "SMA_{}".format(p_fast)
        s_SMA_slow = "SMA_{}".format(p_slow)
        ti_df[s_SMA_fast] = eq.get_SMA(int(p_fast))
        ti_df[s_SMA_slow] = eq.get_SMA(int(p_slow))
    if p_dic["Non-trending indicator"] == "STOCH-S":
        (fastk_period, slowk_period, slowd_period) = eval(p_dic["Non-trending indicator parameters"])
        s_STOCH_K = "STOCH_K_".format(fastk_period, slowk_period, slowd_period)
        s_STOCH_D = "STOCH_D_".format(fastk_period, slowk_period, slowd_period)
        ti_df[s_STOCH_K], ti_df[s_STOCH_D] = eq.get_STOCH(fastk_period, slowk_period, 0, slowd_period, 0)
    if p_dic["MT trend TA indicator"] == "SMA":
        s_SMA_MT_trend = "SMA_{}".format(p_dic["MT trend TA indicator period"])
        ti_df[s_SMA_MT_trend] = eq.get_SMA(int(p_dic["MT trend TA indicator period"]))

    # Initialise remaining variables
    previous_day = eq.get_previous_day(day)
    custom_dic = {}
    nan_in_data = False

    # Run algorithm
    if not nan_in_data:
        # Determine trend direction
        if ti_df[s_ADX][day] > p_dic["Trending threshold"]:
            if ti_df[s_DI_plus][day] > ti_df[s_DI_minus][day]:
                trend = 1
            else:
                trend = -1
        else:
            trend = 0

        medium_term_trend = '+ or -'
        if p_dic['MT trend TA indicator'] == 'SMA':
            if ti_df[s_SMA_MT_trend][day] - ti_df[s_SMA_MT_trend][previous_day] > 0:
                medium_term_trend = '+'
            else:
                medium_term_trend = '-'

        # Determine buy and sell signals
        cross_test = False
        cross_direction = ''
        trading_signal_long = ''
        trading_signal_short = ''
        ta_indicator = ''
        # if trending
        if trend == 1 or trend == -1:
            if p_dic['Trending indicator'] == 'SMA':
                [cross_test, cross_direction] = lib_general_ops.has_crossed(ti_df[s_SMA_fast][previous_day], ti_df[s_SMA_fast][day], ti_df[s_SMA_slow][previous_day], ti_df[s_SMA_slow][day])

            if cross_test and cross_direction == '+' and ('+' in medium_term_trend):
                ta_indicator = p_dic['Trending indicator']
                trading_signal_long = 'buy'
                trading_signal_short = 'sell'

            if cross_test and cross_direction == '-' and ('-' in medium_term_trend):
                ta_indicator = p_dic['Trending indicator']
                trading_signal_long = 'sell'
                trading_signal_short = 'buy'

        # if not trending
        if trend == 0:
            if p_dic['Non-trending indicator'] == 'STOCH-S':
                if ((ti_df[s_STOCH_K][day] < p_dic["STOCH-S Oversold"]) and (ti_df[s_STOCH_D][day] < p_dic["STOCH-S Oversold"])) or ((ti_df[s_STOCH_K][day] > p_dic["STOCH-S Overbought"]) and (ti_df[s_STOCH_D][day] > p_dic["STOCH-S Overbought"])):

                    [cross_test, cross_direction] = lib_general_ops.has_crossed(ti_df[s_STOCH_K][previous_day], ti_df[s_STOCH_K][day], ti_df[s_STOCH_D][previous_day], ti_df[s_STOCH_D][day])

            if cross_test and cross_direction == '+' and (ti_df[s_STOCH_K][day] < p_dic["STOCH-S Oversold"] or (ti_df[s_STOCH_D][day]) < p_dic["STOCH-S Oversold"]):
                ta_indicator = p_dic['Non-trending indicator']
                trading_signal_long = 'buy'
                trading_signal_short = 'sell'

            if cross_test and cross_direction == '-' and (ti_df[s_STOCH_K][day] > p_dic["STOCH-S Overbought"] or (ti_df[s_STOCH_D][day]) > p_dic["STOCH-S Overbought"]) :
                ta_indicator = p_dic['Non-trending indicator']
                trading_signal_long = 'sell'
                trading_signal_short = 'buy'

        # Custom parameters
        if cross_test:
            custom_dic['TA indicator'] = ta_indicator
            custom_dic['Trading signal long'] = trading_signal_long
            custom_dic['Trading signal short'] = trading_signal_short
            custom_dic[s_DI_minus] = ti_df[s_DI_minus][day]
            custom_dic[s_ADX] = ti_df[s_ADX][day]
            if p_dic['Trending indicator'] == 'SMA':
                custom_dic[s_SMA_fast] = ti_df[s_SMA_fast][day]
                custom_dic[s_SMA_slow] = ti_df[s_SMA_slow][day]
            if p_dic['Non-trending indicator'] == 'STOCH-S':
                custom_dic[s_STOCH_K] = ti_df[s_STOCH_K][day]
                custom_dic[s_STOCH_D] = ti_df[s_STOCH_D][day]
                custom_dic[s_DI_plus] = ti_df[s_DI_plus][day]

    return custom_dic


def algorithm_SMA(p_dic, eq, day):
    # Get technical indicators
    ti_df = eq.get_technical_indicators()
    p_fast = p_dic["SMA fast period"]
    p_slow = p_dic["SMA slow period"]
    s_SMA_fast = "SMA_{}".format(p_fast)
    s_SMA_slow = "SMA_{}".format(p_slow)
    ti_df[s_SMA_fast] = eq.get_SMA(int(p_fast))
    ti_df[s_SMA_slow] = eq.get_SMA(int(p_slow))

    # Initialise remaining variables
    previous_day = eq.get_previous_day(day)
    custom_dic = {}
    nan_in_data = False

    # Run algorithm
    if not nan_in_data:
        # Determine buy and sell signals
        trading_signal_long = ''
        trading_signal_short = ''
        [cross_test, cross_direction] = lib_general_ops.has_crossed(ti_df[s_SMA_fast][previous_day], ti_df[s_SMA_fast][day], ti_df[s_SMA_slow][previous_day], ti_df[s_SMA_slow][day])

        if cross_test and cross_direction == '+':
            trading_signal_long = 'buy'
            trading_signal_short = 'sell'

        if cross_test and cross_direction == '-':
            trading_signal_long = 'sell'
            trading_signal_short = 'buy'

        # Custom parameters
        if cross_test:
            custom_dic['Trading signal long'] = trading_signal_long
            custom_dic['Trading signal short'] = trading_signal_short
            custom_dic[s_SMA_fast] = ti_df[s_SMA_fast][day]
            custom_dic[s_SMA_slow] = ti_df[s_SMA_slow][day]

    return custom_dic


def algorithm_SMA_MACD(p_dic, eq, day):
    # Get technical indicators
    ti_df = eq.get_technical_indicators()
    p_fast = p_dic["SMA fast period"]
    p_slow = p_dic["SMA slow period"]
    s_SMA_fast = "SMA_{}".format(p_fast)
    s_SMA_slow = "SMA_{}".format(p_slow)
    ti_df[s_SMA_fast] = eq.get_SMA(int(p_fast))
    ti_df[s_SMA_slow] = eq.get_SMA(int(p_slow))

    p_fast = p_dic["MACD fast period"]
    p_slow = p_dic["MACD slow period"]
    p_signal = p_dic["MACD signal period"]
    s_MACD = "MACD_{}_{}".format(p_fast, p_slow)
    s_MACD_signal = "MACD_signal_{}".format(p_signal)
    s_MACD_hist = "MACD_hist"
    ti_df[s_MACD], ti_df[s_MACD_signal], ti_df[s_MACD_hist] = eq.get_MACD(int(p_fast), int(p_slow), int(p_signal))

    # Initialise remaining variables
    previous_day = eq.get_previous_day(day)
    custom_dic = {}
    nan_in_data = False

    # Run algorithm
    if not nan_in_data:
        # Determine buy and sell signals
        trading_signal_long = ''
        trading_signal_short = ''
        [cross_test, cross_direction] = lib_general_ops.has_crossed(ti_df[s_SMA_fast][previous_day], ti_df[s_SMA_fast][day], ti_df[s_SMA_slow][previous_day], ti_df[s_SMA_slow][day])

        if cross_test and cross_direction == '+' and ti_df[s_MACD][day] > ti_df[s_MACD_signal][day]:
            trading_signal_long = 'buy'
            trading_signal_short = 'sell'

        if cross_test and cross_direction == '-' and ti_df[s_MACD][day] < ti_df[s_MACD_signal][day]:
            trading_signal_long = 'sell'
            trading_signal_short = 'buy'

        # Custom parameters
        if cross_test:
            custom_dic['Trading signal long'] = trading_signal_long
            custom_dic['Trading signal short'] = trading_signal_short
            custom_dic[s_SMA_fast] = ti_df[s_SMA_fast][day]
            custom_dic[s_SMA_slow] = ti_df[s_SMA_slow][day]
            custom_dic[s_MACD] = ti_df[s_MACD][day]
            custom_dic[s_MACD_signal] = ti_df[s_MACD_signal][day]

    return custom_dic