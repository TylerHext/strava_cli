from helper_funcs import *
import argparse
import sys
import time
import datetime

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

# get todays date
today = datetime.datetime.today().strftime('%Y-%m-%d')

# fetch fresh activities from strava
activities_df, access_token, last_activity_date, api_limit, api_usage = get_activities(client_id, client_secret, refresh_token)

# show user last 10 activities
time.sleep(1)
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

# print api usage statistics
api_stats(api_usage, api_limit)

# offer user a list of options: refresh viz, write csv, change configs
while True:
    print("\nOptions:")
    print("1. Create viz")
    print("2. Write CSV")
    # print("3. API usage")
    # print("4. Configure")
    print("Q. Quit")

    choice = input("Please select an option: ")

    if choice == '1':
        # Implement refresh visualization functionality here
        # print('you chose create viz!')
        print("\nOptions:")
        print("1. Refresh all visualizations")
        print("B. Back")

        choice_1 = input("Please select an option: ")

        if choice_1 == '1':
            print("refreshing all visualizations...")
            print(activities_df['distance'])
            calendar_heatmap(activities_df, today)
        elif choice.lower() == 'b':
            pass
        else:
            print("Invalid choice. Please select a valid option...")
        pass
    elif choice == '2':
        # Implement write CSV functionality here
        # print('you chose write csv!')
        odir = "activities/"
        write_csv(activities_df=activities_df, today=today, output_dir=odir)
        print("csv written to activities/ directory")
        pass
    elif choice == '3':
        # Implement detailed api usage statistics here
        print('you chose api usage!')
        pass
    elif choice == '4':
        # Implement change configurations functionality here
        print('you chose update configs!')
        pass
    elif choice.lower() == 'q':
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Please select a valid option (1/2/3/...).")
