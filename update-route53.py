#!/usr/bin/env python3

import logging
import json
import urllib
import boto3
import botocore.errorfactory
from datetime import datetime

ZONEID='<ZONEID>'
RECORDSETS = ['<LIST OF DOMAINS TO UPDATE>']

TYPE='A'
READIP='https://diagnostic.opendns.com/myip'
COMMENT="Auto updated on {:%B %d, %Y @ %H:%M}"
LOGFILE='update-route53.log'
IPFILE='update-route53.ip'

logger = logging.getLogger('update_route53')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(LOGFILE)
file_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
    
class DynDNS:

    def __init__(self):
        self.client = boto3.client('route53')
        self.dns = self.fetch_current_ip_set()
        self.ip = self.read_external_ip()

    def fetch_current_ip_set(self):
        json_record = json.dumps(self.client.list_resource_record_sets(
            HostedZoneId=ZONEID,
            StartRecordName=RECORDSETS[0],
            StartRecordType=TYPE,
            MaxItems='1'
        ), sort_keys=True, indent=4)

        json_record = json.loads(json_record)

        return json_record['ResourceRecordSets'][0]['ResourceRecords'][0]['Value']


    def read_external_ip(self):
        data = urllib.request.urlopen(READIP)
        return data.read().decode('utf-8')


    def ip_outdated(self):
        return (self.dns != self.ip)

    def generate_changes(self, i):
        return {
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'ResourceRecords': [
                    {
                        "Value": self.ip
                    }
                ],
                'Name': i,
                'Type': TYPE,
                'TTL' : 300
            }
        }


    def update_new_ip(self):
        client = self.client
        try:
            client.change_resource_record_sets(
                HostedZoneId=ZONEID,
                ChangeBatch={
                    'Comment': COMMENT.format(datetime.now()),
                    'Changes': list(map(self.generate_changes, RECORDSETS))
                }
            )
        except client.exceptions.InvalidInput as e:
            logger.error("Change batch is invalid")
        else:
            logger.info("Changed from %s to %s" % (self.dns, self.ip))


if __name__ == '__main__':
    logger.info("Checking for IP address change...")
    try:
        dyndns = DynDNS()
        if dyndns.ip_outdated():
            dyndns.update_new_ip()
        else:
            logger.info("IP address has not changed")
    except botocore.exceptions.NoCredentialsError:
        logger.error("Unable to locate credentials")
    except:
        logger.error("An unknown error occurred")
