from helper_funcs import *
import argparse
import sys

## ---------------------------------
# argparse configurations
parser = argparse.ArgumentParser()
parser.add_argument("--quickstart", 
                    help="setup wizard to store credentials in config.json",
                    action='store_true'
                    )
args = parser.parse_args()
## ---------------------------------
# quickstart
if args.quickstart:
    quickstart()
    # check for config.json, handle appropriately
    # if no config.json, inform user we are creating one
    # ask user to input client_id, client_secret, refresh_token
    # future optional configs for viz choices, colors etc can go here
    # exit the program. quickstart is only used for first-time setup.
    sys.exit()
else:
    pass
## ---------------------------------
# reading configs
if config():
    try:
        #client_id, client_secret, refresh_token = config().values()
        config_dict = config()
        client_id = config_dict['client_id']
        client_secret = config_dict['client_secret']
        refresh_token = config_dict['refresh_token']
    except:
        raise Exception("Config file is not properly formatted. Refer to the documentation for proper formatting of config.json file.")
else:
    raise Exception("Config file does not exist. Please create a config.json file using the --quickstart flag.")
## ---------------------------------
# main program

# print welcome message
print('\rwelcome to...\r')
welcome_msg = '''
   _______________  ___ _    _____       ________    ____
  / ___/_  __/ __ \/   | |  / /   |     / ____/ /   /  _/
  \__ \ / / / /_/ / /| | | / / /| |    / /   / /    / /  
 ___/ // / / _, _/ ___ | |/ / ___ |   / /___/ /____/ /   
/____//_/ /_/ |_/_/  |_|___/_/  |_|   \____/_____/___/   
                                                         
'''
print(welcome_msg)

# fetch fresh activities from strava
activities_df, access_token, last_activity_date, api_limit, api_usage = get_activities(client_id, client_secret, refresh_token)

print('Last 10 activities:\r')
pretty_df(
    activities_df,
    cols=[
        'name',
        'distance',
        'moving_time',
        'start_date_local',
        'type'
    ])

# api usage statistics
usage_15, usage_daily = split_string_to_integers(api_usage)
limit_15, limit_daily = split_string_to_integers(api_limit)

usage_15 = round(usage_15/limit_15*100, 2)
usage_daily = round(usage_daily/limit_daily*100, 2)

print(f'15min usage: {usage_15}%\r')
print(f'Daily usage: {usage_daily}%\r')