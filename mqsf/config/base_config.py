# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#

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
