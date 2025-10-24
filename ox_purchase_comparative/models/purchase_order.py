# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrderExt(models.Model):

    _inherit = 'purchase.order'

    requisition_ord_id = fields.Many2one('purchase.requisition.order', string='Requisicion')

    def write(self, values):
        res = super(PurchaseOrderExt, self).write(values)
        if self.requisition_ord_id and self.state == 'to approve':
            self.requisition_ord_id._validate_quote_status()
        return res
    
    def action_edit_order(self):
        return {
            'name': 'Solicitud de cotización',
            'view_mode': 'form',
            'view_id': False,
            'res_model': self._name,
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
        }