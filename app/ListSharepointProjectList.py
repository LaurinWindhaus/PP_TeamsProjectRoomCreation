import requests

def get_projects_from_sharepoint_list(access_token, site_id, list_id):
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items?expand=fields'

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    result = []
    
    while url: 
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            projects = data.get('value', [])
            for project in projects:
                raum_erforderlich = project.get('fields', {}).get('Raum_x0020_erforderlich', '')
                status_projekt = project.get('fields', {}).get('StatusProjekt', '')
                team_id = project.get('fields', {}).get('TeamID', '')
                if raum_erforderlich and (status_projekt == 'Aktiv' or status_projekt == 'Backlog') and team_id == '':
                    # print(f'Raum erforderlich: {raum_erforderlich} - Status Projekt: {status_projekt} - Team ID: {team_id}')
                    result.append(project)
            url = data.get('@odata.nextLink')
        else:
            raise Exception(f'Error retrieving list entries: {response.status_code} - {response.text}')
    return result
    

def update_sharepoint_list_entry(access_token, site_id, list_id, item_id, update_fields):
    url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items/{item_id}'

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    data = {
        "fields": update_fields
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code in [200, 204]:
        return {"message": "Item updated successfully."}
    else:
        raise Exception(f'Error updating list entry: {response.status_code} - {response.text}')