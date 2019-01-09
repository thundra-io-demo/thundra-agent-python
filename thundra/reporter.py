import json
import logging

try:
    import requests
except ImportError:
    from botocore.vendored import requests

from thundra import constants
from thundra.utils import get_configuration
import thundra.utils as utils

logger = logging.getLogger(__name__)

class Reporter():

    def __init__(self, api_key, session=None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = ''
            logger.error('Please set an API key!')
        self.reports = []

        if not session:
            session = requests.Session()
        self.session = session

    def add_report(self, report):
        if get_configuration(constants.THUNDRA_LAMBDA_REPORT_CLOUDWATCH_ENABLE) == 'true':
            try:
                print(json.dumps(report))
            except TypeError:
                logger.error("Couldn't dump report with type {} to json string, \
                    probably it contains a byte array".format(report.get('type'))) 
        else:
            if isinstance(report, list):
                for data in report:
                    self.reports.append(data)
            else:
                self.reports.append(report)

    def send_report(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'ApiKey ' + self.api_key
        }
        request_url = constants.HOST + constants.PATH
        base_url = utils.get_configuration(constants.THUNDRA_LAMBDA_REPORT_REST_BASEURL)
        if base_url is not None:
            request_url = base_url + '/monitoring-data'

        response = self.session.post(request_url, headers=headers, data=self.prepare_report_json())
        self.reports.clear()
        return response

    def prepare_report_json(self):
        report_jsons = []
        for report in self.reports:
            try:
                report_jsons.append(json.dumps(report))
            except TypeError:
                logger.error("Couldn't dump report with type {} to json string, \
                            probably it contains a byte array".format(report.get('type'))) 
        json_string = "[{}]".format(','.join(report_jsons))
        return json_string
