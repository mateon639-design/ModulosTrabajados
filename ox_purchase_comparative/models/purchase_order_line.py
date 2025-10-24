# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrderLineExt(models.Model):

    _inherit = 'purchase.order.line'

    req_ord_id = fields.Many2one(related='order_id.requisition_ord_id', string='Requisicion', store=True)
    payment_term_id = fields.Many2one(related='order_id.payment_term_id', string='Plazo de pago', store=True)
    payment_term = fields.Char(string='Plazo de pago')

    # @api.model
    # def create(self, vals):
    #     for rec in self:
    #         if not vals.get('payment_term'):
    #             vals['payment_term'] = rec.order_id.payment_term_id.id
    #         result = super(PurchaseOrderLineExt, self).create(vals)
    #         return result

    # def write(self, vals):
    #     res = super(PurchaseOrderLineExt, self).write(vals)
    #     if 'payment_term' not in vals:
    #         for rec in self:
    #             rec.update({'payment_term': rec.order_id.payment_term_id.name})
    #     return res

    # def _get_name_payment_term(self):
    #     name = ''
    #     for p in self:
    #         if p.payment_term_id:
    #             name = p.payment_term_id.name
    #         p.payment_term = name
    