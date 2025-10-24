# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError

class ResCountryExt(models.Model):

    _inherit = 'res.country'

    web_enable_update_info = fields.Boolean(string='Disponible para actualización web')
    