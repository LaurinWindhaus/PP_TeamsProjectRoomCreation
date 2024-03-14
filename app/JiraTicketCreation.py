import requests
import json
import json 

def create_jira_ticket(username, password, summary, description):
    url = "https://poeppelmann.atlassian.net/rest/api/3/issue"
    auth = (username, password)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    description_adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "text": description,
                        "type": "text"
                    }
                ]
            }
        ]
    }
    
    payload = json.dumps({
        "fields": {
            "project": { "id": 10003 }, # project_key IT-Helpdesk
            "summary": summary,
            "description": description_adf,
            "issuetype": {
                "name": "Task"
            },
            "customfield_10140": {
                "value": "APM_Office365"
            }
        }
    })

    response = requests.post(url, data=payload, headers=headers, auth=auth)

    if response.status_code == 201:
        return response.json()
    else:
        return response.text


# def list_projects(username, password, jira_url, auth_token):
#     """
#     List all projects in JIRA.

#     :param jira_url: JIRA Base URL
#     :param auth_token: Authentication token for API access
#     :return: None, prints the list of projects
#     """
#     url = f"{jira_url}/rest/api/3/project"
#     headers = {
#         "Accept": "application/json",
#         "Authorization": f"Bearer {auth_token}"
#     }
    
#     response = requests.get(url, headers=headers, auth=(username, password))
    
#     if response.status_code == 200:
#         projects = response.json()
#         for project in projects:
#             print(f"Project Name: {project['name']}, Project Key: {project['key']}, {project['id']}")
#     else:
#         print(f"Failed to list projects, status code: {response.status_code}")


# jira_url = "https://poeppelmann.atlassian.net"
# list_projects(jira_url, token)