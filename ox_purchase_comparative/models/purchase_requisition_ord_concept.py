# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseRequisitionOrderConcept(models.Model):

    _name = 'purchase.requisition.order.concept'
    _description = 'Concepto de aprobación'

    name = fields.Char(string='Concepto', required=True)
    