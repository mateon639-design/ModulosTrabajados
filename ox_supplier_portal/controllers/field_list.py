# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import werkzeug
from werkzeug.urls import url_encode
import json
from odoo import http, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError
from odoo.http import content_disposition, Controller, request, route, Response

from datetime import datetime, timedelta, date, time

import logging
_logger = logging.getLogger(__name__)

class SupplierPortalList(Controller):

    @route(['/portal/city/<int:state_id>'], type='http', auth='public', methods=['GET'], cors='*', csrf=False, website=True)
    def get_portal_city(self, state_id, **kw):

        request.update_env(1)

        vals = []

        if state_id > 0:
            cities = request.env['res.city'].search([('state_id', '=', state_id)])
        else:
            cities = []

        for city in cities:
            vals.append({'' + str(city.id): str(city.name) })
        
        return str(json.dumps(vals))
    
    @route(['/portal/state/<int:country_id>'], type='http', auth='public', methods=['GET'], cors='*', csrf=False, website=True)
    def get_portal_state(self, country_id, **kw):

        request.update_env(1)

        vals = []

        if country_id > 0:
            states = request.env['res.country.state'].search([('country_id', '=', country_id)])
        else:
            states = []

        for state in states:
            vals.append({'' + str(state.id): str(state.name)})
        
        return str(json.dumps(vals))