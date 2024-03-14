from msal import ConfidentialClientApplication
import requests 
import json


def get_access_token(client_id, client_secret, tenant_id):
    app = ConfidentialClientApplication(client_id, authority=f'https://login.microsoftonline.com/{tenant_id}', client_credential=client_secret)

    result = app.acquire_token_silent(['https://graph.microsoft.com/.default'], account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])

    if 'access_token' in result:
        return result['access_token']
    else:
        return "Could not acquire token", result.get('error')


def get_user_id_from_email(email, access_token):
    url = f'https://graph.microsoft.com/v1.0/users/{email}'

    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('id')
    else:
        return None
    

def get_username_from_email(email, access_token):
    url = f'https://graph.microsoft.com/v1.0/users/{email}'

    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('displayName')
    else:
        return None
    

def get_user_email_from_id(access_token, user_id):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}'

    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('mail')
    else:
        return None
    

def find_group_id_by_name(access_token, team_name):
    url = 'https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/Any(x:x eq \'Team\')'

    headers = {'Authorization': 'Bearer ' + access_token}

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            groups = data.get('value', [])
            for group in groups:
                if group.get('displayName', '').lower() == team_name.lower():
                    return group.get('id')
            
            url = data.get('@odata.nextLink')
        else:
            return None
    return None


def get_channel_id_by_name(access_token, group_id, channel_name):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    channels_response = requests.get(f'https://graph.microsoft.com/v1.0/teams/{group_id}/channels', headers=headers)
    if channels_response.status_code != 200:
        raise Exception("Failed to get channels for the team")

    channels = channels_response.json().get('value', [])
    general_channel = next((channel for channel in channels if channel['displayName'] == channel_name), None)
    if not general_channel:
        return None
    return general_channel['id']


def get_sharepoint_site_id(access_token, group_id):
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/sites/root"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('id')
    else:
        return None