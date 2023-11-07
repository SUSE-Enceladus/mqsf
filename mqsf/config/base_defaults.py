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
    def get_amqp_host():
        return 'localhost'

    @staticmethod
    def get_amqp_user():
        return 'guest'

    @staticmethod
    def get_amqp_pass():
        return 'guest'
