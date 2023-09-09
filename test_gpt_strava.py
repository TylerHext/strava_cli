import math
import pandas as pd
import requests
import urllib3
from requests.exceptions import RequestException
from helper_funcs import get_user_input

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

if __name__ == "__main__":
    # For testing purposes, you can call the function here
    df, at, dt = get_activities(
        client_id="77741",
        client_secret="bd69919d8215979f8fac7a0efd9edba72d49b3bf",
        refresh_token="6d566392d349bf97f936ae8990d9b02573e53141"
    )
    # and print the returned DataFrame, access_token, and dt.
    print(at)
    print(dt)
    print(df)

    pass
