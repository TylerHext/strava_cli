import argparse
import sys
from helper_funcs import config, get_user_input, quickstart, get_activities, calendar_heatmap

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quickstart", help="Setup wizard to store credentials in config.json", action='store_true')
    args = parser.parse_args()

    if args.quickstart:
        quickstart()
        sys.exit()

    try:
        config_dict = config()
        client_id = config_dict['client_id']
        client_secret = config_dict['client_secret']
        refresh_token = config_dict['refresh_token']
    except (FileNotFoundError, KeyError):
        raise Exception("Config file is not properly formatted or does not exist. Please create a config.json file using the --quickstart flag.")

    update_viz = get_user_input("\nYour last run was insertDateFromLogs\nWould you like to update visualizations by pinging Strava?")
    
    if update_viz:
        activities_df, access_token, last_activity_date = get_activities(client_id, client_secret, refresh_token)
        print(f"access token is {access_token}")
        print(f"most recent activity is {last_activity_date}")

        # create calendar heatmap visual
        calendar_heatmap(activities_df, last_activity_date)
    else:
        print("Exiting...")
        sys.exit()

if __name__ == "__main__":
    main()
