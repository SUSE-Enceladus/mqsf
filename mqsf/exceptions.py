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


class MQSFException(Exception):
    """
    Base class to handle all known exceptions.

    Specific exceptions are implemented as sub classes of MQSFError

    Attributes

    * :attr:`message`
        Exception message text
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return format(self.message)


class MQSFCommandException(MQSFException):
    """
    Exception raised if an external command called via a Command
    instance has returned with an exit code != 0 or could not
    be called at all.
    """


class MQConnectionException(MQSFException):
    """
    Exception raised of connection to MQ server failed
    """


class MQSFConfigException(MQSFException):
    """
    Exception raised if config file can not be read
    """


class MQSFLogSetupException(MQSFException):
    """
    Exception raised if log file setup failed
    """


class MQSFLoggerException(MQSFException):
    """
    Base class to handle all logger service exceptions.
    """


class MQSFJobException(MQSFException):
    """
    Base class to handle all job exceptions.
    """


class MessageServiceException(MQSFException):
    """
    Exception raised if an error occurs in message service.
    """
