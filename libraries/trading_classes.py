__author__ = "Luis Domingues"


#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import math
import lib_general_ops
import talib
import pandas as pd
import lib_trading_print_results as lib_write
import lib_excel_ops_openpyxl as lib_excel

#----------------------------------------------------------------------------------------
# CLASSES
#----------------------------------------------------------------------------------------
class Stock(object):
    """ Creates a stock object """
    def __init__(self, ticker, name, history_df):
        self.name = name
        self.ticker = ticker
        self.history_df = history_df
        self.ti_df = pd.DataFrame(history_df.index)
        self.ti_df = self.ti_df.set_index('Date')

    def __str__(self):
        return "Stock: %s" % self.name

    def get_ticker(self):
        return self.ticker

    def get_name(self):
        return self.name

    def get_dataset(self):
        return self.history_df

    def get_previous_day(self, curr_day):
        return lib_general_ops.get_previous_date(self.history_df, curr_day)

    def get_next_day(self, curr_day):
        return lib_general_ops.get_next_date(self.history_df, curr_day)

    def get_technical_indicators(self):
        return self.ti_df

    def get_SMA(self, p):
        s = "SMA_{}".format(str(p))
        if s not in self.ti_df.columns:
            self.ti_df[s] = talib.SMA(self.history_df['Close'], p)
        return self.ti_df[s]

    def get_SMA_turnover(self, p):
        s = "SMA_{}_turnover".format(str(p))
        if s not in self.ti_df.columns:
            self.ti_df[s] = talib.SMA(self.history_df['Turnover'], p)
        return self.ti_df[s]

    def get_SMA_price(self, p):
        s = "SMA_{}_price".format(str(p))
        if s not in self.ti_df.columns:
            self.ti_df[s] = talib.SMA(self.history_df['Low'], p)
        return self.ti_df[s]

    def get_MACD(self, fast_period=12, slow_period=26, signal_period=9):
        s_MACD = "MACD_{}_{}".format(str(fast_period),str(slow_period))
        s_signal = "MACD_signal_{}".format(str(signal_period))
        s_hist = "MACD_hist"
        if s_MACD not in self.ti_df.columns:
            self.ti_df[s_MACD], self.ti_df[s_signal], self.ti_df[s_hist] = talib.MACD(self.history_df['Close'], fast_period, slow_period, signal_period)
        return self.ti_df[s_MACD], self.ti_df[s_signal], self.ti_df[s_hist]

    def get_RSI(self, p=14):
        s = "RSI_{}".format(str(p))
        if s not in self.ti_df.columns:
            self.ti_df[s] = talib.RSI(self.history_df['Close'], p)
        return self.ti_df[s]

    def get_STOCH(self, fastk_period=10, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
        s_slowk = "STOCH_K_{}_{}_{}".format(fastk_period, slowk_period, slowd_period)
        s_slowd = "STOCH_D_{}_{}_{}".format(fastk_period, slowk_period, slowd_period)
        if (s_slowk not in self.ti_df.columns) or (s_slowd not in self.ti_df.columns):
            [self.ti_df[s_slowk], self.ti_df[s_slowd]] = talib.STOCH(self.history_df['High'], self.history_df['Low'], self.history_df['Close'],
                                                                     fastk_period, slowk_period,
                                                                     slowk_matype,
                                                                     slowd_period, slowd_matype)
        return self.ti_df[s_slowk], self.ti_df[s_slowd]

    def get_DI_positive(self, p=14):
        s = "DI_plus_{}".format(str(p))
        if s not in self.ti_df.columns:
            self.ti_df[s] = talib.PLUS_DI(self.history_df['High'], self.history_df['Low'], self.history_df['Close'], p)
        return self.ti_df[s]

    def get_DI_negative(self, p=14):
        s = "DI_minus_{}".format(str(p))
        if s not in self.ti_df.columns:
            self.ti_df[s] = talib.MINUS_DI(self.history_df['High'], self.history_df['Low'], self.history_df['Close'], p)
        return self.ti_df[s]

    def get_ADX(self, p=14):
        s = "ADX_{}".format(str(p))
        if s not in self.ti_df.columns:
            self.ti_df[s] = talib.ADX(self.history_df['High'], self.history_df['Low'], self.history_df['Close'], p)
        return self.ti_df[s]


class Order(object):
    """Creates an order class"""
    def __init__(self, id, custom_dic, stock_obj, position_type, order_type, date_obj, price, stop_loss_price=None, money_typical_trade=None, commission_per_op=5):
        self.id = id
        self.stock_obj = stock_obj
        self.name = stock_obj.get_name()
        self.position_type = position_type # either 'long' or 'short'
        self.order_type = order_type # either 'buy' or 'sell'
        self.stop_loss_price = stop_loss_price
        self.date = date_obj
        self.price = price
        self.custom_dic = custom_dic
        if money_typical_trade != None:
            self.amount = math.floor((money_typical_trade-commission_per_op)/price)

    def __str__(self):
        s = '%s %s | %s - %s | %s | Price: %0.4f CURR/unit' % (str(self.id), self.name, self.position_type, self.order_type, self.date, self.price)
        if self.stop_loss_price != None:
            s += ' | Stop: %0.4f CURR/unit' % self.stop_loss_price
        return s

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_position_type(self):
        return self.position_type

    def get_order_type(self):
        return self.order_type

    def get_amount(self):
        a = None
        try:
            a = self.amount
        except:
            pass
        return a

    def get_price(self):
        return self.price

    def get_date(self):
        return self.date

    def get_stop_loss(self):
        return self.stop_loss_price

    def get_stock(self):
        return self.stock_obj

    def get_custom(self):
        return self.custom_dic


class Orders_table:
    """Creates an order table class"""
    def __init__(self, name):
        self.name = name
        self.orders_list = []
        self.n_orders = 0

    def __str__(self):
        s = ''
        for order in self.orders_list:
            s += order.__str__() + '\n'
        return s

    def get_order_id(self, id):
        order = None
        for order in self.orders_list:
            if order.get_id() == id:
                break
        return order

    def get_number_orders(self):
        return self.n_orders

    def is_empty(self):
        if self.n_orders == 0:
            return True
        else:
            return False

    def get_orders_list(self):
        return self.orders_list

    def create_order(self, custom_dic, stock_obj, position_type, order_type, date_obj, price, stop_loss_price=None, money_typical_trade=None, commission_per_op=5):
        order_inst = Order(self.n_orders, custom_dic, stock_obj, position_type, order_type, date_obj, price, stop_loss_price, money_typical_trade, commission_per_op)
        self.orders_list.append(order_inst)
        self.n_orders = self.n_orders + 1


class Position(object):
    """Creates a position class"""
    def __init__(self, id, custom_dic_entry, stock_obj_entry, position_type, money_typical_trade, date_obj_entry, price_entry, stop_loss_price, comission_per_op=5):
        self.id = id
        self.stock_obj_entry = stock_obj_entry
        self.name = stock_obj_entry.get_name()
        self.position_type = position_type
        self.stop_loss_price = stop_loss_price
        self.date_entry = date_obj_entry
        self.price_entry = price_entry
        self.custom_dic_entry = custom_dic_entry
        self.amount = math.floor((money_typical_trade-comission_per_op)/price_entry)
        self.money_entry = self.amount*self.price_entry + comission_per_op

        self.state = 'open'
        self.comission_per_op = comission_per_op

    def __str__(self):
        s = ''
        if self.state == 'open':
            s += '%s %s | %s | Entry: %s | Price (entry): %0.4f CURR/unit | Stop: %0.4f CURR/unit' % (str(self.id), self.name, self.position_type, self.date_entry, self.price_entry, self.stop_loss_price)
        if self.state == 'closed':
            s += '%s %s | %s | Entry: %s | Price (entry): %0.4f CURR/unit | Stop: %0.4f CURR/unit | Exit: %s | Price (exit): %0.4f CURR/unit' % (str(self.id), self.name, self.position_type, self.date_entry, self.price_entry, self.stop_loss_price,self.date_exit, self.price_exit)
        return s

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_state(self):
        return self.state

    def get_position_type(self):
        return self.position_type

    def get_amount(self):
        return self.amount

    def get_price_entry(self):
        return self.price_entry

    def get_price_exit(self):
        return self.price_exit

    def get_date_entry(self):
        return self.date_entry

    def get_date_exit(self):
        return self.date_exit

    def get_stop_loss(self):
        return self.stop_loss_price

    def get_stock_entry(self):
        return self.stock_obj_entry

    def get_stock_exit(self):
        return self.stock_obj_exit

    def get_custom_entry(self):
        return self.custom_dic_entry

    def get_custom_exit(self):
        return self.custom_dic_exit

    def get_money_entry(self):
        return self.money_entry

    def get_money_exit(self):
        return self.money_exit

    # There is no open_position method because instantiating this class is opening a position
    def close_position(self, custom_dic_exit, stock_obj_exit, date_obj_exit, price_exit):
        self.date_exit = date_obj_exit
        self.price_exit = price_exit
        self.stock_obj_exit = stock_obj_exit
        self.custom_dic_exit = custom_dic_exit
        self.state = 'closed'
        self.money_exit = self.amount*self.price_exit - self.comission_per_op
        if self.position_type == 'long':
            self.profit_losses = self.money_exit - self.money_entry
        else: # short
            self.profit_losses = -(self.money_exit - self.money_entry)
        self.profit_losses_pct = self.profit_losses/self.money_entry*100
        return None

    def get_profit_losses(self):
        if self.state == 'closed':
            return self.profit_losses
        else:
            print('Position (%s, %s) is still open.' % (self.name, str(self.id)))
            return None

    def get_profit_losses_pct(self):
        if self.state == 'closed':
            return self.profit_losses_pct
        else:
            print('Position (%s, %s) is still open.' % (self.name, str(self.id)))
            return None

    def check_stop_loss(self, custom_dic_exit, stock_obj, date_obj, price):
        trade_closed = False
        if (self.position_type == 'long') and (price <= self.stop_loss_price):
            custom_dic_exit['Stop Loss'] = 'Triggered'
            self.close_position(custom_dic_exit, stock_obj, date_obj, self.stop_loss_price)
            trade_closed = True
        if (self.position_type == 'short') and (price >= self.stop_loss_price):
            custom_dic_exit['Stop Loss'] = 'Triggered'
            self.close_position(custom_dic_exit, stock_obj, date_obj, self.stop_loss_price)
            trade_closed = True
        return trade_closed


class Positions_table(object):
    """Creates a trades table class"""
    def __init__(self, stock_obj, positions_type):
        self.name = stock_obj.get_name()
        self.positions_list = []
        self.n_positions = 0
        self.positions_type = positions_type
        self.total_money_entry = 0
        self.total_money_exit = 0

    def __str__(self):
        s = ''
        for position in self.positions_list:
            s += position.__str__() + '\n'
        return s

    def is_empty(self):
        if self.n_positions == 0:
            return True
        else:
            return False

    def get_positions_list(self):
        return self.positions_list

    def get_positions_type(self):
        return self.positions_type

    def get_name(self):
        return self.name

    def create_position(self, custom_dic_entry, stock_obj, position_type, money_typical_trade, entry_date_obj, entry_price, stop_loss_price, comission_per_op=5):
        pos_inst = Position(self.n_positions, custom_dic_entry, stock_obj, position_type, money_typical_trade, entry_date_obj, entry_price, stop_loss_price, comission_per_op=comission_per_op)
        self.positions_list.append(pos_inst)
        self.n_positions = self.n_positions + 1
        self.total_money_entry += pos_inst.get_money_entry()
        return None

    def check_stop_loss(self, custom_dic_exit, stock_obj, date_obj, price):
        for position in self.positions_list:
            if position.get_state() == 'open':
                is_closed = position.check_stop_loss(custom_dic_exit, stock_obj, date_obj, price)
                if is_closed:
                    self.total_money_exit += position.get_money_exit()
        return None

    def close_opened_positions(self, custom_dic_exit, stock_obj_exit, position_type, date_obj_exit, price_exit):
        for position in self.positions_list:
            if (position.get_state() == 'open') and (position.get_position_type() == position_type):
                position.close_position(custom_dic_exit, stock_obj_exit, date_obj_exit, price_exit)
                self.total_money_exit += position.get_money_exit()
        return None

    def get_total_money_entry(self, Only_closed_positions=True):
        total_money_entry = 0
        for position in self.positions_list:
            if position.get_state() == 'closed' or not Only_closed_positions:
                total_money_entry += position.get_money_entry()
        self.total_money_entry = total_money_entry
        return total_money_entry

    def get_profit_losses(self, Only_closed_positions=True):
        total_profit_losses = 0
        for position in self.positions_list:
            if position.get_state() == 'closed' or not Only_closed_positions:
                total_profit_losses += position.get_profit_losses()
        self.total_profit_losses = total_profit_losses
        return total_profit_losses

    def get_profit_losses_pct(self):
        total_profit_losses = self.get_profit_losses()
        total_money_entry = self.get_total_money_entry()
        try:
            total_profit_losses_pct = float(total_profit_losses)/float(total_money_entry) * 100
        except ZeroDivisionError:
            total_profit_losses_pct = 0
        self.total_profit_losses_pct = total_profit_losses_pct
        return total_profit_losses_pct


class Trading_Manager(object):
    """Creates a Trading_Manager class"""
    def __init__(self, params_dic):
        # For analysis
        self.p_dic = params_dic
        if params_dic['Mode'] == 'Analysis':
            self.ot = Orders_table("Orders")
        # For backtesting
        if (params_dic['Mode'] == 'Backtesting') or (params_dic['Mode'] == 'Optimization'):
            self.pt_long = {}
            if not params_dic['Only long positions']:
                self.pt_short = {}

        self.value_typical_trade = params_dic['Typical trade value']
        self.commission_value = params_dic['Commission per trade']

    def update_params_dic(self, p_dic):
        self.p_dic = p_dic

    def manage_orders_positions(self, custom_dic, stock_obj, day):
        price = stock_obj.get_dataset()['Close'][day]
        if self.p_dic['Mode'] == 'Analysis':
            # Long
            if custom_dic['Trading signal long'] == 'buy':
                stop_loss = price * (1.0 - self.p_dic['Max losses pct'] / 100.0)
                self.ot.create_order(custom_dic, stock_obj, 'long', 'buy', day, price, stop_loss_price=stop_loss, money_typical_trade=self.value_typical_trade, commission_per_op=self.commission_value)
            if custom_dic['Trading signal long'] == 'sell':
                self.ot.create_order(custom_dic, stock_obj, 'long', 'sell', day, price, money_typical_trade=self.value_typical_trade)

            # Short
            if not self.p_dic['Only long positions']:
                if custom_dic['Trading signal short'] == 'buy':
                    stop_loss = price * (1.0 + self.p_dic['Max losses pct'] / 100.0)
                    self.ot.create_order(custom_dic, stock_obj, 'short', 'buy', day, price, stop_loss_price=stop_loss, money_typical_trade=self.value_typical_trade, commission_per_op=self.commission_value)
                if custom_dic['Trading signal short'] == 'sell':
                    self.ot.create_order(custom_dic, stock_obj, 'short', 'sell', day, price)

        if (self.p_dic['Mode'] == 'Backtesting') or (self.p_dic['Mode'] == 'Optimization'):
            # Long
            k = stock_obj.get_name() + '-long'
            if k not in self.pt_long.keys():
                self.pt_long[k] = Positions_table(stock_obj, 'long')
            self.pt_long[k].check_stop_loss(custom_dic, stock_obj, day, price)
            if custom_dic['Trading signal long'] == 'buy':
                stop_loss = price * (1.0 - self.p_dic['Max losses pct'] / 100.0)
                self.pt_long[k].create_position(custom_dic, stock_obj, 'long', self.value_typical_trade, entry_date_obj=day, entry_price=price, stop_loss_price=stop_loss)
            if custom_dic['Trading signal long'] == 'sell':
                self.pt_long[k].close_opened_positions(custom_dic, stock_obj, 'long', date_obj_exit=day, price_exit=price)

            # Short
            k = stock_obj.get_name() + '-short'
            if not self.p_dic['Only long positions']:
                if k not in self.pt_short.keys():
                    self.pt_short[k] = Positions_table(stock_obj, 'short')
                self.pt_short[k].check_stop_loss(custom_dic, stock_obj, day, price)
                if custom_dic['Trading signal short'] == 'buy':
                    stop_loss = price * (1.0 + self.p_dic['Max losses pct'] / 100.0)
                    self.pt_short[k].create_position(custom_dic, stock_obj, 'short', self.value_typical_trade, entry_date_obj=day, entry_price=price, stop_loss_price=stop_loss)
                if custom_dic['Trading signal short'] == 'sell':
                    self.pt_short[k].close_opened_positions(custom_dic, stock_obj, 'short', date_obj_exit=day, price_exit=price)

    def write_results(self, write_results=True, delete_unused=True):
        if write_results:
            wb = lib_excel.open_workbook(self.p_dic['Excel output file'])
            assert wb
            # Delete unused sheets
            if delete_unused:
                ws_list = wb.get_sheet_names()
                if self.p_dic['Mode'] == 'Analysis':
                    remove_list = ['Backtesting', 'Optimization']
                    for r in remove_list:
                        if r in ws_list:
                            wb.remove_sheet(wb.get_sheet_by_name(r))
                if self.p_dic['Mode'] == 'Backtesting':
                    remove_list = ['Execution', 'Optimization']
                    for r in remove_list:
                        if r in ws_list:
                            wb.remove_sheet(wb.get_sheet_by_name(r))
                if self.p_dic['Mode'] == 'Optimization':
                    remove_list = ['Execution', 'Backtesting']
                    for r in remove_list:
                        if r in ws_list:
                            wb.remove_sheet(wb.get_sheet_by_name(r))

            # Write results
            table = None
            if self.p_dic['Mode'] == 'Analysis':
                table = self.ot
            if (self.p_dic['Mode'] == 'Backtesting') or (self.p_dic['Mode'] == 'Optimization'):
                table = self.pt_long
                if not self.p_dic['Only long positions']:
                    for k in self.pt_short.keys():
                        table[k] = self.pt_short[k]
            if table:
                lib_write.write_results_to_excel(self.p_dic, wb, table, write_params=True, write_table=True)
                output_file = self.p_dic['Excel output file']
                lib_excel.save_workbook(wb, output_file)
            # Close necessary files
            wb.close()
