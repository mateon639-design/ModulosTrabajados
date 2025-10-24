# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import base64
from io import BytesIO
from dateutil.relativedelta import relativedelta

class PurchaseRequisitionOrder(models.Model):

    _name = 'purchase.requisition.order'
    _description = 'Requisicion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_supplier_ids(self):
        suppliers = self.env['res.partner.supplier'].sudo().search([('state','=','done')]).partner_id.ids
        return [('id', 'in', suppliers)]

    name = fields.Char(string='Codigo', required=True, copy=False, default=lambda self: _('New'))
    date_estimed = fields.Date(string='Fecha estimada de compra', required=True, tracking=True)
    date_limit = fields.Date(string='Fecha limite licitación', required=True, tracking=True)
    state = fields.Selection(string='Estado', selection=[('draft', 'Borrador'), ('in_progress', 'En Progreso'), 
                                                         ('to_quote', 'Por Cotizar'), ('to_supplier', 'Ofertado'),
                                                         ('quoted', 'Cotizada'),
                                                         ('final_approval', 'En Aprobación Final'), 
                                                         ('approved', 'Aprobado'), ('refused', 'Rechazado'), 
                                                         ('canceled', 'Cancelado'), ('done', 'Finalizado')], default='draft', tracking=True)
    approvers_ids = fields.Many2many('res.users', string='Aprobadores', tracking=True)
    other_approvers_ids = fields.Many2many('res.users', 'purchase_req_order_other_approvers_rel', string='Aprobadores Adicionales', tracking=True)
    approvers_order_ids = fields.Many2many('res.users', 'purchase_req_order_approvers_rel', string='Aprobadores', tracking=True)
    suppliers_ids = fields.Many2many('res.partner', 'purchase_req_order_supplier_rel', string='Proveedores', tracking=True, domain=_get_supplier_ids)

    requisition_ord_line_ids = fields.One2many('purchase.requisition.order.line', 'requisition_ord_id', string='Productos')
    
    purchase_ids = fields.One2many('purchase.order', 'requisition_ord_id', string='Cotizaciones / Ordenes de compra')

    technical_specifications = fields.Html(string='Especificaciones Técnicas', tracking=True)
    requirement_att = fields.Binary(string='Adjunto técnico')
    requirement_att_name = fields.Char(string='Adjunto técnico', default='Descargar')

    amount_total_estimed = fields.Float(string='Valor Compra Estimado', compute='_amount_total_requisition', store=True)
    amount_total_confirmed = fields.Float(string='Valor Compra confirmado', compute='_amount_total_requisition')
    amount_total = fields.Float(string='Valor Max. Compra')
    department_id = fields.Many2one('hr.department', string='Area', tracking=True)
    concept_id = fields.Many2one('purchase.requisition.order.concept', string='Concepto', tracking=True)
    notes_selection = fields.Text(string='Nota de selección', tracking=True) 

    @api.onchange('date_estimed')
    def _onchange_date_estimed(self):
        self.date_limit = self.date_estimed
    
    @api.onchange('department_id')
    def _onchange_department_id(self):
        self._get_approvers_ids()

    @api.onchange('concept_id')
    def _onchange_concept_id(self):
        self._get_approvers_ids()

    @api.onchange('requisition_ord_line_ids')
    def _onchange_requisition_ord_line_ids(self):
        self._get_approvers_ids()
    
    def _get_approvers_ids(self):
        
        rules = self._get_rules()

        self.approvers_ids = [(5)]

        for rule in rules:

            if self.amount_total_estimed < rule.amount:

                for ap in rule.approvers_ids:
                    self.approvers_ids = [(4, ap.id)]

                break

    @api.depends('requisition_ord_line_ids')
    def _amount_total_requisition(self):
        for req in self:

            amount_total = 0

            for ln in req.requisition_ord_line_ids:
                amount_total = amount_total + (ln.qty * ln.coste)

            req.amount_total_estimed = amount_total

            amount_total = 0

            for ln in req.purchase_ids:
                if ln.state in ('purchase','done'):
                    amount_total = amount_total + ln.amount_total

            req.amount_total_confirmed = amount_total
    
    def _validate_approval_proccess(self):
        for l in self.requisition_ord_line_ids:
            if len(l.approvers_ids) == (len(self.approvers_ids) + len(self.other_approvers_ids)):
                if self.state == 'in_progress':
                    self.state = 'to_quote'
                if self.state == 'final_approval':
                    self.state = 'approved'

    def _validate_quote_status(self):

        send_final_approve = True
        control = 0
        amount_total = self.amount_total

        for cot in self.purchase_ids:

            amount_total = cot.amount_total if cot.amount_total > amount_total else amount_total

            if (cot.state not in ('to approve', 'cancel')) and control == 0:
                send_final_approve = False
                control += 1

        self.amount_total = amount_total

        if send_final_approve:
            self.state = 'quoted'
                
    def action_init_progress(self):

        if len(self.requisition_ord_line_ids) < 1:
            raise ValidationError('Debe ingresar mínimo una línea de producto para iniciar el proceso de requisición!')

        self.env.ref("ox_purchase_comparative.purchase_requisition_event_template").send_mail(self.id, force_send=True)
        self.state = 'in_progress'

    def action_send_supplier(self):

        if not self.suppliers_ids:
            raise ValidationError('Mínimo debe tener un proveedor asignado a la requisición para generar la cotización!')

        self._create_purchase_orders()
        self.state = 'to_supplier'

    def action_final_approval(self):

        for line in self.requisition_ord_line_ids:
            line.approvers_ids = [(5)] 
            line.approvers_refuse_ids = [(5)] 
            line.approvers_especification_ids = [(5)] 

        rules = self._get_rules()

        for rule in rules:
            if self.amount_total < rule.amount:
                self.approvers_order_ids = (rule.approvers_ids  + self.other_approvers_ids)
                break
        
        self.env.ref("ox_purchase_comparative.purchase_requisition_event_template").send_mail(self.id, force_send=True)

        self.state = 'final_approval'

    def action_done(self):

        amount_total = 0

        for cot in self.purchase_ids:
            if cot.state == 'to approve':
                amount_total += cot.amount_total

        if amount_total != self.amount_total:
            raise ValidationError('El valor máximo de compra debe coincidir con el valor de las cotizaciones que se van aprobar!')

        for ln in self.purchase_ids:
            if ln.state not in ('to approve', 'cancel'):
                raise ValidationError('Para finalizar una requisición, las cotizaciones deben estar por aprobar o canceladas!')
        
        for cot in self.purchase_ids:
            if cot.state == 'to approve':
                cot.button_approve()
                cot.button_unlock()
        
        self.state = 'done'

    def action_cancel(self):
        self.state = 'canceled'

    def _create_purchase_orders(self):

        orders = 0
        
        for supplier in self.suppliers_ids:

            vals = {
                'partner_id': supplier.id,
                'date_order': self.date_estimed + relativedelta(hours=6),
                'date_planned': self.date_estimed + relativedelta(hours=6),
                'requisition_ord_id': self.id
            }

            order_exist = self.env['purchase.order'].search([('requisition_ord_id','=',self.id), ('partner_id','=',supplier.id)])

            if not order_exist:

                orders += 1

                purchase = self.env['purchase.order'].create(vals)

                line_env = self.env['purchase.order.line']
                
                for product in self.requisition_ord_line_ids:

                    new_line = line_env.create({
                                'product_id': product.product_id.id,
                                'product_qty': product.qty,
                                'order_id': purchase.id,
                                'price_unit' : 0
                            })
                    
                template = self.env.ref("ox_purchase_comparative.purchase_order_supplier_template")

                if self.requirement_att:
                    attachment_string = BytesIO(base64.b64decode(self.requirement_att))
                    data_record = base64.b64encode(attachment_string.getvalue())

                    ir_values = {
                        'name': "AdjuntoTecnico.pdf",
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'application/x-pdf',
                    }
                    data_id = self.env['ir.attachment'].create(ir_values)
                    template.attachment_ids = [(6, 0, [data_id.id])]

                mail_id = template.send_mail(purchase.id, force_send=True)

                purchase.state = 'sent'

                if self.requirement_att:
                    template.attachment_ids = [(3, data_id.id)]

        if orders > 0:
            self.message_post(body="Proveedores Notificados")

    def _get_event_mails(self):

        state = self.state  

        list_dest = []
        approvers = False

        if state == 'in_progress' or state == 'draft':
            approvers = self.approvers_ids + self.other_approvers_ids

        #if state == 'final_approval':
        #    approvers = self.approvers_order_ids

        if approvers:
            for item in approvers:
                partner = self.env['res.users'].search([('id', '=', item.id)])
                if partner.id not in list_dest:
                    list_dest.append(str(partner.partner_id.id))

        list_dest = ','.join(list_dest)

        return str(list_dest)

    def _get_rules(self):

        domain = [('department_id','=',self.department_id.id)]

        if self.concept_id:
            domain.append(('concept_id','=',self.concept_id.id))
        else:
            domain.append(('concept_id','=',False))

        rules = self.env['purchase.requisition.order.rule'].search(domain, order='amount')

        return rules

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.requisition.order.seq', None) or _('New')
        result = super(PurchaseRequisitionOrder, self).create(vals)
        return result
    
    def action_open_wiz_comparative(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Comparativo de compras",
            "res_model": "purchase.order.line",
            "views": [[False, "pivot"]],
            "view_id": "purchase_order_line_view_pivot",
            "target": "fullscreen",
            "domain": "[('req_ord_id','='," + str(self.id) +")]",
        }
    

class PurchaseRequisitionOrderLog(models.Model):

    _name = 'purchase.requisition.order.log'
    _description = 'Purchase Requisition Log'

    requisition_ord_id = fields.Many2one('purchase.requisition.order', string='Requisicion')
    requisition_ord_line_id = fields.Many2one('purchase.requisition.order.line', string='Linea de requisicion')
    name = fields.Char(string='Accion')
    note = fields.Text(string='Nota')