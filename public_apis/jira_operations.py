​from argparse import ArgumentParser
from datetime import datetime

import boto3
import requests
from jira import JIRA
from requests.auth import HTTPBasicAuth

__version__ = "0.1"


class jira_operations(object):
    """ Jira operations class """

    def __init__(self, username, password, baseUrl):
        self.username = username
        self.password = password
        self.jira_auth = HTTPBasicAuth(self.username, self.password)
        self.baseUrl = baseUrl
        self.client = self.create_jira_client(self.username, self.password, self.baseUrl)

​

def create_jira_client(self, username, password, jira_url):
    try:
        jira_client = JIRA(
            options={
                "server": jira_url,
                "rest_path": "api",
                "rest_api_version": 2,
            },
            basic_auth=(username, password),
            get_server_info=False,
        )
    except Exception as e:
        print(e)
    return jira_client

​

def searchJiraProjectDueDate(self, project="project_name", myDate="2019-12-31", maxResults=5000):
    print("[-] Lisiting items {}".format(" ... "))
    issues = self.client.search_issues('project=' + project + ' and createdDate >=' + myDate, maxResults=maxResults)
    tickets = []
    for issue in issues:
        tickets.append(issue.key)
    return tickets

​
​
​

def findBBTickets(self, project='project_name', condition='and field_X = "Value_X"', maxResults=5000):
    issues = self.client.search_issues('project=' + project + ' ' + condition, maxResults=maxResults)
    teamSummary = {}
    now = datetime.now()
    print('[+] {}'.format(str(now).replace(" ", "")))
    with open(str(now) + "_records_sheets", "w+") as write2File:
        write2File.write("table_row_header_1,table_row_header_2,table_row_header_3,table_row_header_4\n ")
        for issue in issues:
            bountyValue = issue.fields.customfield_XXXX
            tiketId = issue.key
            h1Id = issue.fields.customfield_XXXXY
            teamName = issue.fields.customfield_YYXXC[0]
            aCode = self.getAccountCode(teamName.split("(")[1][:-1])

​
if bountyValue is None:
    bountyValue = 0
else:
    bountyValue = bountyValue.replace(",", "")
​
write2File.write('{} , {} , {} , {} , {} \n '.format(tiketId, h1Id, bountyValue, teamName, aCode))
if aCode in teamSummary:
    teamSummary[aCode] += float(bountyValue)
else:
    teamSummary[aCode] = float(bountyValue)
​
with open(str(now) + "_summarySheet", "w+") as write2File:
    write2File.write("Accountability Code,Bounty Sum \n ")
    for item in teamSummary:
        write2File.write('{},{} \n '.format(item, teamSummary[item]))
print("********************************************************")
​

def getAccountCode(self, objectID):
    url = self.baseUrl + "/rest/insight/1.0/object/" + objectID
    response = requests.get(url, auth=self.jira_auth)
    for attr in response.json()['attributes']:
        if 'Accountability Code' in attr['objectTypeAttribute']['name']:
            return (attr['objectAttributeValues'][0]['value'])

​
​

def main():
    parser = ArgumentParser()
    parser.add_argument('-boy', '--allmybounty', action='store_true',
                        help="Build bugbounty sheets", default=False)
    parser.add_argument('-vms', action='store_true', help="Return Only VM's Ids ", default=True)
    args = parser.parse_args()

​    domain = "XYZ.com"
jira_host = f"https://jira.{domain}/jira"
jira_username = "jira_ro"
ssm = boto3.client('ssm', 'eu-west-1')
jira_password = ssm.get_parameter(Name='SSM_SECRET_PATH', WithDecryption=True)['Parameter']['Value']
jiraObject = jira_operations(jira_username, jira_password, jira_host)
​
​
print("Syncing data from Jira...")
if args.allmybounty:
    jiraObject.findBBTickets()
else:
    print(jiraObject.searchJiraProjectDueDate())
​
print("### Finished ###")
​
​
if __name__ == "__main__":
    main()
