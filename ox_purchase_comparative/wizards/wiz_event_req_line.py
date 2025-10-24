# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class WizPurchaseRequisitionOrderLine(models.TransientModel):
    
    _name = 'wiz.purchase.requisition.order.line'
    _description = 'Wizard gestion evento de aprobación requisicion'


    state = fields.Selection(string='Estado', selection=[('approved', 'Aprobado'), ('refused', 'Rechazado'), ('specifications', 'Requiere Especificaciones')], default='approved')
    note = fields.Text(string='Observacion')
    remove_event_prev = fields.Boolean(string='Anular evento anterior')
    

    def action_apply(self):

        lineId = self.env.context.get('active_id')
        
        line = self.env['purchase.requisition.order.line'].search([('id','=',lineId)])
        current_user = self.env.uid
        current_user = self.env['res.users'].search([('id','=',current_user)])

        if current_user not in line.requisition_ord_id.approvers_ids and current_user not in line.requisition_ord_id.other_approvers_ids and current_user not in line.requisition_ord_id.approvers_order_ids:
            raise ValidationError('No puede realizar gestión sobre una requisición en la cual no hace parte de los aprobadores!')

        if self.remove_event_prev:
            line.approvers_ids = [(3, current_user.id)]
            line.approvers_refuse_ids = [(3, current_user.id)]
            line.approvers_especification_ids = [(3, current_user.id)]

        if not self.remove_event_prev and (current_user in line.approvers_ids or current_user in line.approvers_refuse_ids or current_user in line.approvers_especification_ids):
           raise ValidationError('Ya realizó gestión sobre el item actual.')
        
        if self.note:
            line.notes = (line.notes or '') + self.note

        if self.state == 'approved':
            line.requisition_ord_id.message_post(body="Linea aprobada (" + line.product_id.name + ") [" + str(line.id) + "]")
            line.approvers_ids = [(4, current_user.id)]

        if self.state == 'refused':
            line.requisition_ord_id.message_post(body="Linea rechazada (" + line.product_id.name + ") [" + str(line.id) + "]")
            line.approvers_refuse_ids = [(4, current_user.id)]

        if self.state == 'specifications':
            line.requisition_ord_id.message_post(body="Linea requiere especificaciones (" + line.product_id.name + ") [" + str(line.id) + "]")
            line.approvers_especification_ids = [(4, current_user.id)]

        vals_log = {
            'requisition_ord_id': line.requisition_ord_id.id,
            'requisition_ord_line_id': line.id,
            'name': dict(self._fields['state'].selection).get(self.state),
            'note': self.note
        }

        self.env['purchase.requisition.order.log'].create(vals_log)

        line.requisition_ord_id._validate_approval_proccess()

        return {'type': 'ir.actions.act_window_close'}