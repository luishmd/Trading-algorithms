__author__ = "Luis Domingues"
__maintainer__ = "Luis Domingues"
__email__ = "luis.hmd@gmail.com"

#----------------------------------------------------------------------------------------
# Notes
#----------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import math
import lib_general_ops

#----------------------------------------------------------------------------------------
# CLASSES
#----------------------------------------------------------------------------------------
class Stock(object):
    """ Creates a stock object """
    def __init__(self, name, database_code, dataset):
        self.name = name
        self.database_code = database_code
        self.quandl_code = database_code + '/' + name
        self.dataset = dataset

    def __str__(self):
        return "Stock: %s" % self.name

    def get_name(self):
        return self.name

    def get_database_code(self):
        return self.database_code

    def get_dataset(self):
        return self.dataset

    def get_quandl_code(self):
        return self.quandl_code

    def set_trend(self, trend_int):
        """
        :param trend_int (either -1; 0; 1:
        :return:
        """
        self.trend = trend_int

    def get_trend(self):
        return self.trend

    def set_MA_5(self, MA_5_value):
        self.MA_5 = MA_5_value

    def get_MA_5(self):
        return self.MA_5

    def set_MA_20(self, MA_20_value):
        self.MA_20 = MA_20_value

    def get_MA_20(self):
        return self.MA_20

    def set_MA_50(self, MA_50_value):
        self.MA_50 = MA_50_value

    def get_MA_50(self):
        return self.MA_50

    def set_MA_100(self, MA_50_value):
        self.MA_100 = MA_50_value

    def get_MA_100(self):
        return self.MA_100

    def set_MA_200(self, MA_200_value):
        self.MA_200 = MA_200_value

    def get_MA_200(self):
        return self.MA_200

    def set_RSI(self, RSI_value):
        self.RSI = RSI_value

    def get_RSI(self):
        return self.RSI

    def set_STOCH_S(self, STOCH_S_K_value, STOCH_S_D_value):
        self.STOCH_S_D = STOCH_S_D_value
        self.STOCH_S_K = STOCH_S_K_value

    def get_STOCH_S(self):
        return [self.STOCH_S_K, self.STOCH_S_D]

    def set_DI_positive(self, DI_plus_value):
        self.DI_plus = DI_plus_value

    def get_DI_positive(self):
        return self.DI_plus

    def set_DI_negative(self, DI_minus_value):
        self.DI_minus = DI_minus_value

    def get_DI_negative(self):
        return self.DI_minus

    def set_ADX(self, ADX_value):
        self.ADX = ADX_value

    def get_ADX(self):
        return self.ADX

    def set_MA_turnover(self, MA_turnover_value):
        self.MA_turnover = MA_turnover_value

    def get_MA_turnover(self):
        return self.MA_turnover

    def set_MA_price(self, MA_price_value):
        self.MA_price = MA_price_value

    def get_MA_price(self):
        return self.MA_price


class Order(object):
    """Creates an order class"""
    def __init__(self, id, stock_obj, ta_indicator, position_type, order_type, date_obj, price, stop_loss_price=None, money_typical_trade=None, commission_per_op=5):
        self.id = id
        self.ta_indicator = ta_indicator
        self.stock_obj = stock_obj
        self.name = stock_obj.get_name()
        self.position_type = position_type # either 'long' or 'short'
        self.order_type = order_type # either 'buy' or 'sell'
        self.stop_loss_price = stop_loss_price
        self.date = date_obj
        self.price = price
        if money_typical_trade != None:
            self.amount = math.floor((money_typical_trade-commission_per_op)/price)

    def __str__(self):
        s = '%s %s | %s - %s | %s | Price: %0.4f EUR/unit' % (str(self.id), self.name, self.position_type, self.order_type, self.date, self.price)
        if self.stop_loss_price != None:
            s += ' | Stop: %0.4f EUR/unit' % self.stop_loss_price
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

    def get_ta_indicator(self):
        return self.ta_indicator


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

    def create_order(self, id, stock_obj, ta_indicator, position_type, order_type, date_obj, price, stop_loss_price=None, money_typical_trade=None, commission_per_op=5):
        order_inst = Order(id, stock_obj, ta_indicator, position_type, order_type, date_obj, price, stop_loss_price, money_typical_trade, commission_per_op)
        self.orders_list.append(order_inst)
        self.n_orders = self.n_orders + 1


class Position(object):
    """Creates a position class"""
    def __init__(self, id, stock_obj_entry, ta_indicator_entry, position_type, money_typical_trade, date_obj_entry, price_entry, stop_loss_price, comission_per_op=5):
        self.id = id
        self.stock_obj_entry = stock_obj_entry
        self.name = stock_obj_entry.get_name()
        self.ta_indicator_entry = ta_indicator_entry
        self.position_type = position_type
        self.stop_loss_price = stop_loss_price
        self.date_entry = date_obj_entry
        self.price_entry = price_entry
        self.comission_per_op = comission_per_op
        self.state = 'open'
        self.amount = math.floor((money_typical_trade-self.comission_per_op)/price_entry)
        self.money_entry = self.amount*self.price_entry + self.comission_per_op

    def __str__(self):
        s = ''
        if self.state == 'open':
            s += '%s %s | %s | Entry: %s | Price (entry): %0.4f EUR/unit | Stop: %0.4f EUR/unit' % (str(self.id), self.name, self.position_type, self.date_entry, self.price_entry, self.stop_loss_price)
        if self.state == 'closed':
            s += '%s %s | %s | Entry: %s | Price (entry): %0.4f EUR/unit | Stop: %0.4f EUR/unit | Exit: %s | Price (exit): %0.4f EUR/unit' % (str(self.id), self.name, self.position_type, self.date_entry, self.price_entry, self.stop_loss_price,self.date_exit, self.price_exit)
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

    def get_ta_indicator_entry(self):
        return self.ta_indicator_entry

    def get_ta_indicator_exit(self):
        return self.ta_indicator_exit

    def get_money_entry(self):
        return self.money_entry

    def get_money_exit(self):
        return self.money_exit

    # There is no open_position method because instantiating this class is opening a position
    def close_position(self, stock_obj_exit, ta_indicator_exit, date_obj_exit, price_exit):
        self.date_exit = date_obj_exit
        self.price_exit = price_exit
        self.stock_obj_exit = stock_obj_exit
        self.ta_indicator_exit = ta_indicator_exit
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

    def check_stop_loss(self, stock_obj, ta_indicator_exit, date_obj, price):
        trade_closed = False
        if (self.position_type == 'long') and (price <= self.stop_loss_price):
            self.close_position(stock_obj, ta_indicator_exit, date_obj, self.stop_loss_price)
            trade_closed = True
        if (self.position_type == 'short') and (price >= self.stop_loss_price):
            self.close_position(stock_obj, ta_indicator_exit, date_obj, self.stop_loss_price)
            trade_closed = True
        return trade_closed


class Positions_table(object):
    """Creates a trades table class"""
    def __init__(self, stock_name, positions_type):
        self.name = stock_name
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

    def create_position(self, id, stock_obj, ta_indicator_entry, position_type, money_typical_trade, entry_date_obj, entry_price, stop_loss_price, comission_per_op=5):
        trade_inst = Position(id, stock_obj, ta_indicator_entry, position_type, money_typical_trade, entry_date_obj, entry_price, stop_loss_price, comission_per_op=comission_per_op)
        self.positions_list.append(trade_inst)
        self.n_positions = self.n_positions + 1
        self.total_money_entry += trade_inst.get_money_entry()
        return None

    def check_stop_loss(self, stock_obj, ta_indicator_exit, date_obj, price):
        for position in self.positions_list:
            if position.get_state() == 'open':
                is_closed = position.check_stop_loss(stock_obj, ta_indicator_exit, date_obj, price)
                if is_closed:
                    self.total_money_exit += position.get_money_exit()
        return None

    def close_opened_positions(self, stock_obj_exit, ta_indicator_exit, position_type, date_obj_exit, price_exit):
        for position in self.positions_list:
            if (position.get_state() == 'open') and (position.get_position_type() == position_type):
                position.close_position(stock_obj_exit, ta_indicator_exit, date_obj_exit, price_exit)
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
        total_profit_losses = self.get_profit_losses(self)
        total_money_entry = self.get_total_money_entry(self)
        try:
            total_profit_losses_pct = float(total_profit_losses)/float(total_money_entry) * 100
        except ZeroDivisionError:
            total_profit_losses_pct = 0
        self.total_profit_losses_pct = total_profit_losses_pct
        return total_profit_losses_pct


class Algorithm(object):
    """Creates a trades table class"""
    def __init__(self, params_dic, stock_name, stock_database, quandl_code, stock_ds):
        # For analysis
        self.ot = Orders_table(stock_name)
        self.order_id = 1
        # For backtesting
        self.pt_long = Positions_table(stock_name, 'long')
        self.pt_short = Positions_table(stock_name, 'short')
        self.position_id = 1

        self.value_typical_trade = params_dic['Typical trade value']
        self.commission_value = params_dic['Commission per trade']

        self.stock_database = stock_database
        self.quandl_code = quandl_code

        # Calculate start and end days for analysis
        self.start_date_obj = params_dic['Start date']
        self.end_date_obj = params_dic['End date']
        self.last_n_points = params_dic['Last N days']
        if params_dic['Mode'] == 'Analysis':
            [self.start_date_anal_obj, self.end_date_anal_obj] = lib_general_ops.get_analysis_time_interval(stock_ds['Last'], self.start_date_obj, self.end_date_obj,self.last_n_points)
        if params_dic['Mode'] == 'Backtesting':
            self.start_date_anal_obj = lib_general_ops.get_first_date(stock_ds['Last'])
            self.end_date_anal_obj = lib_general_ops.get_last_date(stock_ds['Last'])

    def set_stock_database(self, stock_database):
        self.stock_database = stock_database

    def set_quandl_codee(self, quandl_code):
        self.quandl_code = quandl_code

    def manage_orders_positions(self, params_dic, stock_obj, ta_indicator, trading_signal_long, trading_signal_short, stock_ds, day):
        if params_dic['Mode'] == 'Analysis':
            # Long
            if trading_signal_long == 'buy':
                stop_loss = stock_ds['Last'][day] * (1.0 - params_dic['Max losses pct'] / 100.0)
                self.ot.create_order(self.order_id, stock_obj, ta_indicator, 'long', trading_signal_long, day, stock_ds['Last'][day], stop_loss_price=stop_loss, money_typical_trade=self.value_typical_trade, commission_per_op=self.commission_value)
                self.order_id = self.order_id + 1
            if trading_signal_long == 'sell':
                self.ot.create_order(self.order_id, stock_obj, ta_indicator, 'long', trading_signal_long, day, stock_ds['Last'][day], money_typical_trade=self.value_typical_trade)
                self.order_id = self.order_id + 1

            # Short
            if (trading_signal_short == 'buy') and (params_dic['Only long positions'] == False):
                stop_loss = stock_ds['Last'][day] * (1.0 + params_dic['Max losses pct'] / 100.0)
                self.ot.create_order(self.order_id, stock_obj, ta_indicator, 'short', trading_signal_long, day, stock_ds['Last'][day], stop_loss_price=stop_loss, money_typical_trade=self.value_typical_trade, commission_per_op=self.commission_value)
                self.order_id = self.order_id + 1
            if (trading_signal_short == 'sell') and (params_dic['Only long positions'] == False):
                self.ot.create_order(self.order_id, stock_obj, ta_indicator, 'short', trading_signal_long, day, stock_ds['Last'][day])
                self.order_id = self.order_id + 1

        if params_dic['Mode'] == 'Backtesting':
            # Long
            self.pt_long.check_stop_loss(stock_obj, 'Stop loss', day, stock_ds['Low'][day])
            if trading_signal_long == 'buy':
                stop_loss = stock_ds['Last'][day] * (1.0 - params_dic['Max losses pct'] / 100.0)
                self.pt_long.create_position(self.position_id, stock_obj, ta_indicator, 'long', self.value_typical_trade, entry_date_obj=day, entry_price=stock_ds['Last'][day], stop_loss_price=stop_loss)
                self.position_id = self.position_id + 1
            if trading_signal_long == 'sell':
                self.pt_long.close_opened_positions(stock_obj, ta_indicator, 'long', date_obj_exit=day, price_exit=stock_ds['Last'][day])

            # Short
            self.pt_short.check_stop_loss(stock_obj, 'Stop loss', day, stock_ds['Low'][day])
            if (trading_signal_short == 'buy') and (params_dic['Only long positions'] == False):
                stop_loss = stock_ds['Last'][day] * (1.0 + params_dic['Max losses pct'] / 100.0)
                self.pt_short.create_position(self.position_id, stock_obj, ta_indicator, 'short', self.value_typical_trade, entry_date_obj=day, entry_price=stock_ds['Last'][day], stop_loss_price=stop_loss)
                self.position_id = self.position_id + 1
            if (trading_signal_short == 'sell') and (params_dic['Only long positions'] == False):
                self.pt_short.close_opened_positions(stock_obj, ta_indicator, 'short', date_obj_exit=day, price_exit=stock_ds['Last'][day])
        return [self.ot, self.pt_long, self.pt_short]