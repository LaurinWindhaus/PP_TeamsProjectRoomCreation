import requests
import json

def check_if_team_exist(access_token, team_name):
    url = 'https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/Any(x:x eq \'Team\')'

    headers = {'Authorization': 'Bearer ' + access_token}
    team_names = []

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            teams = data.get('value', [])
            for team in teams:
                team_display_name = team.get('displayName', '').lower()
                team_names.append(team_display_name)

                if team_display_name == team_name.lower():
                    return True
            url = data.get('@odata.nextLink')
        else:
            return None
    return team_name.lower() in team_names


def create_teams_room(access_token, team_name, team_description, owner_user_id):
    url = 'https://graph.microsoft.com/v1.0/teams'

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    body = {
        "template@odata.bind":"https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
        "displayName": team_name,
        "description": team_description,
        "members":[
            {
                "@odata.type":"#microsoft.graph.aadUserConversationMember",
                "roles":[
                    "owner"
                ],
                "user@odata.bind":"https://graph.microsoft.com/v1.0/users('{0}')".format(owner_user_id)
            }
        ]
    }
    response = requests.post(url, headers=headers, json=body)

    return response



def rename_notes_tab_to_notizbuch(access_token, group_id, channel_id):
    headers = {'Authorization': 'Bearer ' + access_token}
    tabs_url = f'https://graph.microsoft.com/v1.0/teams/{group_id}/channels/{channel_id}/tabs'
    tabs_response = requests.get(tabs_url, headers=headers)
    if tabs_response.status_code != 200:
        return "Fehler beim Abrufen der Tabs."
    
    tabs_data = tabs_response.json().get('value', [])
    notes_tab_id = None
    for tab in tabs_data:
        if tab.get('displayName', '').lower() == 'notes':
            notes_tab_id = tab.get('id')
            break

    if not notes_tab_id:
        return "Notes-Tab nicht gefunden."

    # Schritt 3: Benenne den "Notes" Tab um zu "Notizbuch"
    update_url = f'https://graph.microsoft.com/v1.0/teams/{group_id}/channels/{channel_id}/tabs/{notes_tab_id}'
    update_body = {"displayName": "Notizbuch"}
    update_response = requests.patch(update_url, headers=headers, json=update_body)
    if update_response.status_code == 204:
        return "Der 'Notes' Tab wurde erfolgreich zu 'Notizbuch' umbenannt."
    else:
        return f"Fehler beim Umbenennen des Tabs: {update_response.status_code}"
    

def get_team_room_info(access_token, group_id):
    url = f"https://graph.microsoft.com/v1.0/teams/{group_id}"

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    return response.json()


def post_message_in_channel(access_token, group_id, channel_id, owner_name):
    url = f'https://graph.microsoft.com/v1.0/teams/{group_id}/channels/{channel_id}/messages'

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    adaptive_card_content = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": f"Moin {owner_name} und herzlich willkommen in deinem Teams-Projektraum.",
                "wrap": "true",
                "size": "Medium",
                "weight": "Bolder",
                "horizontalAlignment": "Center"
            },
            {
                "type": "TextBlock",
                "text": "Dieser vorbereitete Projektraum dient mit seinen verschiedenen Registerkarten als **Empfehlung** für die operative Projektarbeit.",
                "wrap": "true"
            },
            {
                "type": "TextBlock",
                "text": "Folgende Registerkarten können euch bei der Projektarbeit gut unterstützen. Wie ihr die einzelnen Registerkarten bedient, findet ihr hier in den kurzen Schulungsvideos für euch: [LINK](https://web.microsoftstream.com/channel/194789a1-0611-4157-8419-ce048d79e4fe)\n",
                "spacing": "Small",
                "wrap": "true"
            },
            {
                "type": "TextBlock",
                "text": "**1.\tBeiträge** zum Informieren und Kommunizieren",
                "wrap": "true",
                "spacing": "Small"
            },
            {
                "type": "TextBlock",
                "text": "**2.\tDateien** für die gesamte Projektdokumentation und Dateiablage",
                "wrap": "true",
                "spacing": "None"
            },
            {
                "type": "TextBlock",
                "text": "**3.\tNotizen** in OneNote zum Festhalten von Projektteammeetings & weiteren Besprechungen und der regelm. Abfrage unserer Stimmung im Team",
                "wrap": "true",
                "spacing": "None"
            },
            {
                "type": "TextBlock",
                "text": "**4.\tAufgaben** in Planner zum Erstellen und Verwalten von Aufgaben",
                "wrap": "true",
                "spacing": "None"
            },
            {
                "type": "TextBlock",
                "text": "**5.\tProjektterminplan** (Gantt Diagramm) in Excel für die Terminplanung und -verfolgung",
                "wrap": "true",
                "spacing": "None"
            },
            {
                "type": "TextBlock",
                "text": "**6.\tEntscheidungen** für das Vorbereiten, Durchführen und Festhalten von Entscheidungen",
                "wrap": "true",
                "spacing": "None"
            },
            {
                "type": "TextBlock",
                "text": "**7.\tProjektstatus** als Übersicht über die regelmäßigen Updates\n\n",
                "wrap": "true",
                "spacing": "None"
            },
            {
                "type": "TextBlock",
                "text": "Auf geht´s: Lade deine Projektteammitglieder in den Teamsraum und heiße sie willkommen.",
                "wrap": "true",
                "spacing": "Small"
            },
            {
                "type": "TextBlock",
                "text": "Unter folgendem Link findest du nützliche Projektmanagement-Vorlagen: [LINK](https://poeppelmanngmbh.sharepoint.com/sites/PPProjekt/SitePages/Vorlagen.aspx?web=1)",
                "wrap": "true"
            },
            {
                "type": "TextBlock",
                "text": "Wenn du Unterstützung brauchst, dann melde dich gerne bei Elena Sieverding ([Chat](https://teams.microsoft.com/l/chat/0/0?users=ElenaSieverding@poeppelmann.com) in Teams).",
                "wrap": "true",
                "spacing": "ExtraLarge"
            }
        ]
    }

    serialized_adaptive_card_content = json.dumps(adaptive_card_content)

    message = {
        "body": {
            "contentType": "html",
            "content": "Here is a custom Adaptive Card"
        },
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": serialized_adaptive_card_content  # Use the serialized string here
            }
        ]
    }

    response = requests.post(url, headers=headers, json=message)

    if response.status_code == 201:
        return "Adaptive Card wurde erfolgreich gesendet."
    else:
        return f"Fehler beim Senden der Adaptive Card: {response.status_code}, {response.text}"
    
# import os
# from services import get_access_token

# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# tenant_id = os.getenv("TENANT_ID")
# access_token = get_access_token(client_id, client_secret, tenant_id)
# print(post_message_in_channel(access_token, '57e85ef2-f76c-42a5-8c6f-00596d51b2b0', '19:xjskC6ugA_Q4owJkZSFHNs1Up6ngkgyeNmhL3p0R6es1@thread.tacv2', 'Laurin windhaus'))