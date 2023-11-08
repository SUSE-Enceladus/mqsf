# Copyright (c) 2023 SUSE LLC.  All rights reserved.
#
# This file is part of mqsf.
#

import pluggy

hookimpl = pluggy.HookimplMarker('mqsf')
"""Marker to be imported and used in plugins (and for own implementations)"""
