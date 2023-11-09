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


class JsonFormat(object):
    """
    Helper class to handle unicode characters
    in json formatted messages correctly
    """
    @staticmethod
    def json_load(file_handle):
        return json.load(file_handle)

    @staticmethod
    def json_loads(json_text):
        return json.loads(json_text)

    @staticmethod
    def json_message(data_dict):
        return json.dumps(
            data_dict, sort_keys=True, indent=4, separators=(',', ': ')
        )
