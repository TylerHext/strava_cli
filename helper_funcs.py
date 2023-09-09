import json
import os
import sys
import requests
import pandas as pd
pd.options.mode.chained_assignment = None
import urllib3
import math
from plotly_calplot import calplot

def config():
    config_file_path = 'config.json'
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as f:
            config_data = json.load(f)
        return config_data
    else:
        return False
    
def get_user_input(question):
    response = input(question + " (yes/no): ").strip().lower()
    return response == "yes"

def quickstart():
    print("welcome to quickstart wizard!")
    if os.path.exists('config.json'):
        clear_configs = get_user_input('You already have a config.json file in the proper location. Would you like to clear the file and start fresh?')
        if clear_configs:
            # remove config.json file
            print('clearing configs...')
            # create config.json file
        else:
            continue_on = get_user_input('Would you like to continue with generating visualizations?')
            if continue_on:
                pass
            else:
                print('exiting...')
                sys.exit()

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
        res_stats = requests.get(stats_url, headers=header).json()
        total_activities = res_stats["all_run_totals"]["count"] + res_stats["all_ride_totals"]["count"]

        df = pd.DataFrame()

        if many == 'all':
            # Calculate how many pages to request; 200 is max page size
            pages = math.ceil(total_activities / 200)

            # Get all activities & append to df
            for page in range(1, pages + 1):
                param = {'per_page': 200, 'page': page}
                res_activities = requests.get(activities_url, headers=header, params=param).json()
                data = pd.json_normalize(res_activities)
                df = pd.concat([df, data], axis=0)
        else:
            try:
                many = int(many)
                if many > 200:
                    raise ValueError("200 is the maximum page size from Strava API. If you want more than 200 activities please pass 'all'.")
                param = {'per_page': many}
                res_activities = requests.get(activities_url, headers=header, params=param).json()
                data = pd.json_normalize(res_activities)
                df = pd.concat([df, data], axis=0)
            except ValueError:
                raise ValueError("Invalid value for 'many'. Please provide an integer or 'all'.")

        df = df.reset_index()

        # Getting activity id and date of the most recent activity, return for GPX build
        dt = df['start_date_local'][0][0:10]

        return df, access_token, dt
    except RequestException as e:
        print(f"Error occurred while retrieving Strava activities: {e}")
        return None, None, None


def calendar_heatmap(df, today):
    # should move run filtering and measurement conversions to get_activities() ?
    # filter for runs only
    df = df[df['type'] == 'Run']
    # convert distance to miles
    df['distance'] = df['distance'].div(1609.34).round(2)

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