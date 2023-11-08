# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#


class Defaults(object):
    """
    Default values
    """
    @classmethod
    def get_config(self):
        return '/etc/mqsf/mqsf_config.yaml'

    @staticmethod
    def get_mq_host():
        return 'localhost'

    @staticmethod
    def get_mq_user():
        return 'guest'

    @staticmethod
    def get_mq_pass():
        return 'guest'

    @classmethod
    def get_base_job_directory(self):
        return '/var/lib/mqsf/'

    @classmethod
    def get_job_directory(self, service_name):
        return '{0}_jobs/'.format(service_name)

    @classmethod
    def get_log_directory(self):
        return '/var/log/msqf/'

    @classmethod
    def get_no_op_okay(self):
        return True

    @staticmethod
    def get_base_thread_pool_count():
        return 10
