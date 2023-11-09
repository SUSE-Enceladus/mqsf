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

from mqsf.main import main
from mqsf import hookimpl, plugin_manager


class ForecastPlugin(object):
    @hookimpl
    def run_task(self, data, log_callback):
        """Get Wx forecast for given location"""
        data['wx_data'] = {
            'Tomorrow': {
                'High Temp': '15C',
                'Low Temp': '10C',
                'Humidity': '56%'
            }
        }


class CurrentPlugin(object):
    @hookimpl
    def run_task(self, data, log_callback):
        """Get current Wx for given location"""
        data['wx_data'] = {
            'Temp': '22C',
            'Humidity': '34%'
        }


plugin_manager.register(ForecastPlugin, 'forecast')
plugin_manager.register(CurrentPlugin, 'current')
main('wx')
