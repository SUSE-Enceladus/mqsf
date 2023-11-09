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

import logging

from amqpstorm import Connection

# project
from mqsf.log.filter import BaseServiceFilter
from mqsf.exceptions import MQConnectionException
from mqsf.utils import setup_mq_log_handler
from mqsf.config.base_config import BaseConfig


class Service(object):
    """
    Base class for MQ message broker

    Attributes

    * :attr:`host`
      MQ server host

    * :attr:`service_exchange`
      Name of service exchange
    """
    def __init__(self, service_exchange):
        self.channel = None
        self.connection = None

        self.service_exchange = service_exchange
        self.config = BaseConfig()  # TODO: determine how to set config file

        # mq settings
        self.mq_host = self.config.get_mq_host()
        self.mq_user = self.config.get_mq_user()
        self.mq_pass = self.config.get_mq_pass()

        self._open_connection()

        logging.basicConfig()
        self.log = logging.getLogger(
            '{0}Service'.format(self.service_exchange.title())
        )
        self.log.setLevel(logging.DEBUG)
        self.log.propagate = False

        mq_handler = setup_mq_log_handler(
            self.mq_host,
            self.mq_user,
            self.mq_pass
        )
        self.log.addHandler(mq_handler)
        self.log.addFilter(BaseServiceFilter())

        self.post_init()

    def post_init(self):
        """
        Post initialization method

        Implementation in specialized service class
        """
        pass

    def _declare_direct_exchange(self, exchange):
        """
        Declare/create exchange and set as durable.

        The exchange, queues and messages will survive a broker restart.
        """
        self.channel.exchange.declare(
            exchange=exchange, exchange_type='direct', durable=True
        )

    def _declare_queue(self, queue):
        """
        Declare the queue and set as durable.
        """
        return self.channel.queue.declare(queue=queue, durable=True)

    def _get_queue_name(self, exchange, name):
        """
        Return formatted name based on exchange and queue name.

        Example: obs.service
        """
        return '{0}.{1}'.format(exchange, name)

    def _open_connection(self):
        """
        Open connection or channel if currently closed or None.

        Raises: MQConnectionException if connection
                cannot be established.
        """
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = Connection(
                    self.mq_host,
                    self.mq_user,
                    self.mq_pass,
                    port=5672,  # TODO: add config option for port
                    virtual_host='my_vhost',  # TODO: add config option for vhost  # noqa
                    heartbeat=600  # TODO: add config option for heartbeat
                )
            except Exception as e:
                raise MQConnectionException(
                    'Connection to MQ server failed: {0}'.format(e)
                )

        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()
            self.channel.confirm_deliveries()

    def _publish(self, exchange, routing_key, message):
        """
        Publish message to the provided exchange with the routing key.
        """
        self.channel.basic.publish(
            body=message,
            routing_key=routing_key,
            exchange=exchange,
            properties={
                'content_type': 'application/json',
                'delivery_mode': 2
            },
            mandatory=True
        )

    def bind_queue(self, exchange, routing_key, name):
        """
        Bind queue on exchange to the provided routing key.

        All messages that match the routing key will be inserted in queue.
        """
        self._declare_direct_exchange(exchange)
        queue = self._get_queue_name(exchange, name)
        self._declare_queue(queue)
        self.channel.queue.bind(
            exchange=exchange, queue=queue, routing_key=routing_key
        )
        return queue

    def close_connection(self):
        """
        If channel or connection open, stop consuming and close.
        """
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()
            self.channel.close()

        if self.connection and self.connection.is_open:
            self.connection.close()

    def consume_queue(self, callback, queue_name, exchange):
        """
        Declare and consume queue.
        """
        queue = self._get_queue_name(exchange, queue_name)
        self._declare_queue(queue)
        self.channel.basic.consume(
            callback=callback, queue=queue
        )

    def unbind_queue(self, queue, exchange, routing_key):
        """
        Unbind the routing_key from the queue on given exchange.
        """
        queue = self._get_queue_name(exchange, queue)
        self.channel.queue.unbind(
            queue=queue, exchange=exchange, routing_key=routing_key
        )
