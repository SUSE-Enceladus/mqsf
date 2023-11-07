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
        self, service_name, plugin_manager, job_type_key=None, can_skip=False
    ):
        self.service_name = service_name
        self.plugin_manager = plugin_manager
        self.job_type_key = job_type_key or 'cloud'
        self.can_skip = can_skip

    def create_job(self, job_config):
        """
        Create new instance of job based on type,
        """
        job_type = job_config.get(self.job_type_key)

        if not job_type and self.can_skip:
            job_type = 'NoOpJob'
        elif not job_type:
            raise MashJobException('No job type provided, cannot create job.')
        else:
            try:
                job_plugin = self.plugin_manager.get_plugin(name=job_type)
            except KeyError:
                raise MashJobException(
                    'Job type {0} is not supported in {1} service.'.format(
                        job_type,
                        self.service_name
                    )
                )

        return job_plugin
