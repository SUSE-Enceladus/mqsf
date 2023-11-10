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

from amqpstorm import Connection

from logging.handlers import SocketHandler


class MQHandler(SocketHandler):
    """
    Log handler for sending messages to MQ.
    """
    def __init__(
        self,
        host='localhost',
        port=5672,
        exchange='logger',
        username='guest',
        password='guest',
        routing_key='mqsf.logger'
    ):
        """
        Initialize the handler instance.
        """
        super(MQHandler, self).__init__(host, port)

        self.username = username
        self.password = password
        self.exchange = exchange
        self.routing_key = routing_key

    def makeSocket(self):
        """
        Create a new instance of MQ socket connection.
        """
        return MQSocket(
            self.host,
            self.port,
            self.username,
            self.password,
            self.exchange,
            self.routing_key
        )

    def makePickle(self, record):
        """
        Format the log message to a json string.
        """
        mq_attrs = ['msg', 'job_id']

        data = {}
        record.msg = self.format(record)

        for attr in mq_attrs:
            if hasattr(record, attr):
                data[attr] = getattr(record, attr)

        return json.dumps(data, sort_keys=True)


class MQSocket(object):
    """
    MQ socket class.

    Maintains a connection for logging and publishing
    logs to exchange.
    """
    def __init__(
        self, host, port, username, password, exchange, routing_key
    ):
        """
        Initialize RabbitMQ socket instance.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange
        self.routing_key = routing_key
        self.connection = None
        self.channel = None
        self.open()
        self.declare_exchange()

    def close(self):
        """
        Close socket connection.
        """
        if self.channel and self.channel.is_open:
            self.channel.close()

        if self.connection and self.connection.is_open:
            self.connection.close()

    def declare_exchange(self):
        self.channel.exchange.declare(
            exchange=self.exchange,
            exchange_type='direct',
            durable=True
        )

    def open(self):
        """"
        Create/open connection and declare logging exchange.
        """
        if not self.connection or self.connection.is_closed:
            self.connection = Connection(
                self.host,
                self.username,
                self.password,
                port=self.port,
                kwargs={'heartbeat': 600}
            )

        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()

    def sendall(self, msg):
        """
        Override socket sendall method to publish message to exchange.
        """
        self.open()
        self.channel.basic.publish(
            body=msg,
            routing_key=self.routing_key,
            exchange=self.exchange,
            properties={
                'content_type': 'application/json',
                'delivery_mode': 2
            }
        )
