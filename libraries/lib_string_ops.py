# Metadata
#=========
__author__ = 'Luis Domingues'

# Description
#============
# Library that provides string operations

# Notes
#======
#

# Known issues/enhancements
#==========================
#

#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------
# INPUTS
#----------------------------------------------------------------------------------------
include_char_list = ["-", " ", "_", ".", "!"]

#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def is_alpha_numeric(string):
    """
    Function that checks whether the input string only contains alphanumeric characters
    """
    return string.isalnum()


def filter_string_alnum(string):
    """
    Function that filters a given string of all non-alphanumeric characters
    """
    return ''.join(char for char in string if char.isalnum())


def filter_string(string, char_list=include_char_list):
    """
    Function that filters a given string of all non-alphanumeric characters plus any characters that are not in an exception list.
    """
    return ''.join(char for char in string if char.isalnum() or char in char_list)

#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------
if __name__ == "__main__":
    pass