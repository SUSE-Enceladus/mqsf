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
import os
import signal

from amqpstorm import AMQPError

from pluggy import PluginManager

from apscheduler import events
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from pytz import utc

from mqsf.service import Service
from mqsf.status_levels import EXCEPTION, SUCCESS
from mqsf.job_factory import BaseJobFactory
from mqsf import no_op_job
from mqsf import hookspecs
from mqsf.json_format import JsonFormat
from mqsf.utils import (
    remove_file,
    persist_json,
    restart_jobs,
    setup_logfile
)


class MessageService(Service):
    """
    Base class for message services that live in the image listener.
    """
    def post_init(self):
        """Initialize base service class and job scheduler."""
        self.listener_queue = 'listener'
        self.listener_msg_key = 'listener_msg'

        self.jobs = {}

        # setup service job directory
        self.job_directory = self.config.get_job_directory(
            self.service_exchange
        )
        os.makedirs(
            self.job_directory, exist_ok=True
        )

        self.prev_service = self.config.get_previous_service()

        pm = PluginManager('mqsf')

        if self.config.get_no_op_okay():
            pm.add_hookspecs(hookspecs)
            pm.register(no_op_job, 'NoOpJob')
            pm.load_setuptools_entrypoints('mqsf')

        # Create job factory
        self.job_factory = BaseJobFactory(
            service_name=self.service_exchange,
            plugin_manager=pm,
            can_skip=self.config.get_no_op_okay()
        )

        logfile_handler = setup_logfile(
            self.config.get_log_file(self.service_exchange)
        )
        self.log.addHandler(logfile_handler)

        self.bind_queue(
            self.prev_service,
            self.listener_msg_key,
            self.listener_queue
        )

        thread_pool_count = self.config.get_base_thread_pool_count()
        executors = {
            'default': ThreadPoolExecutor(thread_pool_count)
        }
        self.scheduler = BackgroundScheduler(executors=executors, timezone=utc)
        self.scheduler.add_listener(
            self._process_job_result,
            events.EVENT_JOB_EXECUTED | events.EVENT_JOB_ERROR
        )
        self.scheduler.add_listener(
            self._process_job_missed,
            events.EVENT_JOB_MISSED
        )

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        restart_jobs(self.job_directory, self._add_job)
        self.start()

    def _add_job(self, job_config):
        """
        Load and schedule job if job id does not already exist.
        """
        job_id = job_config['id']

        if job_id not in self.jobs:
            self.jobs[job_id] = job_config
            self.log.info(
                'Job will be scheduled.',
                extra={'job_id': job_id}
            )
            self._schedule_job(job_id)
        else:
            self.log.warning(
                'Job already scheduled.',
                extra={'job_id': job_id}
            )

    def _cleanup_job(self, job_id):
        """
        Job failed upstream.

        Delete job and notify the next service.
        """
        job_config = self.jobs[job_id]

        self.log.warning('Failed upstream.', extra={'job_id': job_id})
        self._delete_job(job_id)

        self._publish_message(job_config, job_id)

    def _delete_job(self, job_id):
        """
        Remove job from file store and delete from listener queue.

        Also attempt to remove any running instances of the job.
        """
        if job_id in self.jobs:
            self.log.info(
                'Deleting job.',
                extra={'job_id': job_id}
            )

            del self.jobs[job_id]

            job_file = '{0}job-{1}.json'.format(
                self.job_directory,
                job_id
            )

            remove_file(job_file)
        else:
            self.log.warning(
                'Job deletion failed, job is not queued.',
                extra={'job_id': job_id}
            )

    def _handle_listener_message(self, message):
        """
        Callback for listener messages.
        """
        listener_msg = self._get_listener_msg(
            message.body,
            '{0}_result'.format(self.prev_service)
        )

        job_id = None
        if listener_msg:
            status = listener_msg['status']
            job_id = listener_msg['id']

        if job_id and job_id not in self.jobs:
            self.jobs[job_id] = listener_msg

            job_file = '{0}job-{1}.json'.format(
                self.job_directory,
                job_id
            )
            persist_json(
                job_file,
                listener_msg
            )

            if status == SUCCESS:
                self._schedule_job(job_id)
            else:
                self._cleanup_job(job_id)
        elif job_id in self.jobs:
            self.log.warning(
                'Job already queued.',
                extra={'job_id': job_id}
            )

        message.ack()

    def _process_job_result(self, event):
        """
        Callback when job background process finishes.

        Handle exceptions and errors that occur and logs info to job log.
        """
        job_id = event.job_id
        job_config = self.jobs[job_id]
        metadata = {'job_id': job_id}

        self._delete_job(job_id)

        if event.exception:
            job_config['status'] = EXCEPTION
            msg = 'Exception in {0}: {1}'.format(
                self.service_exchange,
                event.exception
            )
            job_config.get('errors', []).append(msg)
            self.log.error(
                msg,
                extra=metadata
            )
        elif job_config['status'] == SUCCESS:
            self.log.info(
                '{0} successful.'.format(
                    self.service_exchange
                ),
                extra=metadata
            )
        else:
            self.log.error(
                'Error occurred in {0}.'.format(
                    self.service_exchange
                ),
                extra=metadata
            )

        self._publish_message(job_config, job_id)

    def _process_job_missed(self, event):
        """
        Callback when job background process misses execution.

        This should not happen as no jobs are scheduled, log any occurrences.
        """
        job_id = event.job_id
        metadata = {'job_id': job_id}

        self.log.warning(
            'Job missed during {0}.'.format(
                self.service_exchange
            ),
            extra=metadata
        )

    def _publish_message(self, job_config, job_id):
        """
        Publish message to next service exchange.
        """
        message = self._get_status_message(job_config)

        try:
            self.publish_job_result(self.service_exchange, message)
        except AMQPError:
            self.log.warning(
                'Message not received: {0}'.format(message),
                extra={'job_id': job_id}
            )

    def _schedule_job(self, job_id):
        """
        Schedule new job in background scheduler for job based on id.
        """
        try:
            self.scheduler.add_job(
                self._start_job,
                args=(job_id,),
                id=job_id,
                max_instances=1,
                misfire_grace_time=None,
                coalesce=True
            )
        except ConflictingIdError:
            self.log.warning(
                'Job already running. Received multiple '
                'listener messages.',
                extra={'job_id': job_id}
            )

    def _start_job(self, job_id):
        """
        Process job based on job id.
        """
        job_config = self.jobs[job_id]

        try:
            plugin = self.job_factory.create_job(job_config)
        except Exception as error:
            self.log.error(
                'Invalid job: {0}.'.format(error)
            )
            job_config['status'] = EXCEPTION
            job_config.get('errors', []).append(error)
        else:
            plugin.run_task(job_config, self.log)

    def _get_listener_msg(self, message, key):
        """Load json and attempt to get message by key."""
        try:
            listener_msg = json.loads(message)[key]
        except Exception:
            self.log.error(
                'Invalid listener message: {0}, '
                'missing key: {1}'.format(
                    message,
                    key
                )
            )
            listener_msg = None

        return listener_msg

    def _get_status_message(self, job_config):
        """
        Build and return json message.

        Message contains completion status to post to next service exchange.
        """
        key = '{0}_result'.format(self.service_exchange)
        return JsonFormat.json_message(
            {
                key: job_config
            }
        )

    def publish_job_result(self, exchange, message):
        """
        Publish the result message to the listener queue on given exchange.
        """
        self._publish(exchange, self.listener_msg_key, message)

    def start(self):
        """
        Start listener service.
        """
        self.scheduler.start()
        self.consume_queue(
            self._handle_listener_message,
            self.listener_queue,
            self.prev_service
        )

        try:
            self.channel.start_consuming()
        except Exception:
            self.stop()
            raise

    def stop(self, signum=None, frame=None):
        """
        Gracefully stop the service.

        Shutdown scheduler and wait for running jobs to finish.
        Close AMQP connection.
        """
        if signum:
            self.log.info(
                'Got a TERM/INTERRUPT signal, shutting down gracefully.'
            )
        else:
            self.log.info(
                'An unhandled Exception occurred in event loop, '
                'shutting down gracefully.'
            )

        self.scheduler.shutdown()
        self.close_connection()
