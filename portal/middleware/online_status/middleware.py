# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from __future__ import unicode_literals

from django.core.cache import cache

from conf import online_status_settings as config
from status import refresh_user, refresh_users_list, OnlineStatus


class OnlineStatusMiddleware(object):
    """Cache OnlineStatus instance for an authenticated User"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.set_status(request)

        response = self.get_response(request)

        return response

    def set_status(self, request):
        if request.user.is_authenticated:
            onlinestatus = cache.get(config.CACHE_PREFIX_USER % request.user.pk)
        elif not config.ONLY_LOGGED_USERS:
            onlinestatus = cache.get(
                config.CACHE_PREFIX_ANONYM_USER % request.session.session_key
            )
        else:
            return

        if not onlinestatus:
            onlinestatus = OnlineStatus(request)

        refresh_user(request)
        refresh_users_list(request, updated=onlinestatus)