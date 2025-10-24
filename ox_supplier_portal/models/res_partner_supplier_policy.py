# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartnerSupplierPolicy(models.Model):

    _name = 'res.partner.supplier.policy'
    _description = 'Requisito'

    name = fields.Char(string='Nombre política')
    description = fields.Html(string='Detalle política')
    
    def init(self):

        policy = self.env['res.partner.supplier.policy'].search_count([])

        if policy == 0:

            cr1 = self.env['res.partner.supplier.policy'].create({
                'name':'Política de calidad'
            })
            cr2 = self.env['res.partner.supplier.policy'].create({
                'name':'Acuerdo de confidencialidad'
            })
            cr3 = self.env['res.partner.supplier.policy'].create({
                'name':'Politica de protección de datos'
            })
    