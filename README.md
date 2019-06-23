# Background
Implement knowledge of financial technical indicators to (hopefully) improve finances :)


# Description
Script used for analysing stocks using different algorithms. It provides an initial screening and filters only stocks with certain user-defined parameters, that can be later analysed by the user in more detail in an appropriate software.

The script implements the following steps:
1. Read/update data from a database (data from quandl' Euronext database)
2. Read a set of user inputs
3. Apply filters to stocks, such as no longer traded stocks, stocks with low turnover, etc)
4. For the subset of stock candidates, run the trading algorithm, defined/selected by the user, which select only appropriate stocks
5. Write the set of appropriate stocks to an excel file, so that they can be analysed by the user


## Output
Excel file with the stocks matching user-defined criteria. The excel file where results are stored is copied from a defined template (set in inputs.yaml), to a subdirectory in 'outputs/'. The current date_time is used to generate the name of the subdirectory and output file. This prevents accidental overwriting.

## Input data
1. Execution inputs. See file 'inputs.yaml'
    - *Update data*: updates data in the database -- Possible values: True / False --
    - *Run algorithm*: chooses whether or not to run the algorithm -- Possible values: True / False --
	- *Output template*: name of the template to use for results -- Possible values: any *.xlsx file --
    - *Mode*: chooses to analyze data or to do a backtest -- Possible values: 'Analysis' / 'Backtesting' -- 
    - *Stock list*: a list of stocks to analyse. Empty means all stocks -- Possible values: None / a list of quandl stock codes ['BCP'] / a list name, which should be defined in this file e.g. psi20 --
    - *Format date string*: format for start and end dates -- Possible values: any string that can be interpreted as a data by datetime --
    - *Start date*: start date of analysis. If empty is the first date available for a given stock -- Possible values: Any string in the format defined --
    - *End date*: end date of analysis. If empty is the last date available for a given stock -- Possible values: Any string in the format defined --
    - *Last N days*: corresponds to the number of last points to consider for the analysis, e.g. only last 200 points. Calculates start date accordingly. -- Possible values: an integer --
    - *Algorithm name*: name of trade function used  -- Any name provided there is a function with the same name --
    - *Filters list*: list of filters to apply to stocks -- Possible values: dataset_size / dataset_old / turnover / price --

2. Backtesting inputs. See file 'inputs.yaml'
    - *Backtesting print positions*: more verbose when backtesting -- Possible values: True / False --
    - *Only long positions*: only considers long positions  -- Possible values: True / False --
    - *Max losses pct*: used to set a stop loss when backtesting  -- Possible values: float (percentage) --
    - *Typical trade value*: typical value invested in a trade  -- Possible values: float (in euros) --
    - *Commission per trade*: typical commission per trade  -- Possible values: float (in euros) --

3. Filter inputs. See file 'inputs.yaml'
    - *Min turnover*: minimum turnover value  -- Possible values: float (in EUR) -- 
    - *Max price*: maximum price per share  -- Possible values: float (in EUR) --
    - *Min dataset size*: minimum days in the dataset for a given stock -- Possible values: integer --
    - *Max days since update*: maximum days since update -- Possible values: integer --
    
4. Algorithm 1 inputs. See file 'inputs.yaml'
    - *Trending indicator*: indicator to use to determine buy/sell signals when trending -- Possible values: 'MA5/20' / 'MA20/50' --
    - *Non-trending indicator*: indicator to use to determine buy/sell signals when trending -- Possible values: STOCH-S --
    - *Trending threshold*: Threshold for trend determination
    - *STOCH-S Oversold*: Slow stochastics oversold threshold
    - *STOCH-S Overbought*: Slow stochastics overbought threshold
    - *MT trend TA indicator*: Technical indicator for medium term trend -- Possible values: MA5, MA20, MA50, MA200 --
	
5. Api key for quandl. See instructions below.
	api_key: the api key generated when signing up to quandl

	
# Algorithms implemented

## Algorithm 1:
This algorithm checks the general trend using the ADX (14-day) and the moving average for medium term trend (MT trend TA indicator):

	- If trending, then it uses a two-signal moving average to determine buy and sell signals. User can select these in the parameters ('Trending indicator')

	- If not trending, then it uses a non-trending indicator. Currently only slow stochastics are implemented.
	
	
# Technologies used
Python3 including the libraries:

	- quandl
	- math
	- csv
	- pickle
	- os
	- os.path
	- datetime
	- getpass
	- openpyxl
	- sys
	- bisect
	- talib
	- numpy


# Status
This work is still in development.


# Known issues
1. Backtesting option does not work properly

# Future enhancements
1. Add sql connectivity
2. Add possibility of using more than Euronext database
3. Add more try / except and assert statements to improve robustness
4. Remove hard coding of 'Euronext' database


# How to use it
1. Need to sign up to quandl to obtain a api key. Once it is done, copy file 'quandl_api_key.yaml.dist', remove the '.dist' from the name and fill in the api_key

2. Create a python 3 environment with the required libraries:
	- quandl
	- math
	- csv
	- pickle
	- os
	- os.path
	- datetime
	- getpass
	- openpyxl
	- sys
	- bisect
	- talib
	- numpy

3. To install ta-lib wrapper, go to https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib and copy the correct wheel to a directory. Navigate to the directory and execute

		`pip install TA_Lib-XXXXX.whl`

4. Run *trading_main*

