import cgi
import csv
import json
import logging
from io import StringIO

import requests
from joblib import Parallel, delayed
from requests.auth import HTTPBasicAuth
from utils.processors.details import details_processor
from utils.processors.overview import overview_processor

__version__ = "0.1"


class NexposeConnection(object):
    def __init__(self, nxserver, user, password, config):
        logging.info("Nexpose: Parameter Initializing ")
        self.config = config
        self.nxserver = nxserver
        self.nxapiroot = 'https://%s/api/3' % nxserver
        self.api_session = requests.Session()
        if 'certificate' in self.config['nexpose']:
            self.api_session.verify = self.config['nexpose']['certificate']
        self.api_session.auth = HTTPBasicAuth(user, password)

        self.web_session = self.perform_web_login(nxserver, user, password)

    def perform_web_login(self, nxserver, user, password):
        web_session = requests.Session()
        if 'certificate' in self.config['nexpose']:
            web_session.verify = self.config['nexpose']['certificate']

        url = 'https://%s/data/user/login' % nxserver
        payload = {"nexposeccusername": user, "nexposeccpassword": password}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = web_session.post(url, headers=headers, data=payload)
        assert response.status_code == 200

        return web_session

    def perform_post_method(self, url, payload=''):
        response = self.web_session.post(
            url=url,
            headers={
                "nexposeCCSessionID": self.web_session.cookies['nexposeCCSessionID']},
            data=payload
        )
        assert response.status_code == 200
        return response

    def _get_vulndata(self, report_id, headermap=None):
        r = self.api_session.get(
            f'{self.nxapiroot}/reports/{report_id}/history/latest'
        )

        if r and 'status' in r.json() and r.json()['status'] == 'complete':
            url = f'{self.nxapiroot}/reports/{report_id}/history/latest/output'
            if report_id == self.config['nexpose']['reports']['vulndetails']:
                details_processor(session=self.api_session, url=url)
            elif report_id == self.config['nexpose']['reports']['vulnoverview']:
                overview_processor(session=self.api_session, url=url)
            else:
                # TODO: refactor it
                r = self.api_session.get(url)
                header = r.text.splitlines()[0]

                if headermap is not None:
                    for col, new_col in list(headermap.items()):
                        header = header.replace(col, new_col)

                newcsv = StringIO()
                newcsv.write("%s\n" % header)
                newcsv.write(cgi.escape('\n'.join(r.text.splitlines()[1:])))
                newcsv.seek(0)

                res = csv.DictReader(newcsv)

                return list(res)
        else:
            raise Exception(f'Report is not complete report_id: {report_id}')

    def get_overview_report(self):
        self._get_vulndata(
            report_id=self.config['nexpose']['reports']['vulnoverview'],
        )

    def get_details_report(self):
        self._get_vulndata(
            report_id=self.config['nexpose']['reports']['vulndetails'],
        )

    def qlik_sense_report(self, args_local=False):
        coverage_by_site = {}
        status_list = [
            'Successful', 'Aborted', 'Unknown', 'Running', 'Finished',
            'Stopped', 'Error', 'Paused', 'Dispatched', 'Integrating'
        ]

        if args_local:
            with open('scans_coverage_overview.json') as f:
                overview_results = json.load(f)
        else:
            scancoverage = self._get_vulndata(
                report_id=self.config['nexpose']['reports']['scanCoverageITGov_overview'])
            overview_results = [dict(item) for item in scancoverage]
            with open("scans_coverage_overview.json", "w") as f:
                f.write(json.dumps(overview_results))
            scancoverage = self._get_vulndata(
                report_id=self.config['nexpose']['reports']['scanCoverageITGov_detailed'])

            details_results = [dict(item) for item in scancoverage]
            for item in details_results:
                if not item['name'] in coverage_by_site:
                    coverage_by_site[item['name']] = {}
                    for state in status_list:
                        coverage_by_site[item['name']][state] = set()

                coverage_by_site[item['name']][item['scan_status']].add(item['ip_address'])

            for item in overview_results:
                name = item['name']
                for state in status_list:
                    if name in coverage_by_site:
                        item[state] = len(coverage_by_site[name][state])
                    else:
                        item[state] = 0

            with open("scans_coverage_details.json", "w") as f:
                f.write(json.dumps(overview_results))

        return overview_results

    def get_assets(self, args_local=False):
        def add_asset(asset):
            if asset['assessedForVulnerabilities']:
                try:
                    if 'history' in asset:
                        last_seen = asset['history'][-1]['date'][:10]
                    else:
                        last_seen = ''

                    a = {
                        'ip': asset['ip'],
                        'hostname': asset.get('hostName', ''),
                        'lastseen': last_seen,
                        'ports': ','.join(
                            map(str, [s['port'] for s in asset['services']])
                        ) if 'services' in asset else ''
                    }

                    return a
                except Exception as e:
                    logging.warning("Error adding asset: %s" % e)

        if args_local:
            with open('assets.json') as f:
                assets = json.load(f)
        else:
            r = self.api_session.post('%s/assets/search?size=500' % self.nxapiroot, json={"filters": [
                {"field": "last-scan-date", "operator": "is-within-the-last", "value": 10}], "match": "all"})
            res = r.json()

            assets = []
            for i in range(0, res['page']['totalPages']):
                logging.info("\rPage %s/%s" % (i + 1, res['page']['totalPages']))
                r = self.api_session.post('%s/assets/search?size=500&page=%s' % (self.nxapiroot, i), json={"filters": [
                    {"field": "last-scan-date", "operator": "is-within-the-last", "value": 10}], "match": "all"})
                nxres = r.json()
                assets.extend(Parallel(n_jobs=10)(delayed(add_asset)(asset)
                                                  for asset in nxres['resources']))
                assets = list([_f for _f in assets if _f])

            with open('assets.json', 'w') as f:
                f.write(json.dumps(assets))

        return assets

    def get_asset_arns(self):
        assets = dict()
        asset_report = self._get_vulndata(
            report_id=self.config['nexpose']['reports']['asset_csv'])
        for item in asset_report:
            asset = dict(item)
            ip = asset['ip_address']
            uid = asset['unique_id']
            site = asset['site_name']
            if uid.startswith('i-') and ' - ' in site:
                account, region = site.split(' - ')
                assets[ip] = f'arn:aws:ec2:{region}:{account}:instance/{uid}'
        return assets

    def get_container_details(self, asset):
        response = self.perform_post_method(
            "https://%s/data/assets/%s/containers" % (self.nxserver, asset['id']))

        containers = []
        if response.status_code == 200:
            # print(response.text)
            print(response.text)
            for container in response.json()['records']:
                containers.append({'ip': asset['ip'],
                                   'id': container['id'],
                                   'name': container['name'],
                                   'digest': container['imageDigest'],
                                   'image_id': container['imageID'],
                                   'repository': container['imageRepository'],
                                   'creation_time': container['creationTime'],
                                   'start_time': container['startTime'],
                                   'status': container['status']})

            return containers

    def get_containers(self, args_local=False):
        if args_local:
            with open('containers.json') as f:
                containers = json.load(f)
        else:
            assets_with_containers = self.get_assets_with_containers()
            ctmp = Parallel(n_jobs=10)(delayed(self.get_container_details)(
                asset) for asset in assets_with_containers)
            containers = [container for c in ctmp for container in c]

            with open('containers.json', 'w') as f:
                f.write(json.dumps(containers))

        return containers

    def get_assets_with_containers(self):
        logging.info('List asset IDs...')
        assetfilter = {"filters": [
            {"field": "containers", "operator": "are", "value": "0"}], "match": "all"}
        r = self.api_session.post(
            '%s/assets/search?size=500' % self.nxapiroot, json=assetfilter)

        res = r.json()

        assets = []
        pages = res['page']['totalPages']
        for page in range(0, pages):
            assets.extend(res['resources'])

            if page != res['page']['totalPages']:
                res = self.api_session.post(
                    '%s/assets/search?size=500&page=%s' % (self.nxapiroot, page), json=assetfilter).json()

        return assets
