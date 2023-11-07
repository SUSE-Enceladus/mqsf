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

    def get_amqp_host(self):
        """
        Return the amqp host url.

        :rtype: string
        """
        amqp_host = self._get_attribute(
            attribute='amqp_host'
        )

        return amqp_host or Defaults.get_amqp_host()

    def get_amqp_user(self):
        """
        Return the amqp user name.

        :rtype: string
        """
        amqp_user = self._get_attribute(
            attribute='amqp_user'
        )

        return amqp_user or Defaults.get_amqp_user()

    def get_amqp_pass(self):
        """
        Return the amqp password.

        :rtype: string
        """
        amqp_pass = self._get_attribute(
            attribute='amqp_pass'
        )

        return amqp_pass or Defaults.get_amqp_pass()
