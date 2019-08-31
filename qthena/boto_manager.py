#!python
# ==========================================================#
# project        :sjd Automation
# title          :boto_manager.py
# description    :abstracts and centralizes boto client and sessions used in this framework
# author         :sjdillon
# date           :06/18/2018
# python_version :2.7.8
# notes          :
# ==========================================================#
import logging
import boto3

logging.basicConfig(format="%(asctime)s - %(thread)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BotoClientManager:
    """ Handles keeping state boto client sessions """

    def __init__(self, params):
        logger.debug('BotoClientManager init params:{}:'.format(params))
        self.service = params['service']
        self.region = params['region']
        if 'profile' in params:
            self.profile = params['profile']
        if 'mock_mode' in params:
            self.mock_mode = params['mock_mode']
        if 'mock_data_path' in params:
            self.mock_data_path = params['mock_data_path']

    def get_client(self):
        if hasattr(self, 'profile'):
            session = boto3.Session(profile_name=self.profile)
        else:
            session = boto3.Session()
        if hasattr(self, 'mock_mode'):
            import placebo
            pill = placebo.attach(session, data_path=self.mock_data_path)
            if self.mock_mode == 'playback':
                pill.playback()
                logger.info('playing back mock boto calls from {}'.format(self.mock_data_path))
            if self.mock_mode == 'record':
                pill.record()
                logger.info('recording boto to {}'.format(self.mock_data_path))
        client = session.client(self.service, region_name=self.region)
        return client
