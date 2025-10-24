# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartnerSupplierContract(models.Model):

    _name = 'res.partner.supplier.contract'
    _description = 'Convenio Proveedor'

    link_up_id = fields.Many2one('res.partner.supplier', string='Vinculación')
    date_start = fields.Date(string='Fecha Inicial')
    date_end = fields.Date(string='Fecha Final')
    date_renew = fields.Date(string='Fecha Renovación')
    description = fields.Text(string='Descripción')
    
    
    