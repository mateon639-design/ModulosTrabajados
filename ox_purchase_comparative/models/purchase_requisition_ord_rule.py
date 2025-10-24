# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseRequisitionOrderRule(models.Model):

    _name = 'purchase.requisition.order.rule'
    _description = 'Regla de aprobación'

    department_id = fields.Many2one('hr.department', string='Area', required=True)
    concept_id = fields.Many2one('purchase.requisition.order.concept', string='Concepto')
    amount = fields.Float(string='Monto máximo')
    active = fields.Boolean(string='Activo', default=True)
    approvers_ids = fields.Many2many('res.users', string='Aprobadores')