# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseRequisitionLine(models.Model):

    _name = 'purchase.requisition.order.line'
    _description = 'Purchase Requisition Line'

    
    requisition_ord_id = fields.Many2one('purchase.requisition.order', string='Requisicion')
    product_id = fields.Many2one('product.product', string='Producto')
    qty = fields.Float(string='Cantidad')
    coste = fields.Float(string='Costo Estimado')
    approvers_ids = fields.Many2many('res.users', string='Aprobado por')
    approvers_refuse_ids = fields.Many2many('res.users', relation='purchase_res_users_refuse_rel', string='Rechazado por')
    approvers_especification_ids = fields.Many2many('res.users', relation='purchase_res_users_especification_rel', string='Requiere especificaciones')
    notes = fields.Html(string='Observaciones')

    def action_open_wiz_event(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Evento de requisición",
            "res_model": "wiz.purchase.requisition.order.line",
            "views": [[False, "form"]],
            "view_id": "wiz_purchase_requisition_order_line_view_form",
            "target": "new",
            "domain": "[('id','='," + str(self.id) +")]",
            "context": "{'active_id': " + str(self.id) + "}",
        }
    
    def action_open_wiz_event_log(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Eventos de requisición",
            "res_model": "purchase.requisition.order.log",
            "views": [[False, "tree"]],
            "view_id": "purchase_requisition_order_log_action",
            "target": "new",
            "domain": "[('requisition_ord_line_id','='," + str(self.id) +")]",
        }
        


        
    

    
    
    

    
    
    