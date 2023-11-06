# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#

import logging
import os


class SchedulerLoggingFilter(logging.Filter):
    def filter(self, record):
        ignore = 'maximum number of running instances reached'
        return ignore not in record.msg


class BaseServiceFilter(logging.Filter):
    """
    Filter rule for BaseService logger

    The message format this filter applies to contains
    two custom fields not part of the standard logging

    * %newline
      will be set to whatever os.linesep is

    * %job
      will be set to job_id or empty if not present
    """
    def filter(self, record):
        record.newline = os.linesep
        if hasattr(record, 'job_id'):
            record.job = 'Job[{0}]: '.format(record.job_id)
        else:
            record.job = ''
        return True
