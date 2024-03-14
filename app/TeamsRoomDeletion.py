import requests


def soft_delete_group(access_token, group_id):
    url = f'https://graph.microsoft.com/v1.0/groups/{group_id}'

    headers = {'Authorization': 'Bearer ' + access_token}

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        return True
    else:
        return False
    

def check_if_group_is_soft_deleted(access_token, group_id):
    url = f'https://graph.microsoft.com/v1.0/directory/deleteditems/microsoft.graph.group/{group_id}'

    headers = {'Authorization': 'Bearer ' + access_token}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        return None