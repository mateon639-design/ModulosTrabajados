# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartnerSupplierLineReq(models.Model):

    _name = 'res.partner.supplier.req'
    _description = 'Requisito'

    name = fields.Char(string='Requisito')
    req_optional = fields.Boolean(string='Opcional')
    type_req = fields.Selection(string='Tipo', selection=[('person', 'Individual'), ('company', 'Compañia')], default='company')
    active = fields.Boolean(string='Activo', default=True)
    
    
    