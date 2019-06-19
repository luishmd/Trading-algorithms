# Metadata
#=========
__author__ = 'Luis Domingues'

# Description
#============
# Library that provides datetime operations

# Notes
#======


# Known issues/enhancements
#==========================


#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
from datetime import datetime, timedelta, date
import time


#----------------------------------------------------------------------------------------
# FORMATS
#----------------------------------------------------------------------------------------
t_format_source = "%H:%M:%S"
d_t_divider_source = "T"
d_format_source = "%Y-%m-%d"

t_format_print = "%H:%M:%S"
d_format_print = "%d %B %Y"

#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def create_datetime_object(date_time_tzinfo_str, date_format = d_format_source, time_format = t_format_source, divider = d_t_divider_source):
    """
    Function that returns the datetime object (e.g. input 2017-03-08T19:29:25.000Z)
    """
    format = date_format + divider + time_format
    try: # if it has tzinfo
        [date_time_str, tzinfo_str] = date_time_tzinfo_str.split(".")
        datetime_obj = datetime.strptime(date_time_str, format)
    except: # otherwise
        date_time_str = date_time_tzinfo_str
        datetime_obj = datetime.strptime(date_time_str, format)
    return datetime_obj


def create_date_object(datetime_obj):
    """
    Function that returns the date object
    """
    date_obj = datetime.date(datetime_obj)
    return date_obj


def create_time_object(datetime_obj):
    """
    Function that returns the time object
    """
    time_obj = datetime.time(datetime_obj)
    return time_obj


def create_timedelta_object(delta_t_seconds):
    """
    Function that returns the timedelta object for a given amount of seconds
    """
    timedelta_obj = timedelta(seconds=delta_t_seconds)
    return timedelta_obj


def get_current_time_str(time_format = t_format_source):
    """
    Function that returns the current time
    """
    current_time_str =  time.strftime(time_format)
    return current_time_str


def get_current_date_str(date_format = d_format_source):
    """
    Function that returns the current date as a string
    """
    date_obj = date.today()
    current_date_str =  date_obj.strftime(date_format)
    return current_date_str


def get_date_week_number(date_obj):
    """
    Function that returns the current week number
    """
    [iso_year, iso_week_no, iso_week_day] = date.isocalendar(date_obj)
    return iso_week_no


def get_current_datetime_str(date_format = d_format_source, time_format = t_format_source, divider = d_t_divider_source):
    """
    Function that returns the current date and time in the standard format
    """
    current_time_str = get_current_time_str(time_format)
    current_date_str = get_current_date_str(date_format)
    current_datetime_str = current_date_str + divider + current_time_str
    return current_datetime_str



def format_date(datetime_obj, date_format = d_format_print):
    """
    Function that formats the date from a datetime object
    """
    date_str = datetime_obj.strftime(date_format)
    return date_str


def format_time(datetime_obj, time_format = t_format_print):
    """
    Function that formats the time from a datetime object
    """
    time_str = datetime_obj.strftime(time_format)
    return time_str


def calc_start_time(activity_end_time_obj, delta_t_seconds):
    """
    Function that calculates the start time (datetime object) given a delta t relative to the end time of the activity
    """
    delta = create_timedelta_object(delta_t_seconds)
    start_time_obj = activity_end_time_obj - delta
    return start_time_obj


#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------
if __name__ == "__main__":
    now = get_current_datetime_str()
    dt= create_datetime_object(now)
    d = create_date_object(dt)
    print(d)
    Nw = get_date_week_number(d)
    print(Nw)
    pass
