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

import json

from mqsf.main import main
from mqsf import hookimpl, plugin_manager


class EmailPlugin(object):
    @hookimpl
    def run_task(self, data, log_callback):
        """Send email notification with Wx data"""
        wx_info = data['wx_data']
        print(json.dumps(wx_info))


def run():
    plugin_manager.register(EmailPlugin, 'email')
    main('notif')


run()
