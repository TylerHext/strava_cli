# from helper_funcs import config, get_user_input, quickstart, get_activities, calendar_heatmap, pretty_df
from helper_funcs import *
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--quickstart", 
                    help="setup wizard to store credentials in config.json",
                    action='store_true'
                    )
args = parser.parse_args()

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

activities_df, access_token, last_activity_date = get_activities(client_id, client_secret, refresh_token)

# pretty_df(
#     activities_df,
#     cols=[
#         'name',
#         'distance',
#         'moving_time',
#         'start_date_local',
#         'type'
#     ])

pretty_df(
    activities_df,
    cols=[
        'name',
        'distance',
        'moving_time',
        'start_date_local',
        'type'
    ])

# update_viz = get_user_input("\nYour last run was insertDateFromLogs\nWould you like to update visualizations by pinging strava?")

# if update_viz:
#     activities_df, access_token, last_activity_date = get_activities(client_id, client_secret, refresh_token)
#     print(f"access token is {access_token}")
#     print(f"most recent activity is {last_activity_date}")

#     # create calendar heatmap visual
#     calendar_heatmap(activities_df, last_activity_date)
# else:
#     print("exiting...")
#     sys.exit()