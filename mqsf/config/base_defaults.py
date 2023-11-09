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
        return '/var/log/mqsf/'

    @classmethod
    def get_no_op_okay(self):
        return True

    @staticmethod
    def get_base_thread_pool_count():
        return 10
