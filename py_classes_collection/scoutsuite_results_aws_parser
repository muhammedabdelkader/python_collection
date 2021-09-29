import json

""" Parse results json file, collect all non-warning findings under same file for each service, formate output to fit jira """

## Required input
scoutsuite_results_aws_file_path = "XXX.js"


def is_not_warning(list, item, key="max_level", risk_level="warning"):
    if list[item].get(key, 0) != risk_level:
        return item


## Dump js output in json formate
def parseme(file_path):
    with open(file_path) as f:
        json_payload = f.readlines()
        json_payload.pop(0)
        json_payload = "".join(json_payload)
        json_file = json.loads(json_payload)
        return json_file


## Services were able to access
def list_interest_services(last_run):
    summary = last_run.get("summary", 0)
    return filter(lambda item: is_not_warning(summary, item), summary.keys())


## Only accepted risk gives true in return
def risk_not_accepted(item, accepted_risks=["warning"]):
    return not (item in accepted_risks)


my_json = parseme(scoutsuite_results_aws_file_path)
last_run = my_json.get("last_run", 0)
if last_run:
    interested_list = list_interest_services(last_run)
    issues_keys = [service for service in interested_list]
    for service_issue in issues_keys:
        with open(service_issue, "w+") as service_file:
            for item in (
                my_json.get("services", None)
                .get(f"{service_issue}", None)
                .get("findings", None)
            ):
                # TODO level key value contants
                finding = (
                    my_json.get("services", None)
                    .get(f"{service_issue}", None)
                    .get("findings", None)
                    .get(item, None)
                )
                if risk_not_accepted(finding.get("level", "warning")):

                    if finding.get("references", None):
                        ref = finding.get("references")[0]
                    ref = f"[references link|{ref}]"
                    if len(finding.get("items", None)):
                        finding_record = {
                            "Title": f'\n{service_issue}:{finding.get("description",None)}',
                            "Description": finding.get("rationale", None),
                            "affected_items": finding.get("items", None),
                            "recommendation & refferences": f'{finding.get("remediation","")} \n{ref}',
                        }
                        service_file.write("\n--\n")
                        for key in finding_record.keys():

                            service_file.write("\n")
                            service_file.write(f"*_{key}_*: \n{finding_record[key]}\n")
                            service_file.write("\n")
                        service_file.write("\n--\n")
