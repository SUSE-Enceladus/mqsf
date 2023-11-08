# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#

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
