# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#

import logging
import sys
import traceback

# project
from mqsf.exceptions import MQSFException
from mqsf.message_service import MessageService


def main(service_name):
    """
    mqsf - create service application entry point
    """
    try:
        logging.basicConfig()
        log = logging.getLogger('MessageService')
        log.setLevel(logging.DEBUG)

        # run service, enter main loop
        MessageService(
            service_exchange=service_name
        )
    except MQSFException as e:
        # known exception
        log.error('{0}: {1}'.format(type(e).__name__, format(e)))
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
    except SystemExit:
        # user exception, program aborted by user
        sys.exit(0)
    except Exception as e:
        # exception we did no expect, show python backtrace
        log.error('Unexpected error: {0}'.format(e))
        traceback.print_exc()
        sys.exit(1)
