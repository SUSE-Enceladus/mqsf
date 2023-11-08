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

from mqsf.exceptions import MQSFJobException


class BaseJobFactory(object):
    """
    Base Job Factory.
    """
    def __init__(
        self, service_name, plugin_manager, plugin_key=None, can_skip=False
    ):
        self.service_name = service_name
        self.plugin_manager = plugin_manager
        self.can_skip = can_skip
        self.plugin_key = plugin_key or 'plugin'

    def create_job(self, job_config):
        """
        Create new instance of job based on type,
        """
        plugin_name = job_config.get(self.plugin_key)

        if not plugin_name:
            raise MQSFJobException(
                'No plugin type provided, cannot create job'
            )

        job_plugin = self.plugin_manager.get_plugin(name=plugin_name)

        if not job_plugin and not self.can_skip:
            raise MQSFJobException(
                'Plugin type {0} is not supported in {1} service'.format(
                    plugin_name,
                    self.service_name
                )
            )

        if not job_plugin and self.can_skip:
            job_plugin = self.plugin_manager.get_plugin(name='NoOpJob')

        return job_plugin
