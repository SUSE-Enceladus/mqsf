# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#

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
