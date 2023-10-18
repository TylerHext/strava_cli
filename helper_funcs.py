import json
import os
import sys
import requests
import pandas as pd
pd.options.mode.chained_assignment = None
import urllib3
import math
from plotly_calplot import calplot
from tabulate import tabulate
from requests.exceptions import RequestException
import time

### ---------------------------------
#               ARGPARSE
### ---------------------------------

def config():
    ''' returns configs in json format from config.json file '''
    config_file_path = 'config.json'
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            config_data = json.load(f)
        return config_data
    else:
        return False
    
def get_user_input(question):
    ''' prompts user for yes/no, only proceeds if yes '''
    response = input(question + " (yes/no): ").strip().lower()
    return response == "yes"

def quickstart():
    ''' asks some questions to populate a config.json file for new user '''
    print("welcome to quickstart wizard!")
    if os.path.exists('config.json'):
        clear_configs = get_user_input('You already have a config.json file. Would you like to overwrite it?')
        if clear_configs:
            # remove config.json file
            print('clearing configs...')
            # create config.json file
        else:
            pass
    else: # TODO
        pass
        # create a config.json file by asking questions to user

def update_status_bar(iteration, total, bar_length=50):
    progress = iteration / total
    arrow = '=' * int(round(progress * bar_length))
    spaces = ' ' * (bar_length - len(arrow))
    sys.stdout.write(f'\r[{arrow}{spaces}] {int(progress * 100)}%')
    sys.stdout.flush()


### ---------------------------------
#                 DATA
### ---------------------------------

def get_activities(client_id, client_secret, refresh_token, many='all'):
    '''Returns all Strava activities in a pandas DataFrame'''

    # Mute an API warning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    auth_url = "https://www.strava.com/oauth/token"
    id_url = 'https://www.strava.com/api/v3/athlete'
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'

    # Getting a new access token
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': "refresh_token",
        'f': "json"
    }
    try:
        res = requests.post(auth_url, data=payload, verify=False)
        res.raise_for_status()  # Check for any errors in the response
        access_token = res.json()['access_token']
        
        # Construct header using access token
        header = {'Authorization': 'Bearer ' + access_token}
        # Get athlete id, we need all these calls to calculate how many calls required for all activities
        id = requests.get(id_url, headers=header).json()["id"]

        # Get total activity count
        stats_url = f'https://www.strava.com/api/v3/athletes/{id}/stats'
        res_stats = requests.get(stats_url, headers=header)
        res_hd = res_stats.headers
        res_stats = res_stats.json()
        total_activities = res_stats["all_run_totals"]["count"] + res_stats["all_ride_totals"]["count"]

        api_limit = res_hd.get('X-RateLimit-Limit')
        api_usage = res_hd.get('X-RateLimit-Usage')

        df = pd.DataFrame()

        if many == 'all':
            # Calculate how many pages to request; 200 is max page size
            pages = math.ceil(total_activities / 200)

            print("Fetching all activities:")
            for page in range(1, pages + 1):
                param = {'per_page': 200, 'page': page}
                res_activities = requests.get(activities_url, headers=header, params=param).json()
                data = pd.json_normalize(res_activities)
                df = pd.concat([df, data], axis=0)
                # sys.stdout.write('\r')
                # sys.stdout.write(f"Progress: {page}/{pages} pages")
                # sys.stdout.flush()
                update_status_bar(page, pages)
                # time.sleep(1)  # Add a small delay to avoid API rate limits
            print("\nFetching completed.")

        else:
            try:
                many = int(many)
                if many > 200:
                    raise ValueError("200 is the maximum page size from Strava API. If you want more than 200 activities please pass 'all'.")
                param = {'per_page': many}
                res_activities = requests.get(activities_url, headers=header, params=param).json()
                data = pd.json_normalize(res_activities)
                df = pd.concat([df, data], axis=0)
                print(f"Fetching {many} activities...")
            except ValueError:
                raise ValueError("Invalid value for 'many'. Please provide an integer or 'all'.")

        df = df.reset_index()

        # Getting activity id and date of the most recent activity, return for GPX build
        dt = df['start_date_local'][0][0:10]

        return df, access_token, dt, api_limit, api_usage
    except RequestException as e:
        print(f"Error occurred while retrieving Strava activities: {e}")
        return None, None, None, None, None

def meters_to_miles(column):
    # 1 meter is approximately 0.000621371 miles
    conversion_factor = 0.000621371
    return (column * conversion_factor).round(2)

def seconds_to_hh_mm(column):
    # Convert seconds to hours and minutes
    hours = column // 3600  # 3600 seconds in an hour
    minutes = (column % 3600) // 60  # 60 seconds in a minute
    return f"{hours:02d}:{minutes:02d}"

def convert_timestamp(column):
    # convert column to datetime
    datetime_series = pd.to_datetime(column)
    # format datetime pretty
    formatted_series = datetime_series.dt.strftime('%Y-%m-%d %I:%M %p')
    return formatted_series

def pretty_df(df, length=10, cols=[]):
    # convert column units & formats
    df['distance'] = meters_to_miles(df['distance'])
    df['moving_time'] = df['moving_time'].apply(seconds_to_hh_mm)
    df['start_date_local'] = convert_timestamp(df['start_date_local'])

    if len(cols) == 0:
        print(tabulate(df.head(length), headers='keys', tablefmt='psql', showindex=False))
    else:
        df = df[cols]
        print(tabulate(df.head(length), headers='keys', tablefmt='psql', showindex=False))

def split_string_to_integers(input_string):
    try:
        # Split the input string at the comma and convert the parts to integers
        parts = input_string.split(',')
        if len(parts) == 2:
            num1 = int(parts[0].strip())
            num2 = int(parts[1].strip())
            return num1, num2
        else:
            raise ValueError("Input should contain exactly two comma-separated integers.")
    except ValueError:
        raise ValueError("Invalid input format. Please provide two comma-separated integers.")

def api_stats(api_usage, api_limit):
    # parse usage & limits
    usage_15, usage_daily = split_string_to_integers(str(api_usage))
    limit_15, limit_daily = split_string_to_integers(str(api_limit))
    # calculate usage stats
    usage_15 = round(usage_15/limit_15*100, 2)
    usage_daily = round(usage_daily/limit_daily*100, 2)
    # display usage stats
    print(f'15min usage: {usage_15}%\r')
    print(f'Daily usage: {usage_daily}%\r')

### ---------------------------------
#                 VIZ
### ---------------------------------

def calendar_heatmap(df, today):
    # filter for runs only
    df = df[df['type'] == 'Run']
    # convert distance to miles
    # df['distance'] = df['distance'].div(1609.34).round(2) # commented out because apparently i'm converting upstream; idk where

    # convert date
    # idk wtf this is but its the only way i could get it to work with calplot
    df['date'] = pd.to_datetime(df['start_date_local'])
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    df['date'] = pd.to_datetime(df['date'])

    # CALPLOT
    #========
    fig = calplot(df,
                  x="date",
                  y="distance",
                  # dark_theme=False,
                  dark_theme=True,
                  gap=0,
                  colorscale='aggrnyl',
                  # years_title=True,
                  month_lines_color="#4D4D4D",
                  month_lines_width=2,
                  space_between_plots=0.01
                  # paper_bgcolor='#00FFFD'
                  )
    fig.write_image(f"viz/calplot_{today}.png", width=1300, height=700)
    fig.write_html(f"viz/calplot_{today}.html")
    print("images written to viz/ directory")