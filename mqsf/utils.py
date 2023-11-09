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

import datetime
import json
import logging
import os
import random
import requests

from contextlib import contextmanager, suppress
from string import ascii_lowercase
from tempfile import NamedTemporaryFile

from mqsf.log.handler import MQHandler
from mqsf.exceptions import MQSFException, MQSFLogSetupException
from mqsf.json_format import JsonFormat


@contextmanager
def create_json_file(data):
    try:
        temp_file = NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'w') as json_file:
            json_file.write(JsonFormat.json_message(data))
        yield temp_file.name
    finally:
        with suppress(OSError):
            os.remove(temp_file.name)


@contextmanager
def create_key_file(data):
    try:
        temp_file = NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'w') as key_file:
            key_file.write(data)
        yield temp_file.name
    finally:
        with suppress(OSError):
            os.remove(temp_file.name)


def generate_name(length=8):
    """
    Generate a random lowercase string of the given length: Default of 8.
    """
    return ''.join([random.choice(ascii_lowercase) for i in range(length)])


def get_key_from_file(key_file_path):
    """
    Return a key as string from the given file.
    """
    with open(key_file_path, 'r') as key_file:
        key = key_file.read().strip()

    return key


def format_string_with_date(value, timestamp=None, date_format='%Y%m%d'):
    if not timestamp:
        timestamp = datetime.date.today().strftime(date_format)

    try:
        value = value.format(date=timestamp)
    except KeyError:
        # Ignore unknown format strings.
        pass

    return value


def timestamp_from_epoch(epoch, date_format='%Y%m%d'):
    timestamp = datetime.datetime.fromtimestamp(
        int(epoch),
        datetime.timezone.utc
    )
    return timestamp.strftime(date_format)


def remove_file(file_path):
    """
    Remove file from disk if it exists.
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


def persist_json(file_path, data):
    """
    Persist the json data to a file on disk.
    """
    with open(file_path, 'w') as json_file:
        json_file.write(JsonFormat.json_message(data))


def load_json(file_path):
    """
    Load json from file and return dictionary.
    """
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    return data


def restart_job(job_file, callback):
    """
    Restart job from config file using callback.
    """
    job_config = load_json(job_file)
    callback(job_config)


def restart_jobs(job_dir, callback):
    """
    Restart all jobs in job_dir using callback.
    """
    for job_file in os.listdir(job_dir):
        restart_job(os.path.join(job_dir, job_file), callback)


def handle_request(url, endpoint, method, job_data=None):
    """
    Post request based on endpoint and data.

    If response is unsuccessful raise exception.
    """
    request_method = getattr(requests, method)
    data = None if not job_data else JsonFormat.json_message(job_data)
    uri = ''.join([url, endpoint])

    response = request_method(uri, data=data)

    if response.status_code not in (200, 201):
        try:
            msg = response.json()['msg']
        except Exception:
            msg = 'Request to {uri} failed: {reason}'.format(
                uri=uri,
                reason=response.reason
            )

        raise MQSFException(msg)

    return response


def setup_logfile(logfile):
    """
    Create log dir and log file if either does not already exist.
    """
    try:
        log_dir = os.path.dirname(logfile)
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
    except Exception as e:
        raise MQSFLogSetupException(
            'Log setup failed: {0}'.format(e)
        )

    logfile_handler = logging.FileHandler(
        filename=logfile, encoding='utf-8'
    )

    return logfile_handler


def get_logging_formatter():
    return logging.Formatter(
        '%(newline)s%(levelname)s %(asctime)s %(name)s%(newline)s'
        '    %(job)s%(message)s'
    )


def setup_mq_log_handler(host, username, password):
    rabbit_handler = MQHandler(
        host=host,
        username=username,
        password=password,
        routing_key='mqsf.logger'
    )
    rabbit_handler.setFormatter(get_logging_formatter())

    return rabbit_handler


def normalize_dictionary(data):
    for key, value in data.items():
        normalize_data(data, value, key)

    return data


def normalize_list(data):
    for index, value in enumerate(data):
        normalize_data(data, value, index)

    return data


def normalize_data(data, value, key):
    if hasattr(value, 'strip'):
        data[key] = value.strip()
    elif isinstance(value, dict):
        data[key] = normalize_dictionary(value)
    elif isinstance(value, list):
        data[key] = normalize_list(value)

    return data
