# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#

import os
import yaml

from mqsf.exceptions import MQSFConfigException
from mqsf.config.base_defaults import Defaults


class BaseConfig(object):
    """
    Implements reading of a yaml configuration file:

    The mash configuration files are yaml formatted files containing
    information to control the behavior of each service.
    """
    def __init__(self, config_file=None):
        config_file = config_file or Defaults.get_config()
        self.config_data = None
        try:
            with open(config_file, 'r') as config:
                self.config_data = yaml.safe_load(config)
        except Exception as e:
            raise MQSFConfigException(
                'Failed reading config file: {config}: {error}'.format(
                    config=config_file, error=e
                )
            )

    def _get_attribute(self, attribute, element=None):
        if self.config_data:
            if element:
                if self.config_data.get(element):
                    return self.config_data[element].get(attribute)
            else:
                return self.config_data.get(attribute)

    def get_mq_host(self):
        """
        Return the mp host url.

        :rtype: string
        """
        mq_host = self._get_attribute(
            attribute='mq_host'
        )

        return mq_host or Defaults.get_mq_host()

    def get_mq_user(self):
        """
        Return the mq user name.

        :rtype: string
        """
        mq_user = self._get_attribute(
            attribute='mq_user'
        )

        return mq_user or Defaults.get_mq_user()

    def get_mq_pass(self):
        """
        Return the mq password.

        :rtype: string
        """
        mq_pass = self._get_attribute(
            attribute='mq_pass'
        )

        return mq_pass or Defaults.get_mq_pass()

    def get_log_directory(self):
        """
        Return log directory path based on log_dir attribute.

        :rtype: string
        """
        log_dir = self._get_attribute(attribute='log_dir')
        return log_dir or Defaults.get_log_directory()

    def get_log_file(self, service):
        """
        Return log file name based on log_dir attribute.

        :rtype: string
        """
        log_dir = self.get_log_directory()
        return '{dir}{service}_service.log'.format(
            dir=log_dir, service=service
        )

    def get_job_directory(self, service_name):
        """
        Return job directory path based on service name attribute.

        :rtype: string
        """
        base_job_dir = self._get_attribute(attribute='base_job_dir')
        base_job_dir = base_job_dir or Defaults.get_base_job_directory()
        return os.path.join(
            base_job_dir,
            Defaults.get_job_directory(service_name)
        )

    def get_previous_service(self):
        """
        Return the previous service from config.
        """
        prev_service = self._get_attribute(attribute='previous_service')

        if not prev_service:
            raise MQSFConfigException(
                'previous_service is required in config file.'
            )

        return prev_service

    def get_no_op_okay(self):
        """
        Return the no op status for the service from config.
        """
        no_op_okay = self._get_attribute(attribute='no_op_okay')
        return no_op_okay or Defaults.get_no_op_okay()

    def get_base_thread_pool_count(self):
        """
        Return the thread pool count for the services background scheduler.

        :return: int
        """
        base_thread_pool_count = self._get_attribute(
            attribute='base_thread_pool_count'
        )
        return base_thread_pool_count or Defaults.get_base_thread_pool_count()
