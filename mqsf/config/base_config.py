# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-

import os
import yaml

from mqsf.exceptions import MQSFConfigException


# Default config values
DEFAULT_CONFIG_FILE = '/etc/mqsf/mqsf_config.yaml'
DEFAULT_MQ_HOST = 'localhost'
DEFAULT_MQ_USER = 'guest'
DEFAULT_MQ_PASS = 'guest'
DEFAULT_LOG_DIRECTORY = '/var/log/mqsf/'
DEFAULT_JOB_DIRECTORY_TEMPLATE = '{0}_jobs/'
DEFAULT_BASE_JOB_DIRECTORY = '/var/lib/mqsf/'
DEFAULT_NO_OP_OKAY = True
DEFAULT_BASE_THREAD_POOL_COUNT = 10
DEFAULT_PLUGIN_KEY = 'plugin'


class BaseConfig(object):
    """
    Implements reading of a yaml configuration file:

    The mash configuration files are yaml formatted files containing
    information to control the behavior of each service.
    """
    def __init__(self, config_file=None):
        config_file = config_file or DEFAULT_CONFIG_FILE
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
                    return self.config_data[element].get(attribute, None)
            else:
                return self.config_data.get(attribute, None)

    def get_mq_host(self):
        """
        Return the mp host url.

        :rtype: string
        """
        mq_host = self._get_attribute(
            attribute='mq_host'
        )

        return mq_host or DEFAULT_MQ_HOST

    def get_mq_user(self):
        """
        Return the mq user name.

        :rtype: string
        """
        mq_user = self._get_attribute(
            attribute='mq_user'
        )

        return mq_user or DEFAULT_MQ_USER

    def get_mq_pass(self):
        """
        Return the mq password.

        :rtype: string
        """
        mq_pass = self._get_attribute(
            attribute='mq_pass'
        )

        return mq_pass or DEFAULT_MQ_PASS

    def get_log_directory(self):
        """
        Return log directory path based on log_dir attribute.

        :rtype: string
        """
        log_dir = self._get_attribute(attribute='log_dir')
        return log_dir or DEFAULT_LOG_DIRECTORY

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
        base_job_dir = base_job_dir or DEFAULT_BASE_JOB_DIRECTORY
        return os.path.join(
            base_job_dir,
            DEFAULT_JOB_DIRECTORY_TEMPLATE.format(service_name)
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
        if no_op_okay is None:
            return DEFAULT_NO_OP_OKAY
        return no_op_okay

    def get_base_thread_pool_count(self):
        """
        Return the thread pool count for the services background scheduler.

        :return: int
        """
        base_thread_pool_count = self._get_attribute(
            attribute='base_thread_pool_count'
        )
        return base_thread_pool_count or DEFAULT_BASE_THREAD_POOL_COUNT

    def get_plugin_key(self):
        """
        Return the plugin key name to use for determining what plugin to run.
        """
        plugin_key = self._get_attribute(attribute='plugin_key')
        return plugin_key or DEFAULT_PLUGIN_KEY
