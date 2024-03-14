import requests
import datetime


def get_planner_ids_for_group(access_token, group_id):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    url = f'https://graph.microsoft.com/v1.0/groups/{group_id}/planner/plans'
    response = requests.get(url, headers=headers)

    print(response.text)

    if response.status_code == 200:
        plans = response.json().get('value', [])
        return [plan['id'] for plan in plans]
    else:
        raise Exception(f"Error fetching planner IDs: {response.status_code}")
    

def create_planner_in_existing_team(access_token, group_id):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    planner_payload = {
        "owner": group_id,
        "title": 'Aufgaben'
    }
    planner_response = requests.post('https://graph.microsoft.com/v1.0/planner/plans', headers=headers, json=planner_payload)

    if planner_response.status_code != 201:
        raise Exception(f"Failed to create planner. Status Code: {planner_response.status_code}, Response: {planner_response.text}")

    return planner_response.json()['id']


def get_tasks_and_buckets_from_template_planner(access_token, source_planner_id):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    url_tasks = f'https://graph.microsoft.com/v1.0/planner/plans/{source_planner_id}/tasks'
    url_buckets = f'https://graph.microsoft.com/v1.0/planner/plans/{source_planner_id}/buckets'

    tasks_response = requests.get(url_tasks, headers=headers)
    buckets_response = requests.get(url_buckets, headers=headers)

    if tasks_response.status_code == 200 and buckets_response.status_code == 200:
        tasks = tasks_response.json().get('value', [])
        buckets = buckets_response.json().get('value', [])
        return tasks, buckets
    else:
        raise Exception("Error fetching tasks or buckets from source planner")


def create_bucket_in_planner(access_token, planner_id, bucket_name):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    bucket_payload = {
        "name": bucket_name,
        "planId": planner_id,
        "orderHint": " !"
    }
    bucket_response = requests.post('https://graph.microsoft.com/v1.0/planner/buckets', headers=headers, json=bucket_payload)

    if bucket_response.status_code != 201:
        raise Exception("Failed to create bucket")

    return bucket_response.json()['id']


def create_task_in_planner(access_token, planner_id, bucket_id, task_name):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    task_payload = {
        "planId": planner_id,
        "bucketId": bucket_id,
        "title": task_name
    }
    task_response = requests.post('https://graph.microsoft.com/v1.0/planner/tasks', headers=headers, json=task_payload)
    if task_response.status_code != 201:
        raise Exception("Failed to create task")

    return task_response.json()['id']


def is_planner_already_added_as_tab(access_token, team_id, planner_id):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    channels_response = requests.get(f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels', headers=headers)
    if channels_response.status_code != 200:
        raise Exception("Failed to get channels for the team")

    channels = channels_response.json().get('value', [])
    general_channel = next((channel for channel in channels if channel['displayName'] == 'General'), None)
    if not general_channel:
        raise Exception("General channel not found")

    channel_id = general_channel['id']

    tabs_response = requests.get(f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/tabs', headers=headers)
    if tabs_response.status_code != 200:
        raise Exception("Failed to get tabs for the General channel")

    tabs = tabs_response.json().get('value', [])

    for tab in tabs:
        if tab.get('teamsApp@odata.bind') == "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.planner":
            if tab.get('configuration', {}).get('entityId') == planner_id:
                return True
    return False


def add_planner_as_tab_in_default_channel(access_token, team_id, planner_id, user_principal_name):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    channels_response = requests.get(f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels', headers=headers)
    if channels_response.status_code != 200:
        raise Exception("Failed to get channels for the team")

    channels = channels_response.json().get('value', [])
    general_channel = next((channel for channel in channels if channel['displayName'] == 'General'), None)
    if not general_channel:
        raise Exception("General channel not found")

    channel_id = general_channel['id']

    tab_payload = {
        "displayName": 'Aufgaben',
        "teamsApp@odata.bind": "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.planner",
        "configuration": {
            "entityId": planner_id,
            "contentUrl": f"https://tasks.office.com/{team_id}/Home/PlannerFrame?page=7&planId={planner_id}&auth_pvr=Orgid&auth_upn={user_principal_name}&mkt=de-DE",
            "websiteUrl": f"https://tasks.office.com/{team_id}/Home/PlanViews/{planner_id}",
            "removeUrl": f"https://tasks.office.com/{team_id}/Home/PlannerFrame?page=13&planId={planner_id}&auth_pvr=Orgid&auth_upn={user_principal_name}&mkt=de-DE",
            "dateAdded": datetime.datetime.now().isoformat(),
            "ownerId": team_id
        }
    }
    tab_response = requests.post(f'https://graph.microsoft.com/v1.0/teams/{team_id}/channels/{channel_id}/tabs', headers=headers, json=tab_payload)

    if tab_response.status_code != 201:
        raise Exception(f"Failed to add planner as a tab in Teams channel. Status Code: {tab_response.status_code}, Response: {tab_response.text}")

    return tab_response.json()