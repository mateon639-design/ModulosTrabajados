# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import random

dict_status = [('pre_registered', 'Pre-Inscrito'), ('pre_validate', 'En Validación'), ('requires_specifications', 'Requiere Especificaciones'), 
        ('done', 'Aprobado'), ('refused', 'Rechazado'), ('under_renovation', 'En Renovación')]

OPT_CHAR = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9']

class ResPartnerExt(models.Model):

    _inherit = 'res.partner'
    _description = 'Partner'

    link_up_ids = fields.One2many('res.partner.supplier', 'partner_id', string='Vinculaciones')
    supplier_status = fields.Char(string='Estado Vinculación', compute='_compute_link_up')
    retencion = fields.Boolean(string='Maneja Retención')
    
    def action_send_mail_supplier_register(self):

        for partner in self:

            current_email = partner.email
            link_up = partner._get_link_up()
            user_portal = partner.user_ids

            if not partner.ref:
                raise ValidationError('No puede otorgar acceso al portal de proveedores si no tiene asignado un número de identificación!')

            if not link_up:
                link_up = partner._create_linkup_supplier()
                
            if not user_portal:
                NewAccessPortal = self.env['portal.wizard'].sudo().create({})
                NewAccess = self.env['portal.wizard.user'].sudo().create({
                    'wizard_id': NewAccessPortal.id,
                    'partner_id': partner.id,
                    'email': partner.ref,
                    'email_state': 'ok'
                })

                user_id = NewAccess.action_grant_access_portal()
                user_id._change_password(partner.ref)
                user_id.partner_id.email = current_email
            
            link_up.info_proveedor = True
            link_up.info_tributaria = True
            link_up.info_metodo_pago = True
            link_up.info_referencias = True
            link_up.info_requisitos = True
            link_up.info_politicas = True
            link_up.action_done(False)
            link_up.message_post(body="Acceso A Portal Otorgado Manualmente")

            email = self.env.ref("ox_supplier_portal.supplier_register_portal_manual_template").send_mail(link_up.id, force_send=True, raise_exception=False)
            email_sent = self.env['mail.mail'].search([('id','=',email)])
            #link_up.message_post(body=email_sent.body)


    @api.depends('link_up_ids')
    def _compute_link_up(self):

        status = dict(dict_status)
        supplier_status = status.get('pre_registered')
        
        for state_line in self.link_up_ids:
            supplier_status = status.get(state_line.state) if state_line.active else 'pre_registered'

        self.supplier_status = supplier_status

    def _create_linkup_supplier(self):

        linkup = self.env['res.partner.supplier'].create({'partner_id': self.id})
        
        domain = [('type_req','=', self.company_type)]
        
        requirements = self.env['res.partner.supplier.req'].search(domain)

        for req in requirements:
            vals = {
                'link_up_id': linkup.id,
                'requirement_id': req.id,
                'req_optional': req.req_optional,
            }
            self.env['res.partner.supplier.line'].create(vals)

        return linkup
    
    def _get_status_supplier(self):
        status_supplier = self.env['res.partner.supplier'].search([('partner_id','=',self.id), ('active','=',True)], limit=1).state
        return status_supplier if status_supplier else 'none'

    def _get_link_up(self):
        link_up = self.env['res.partner.supplier'].search([('partner_id','=',self.id), ('active','=',True)], limit=1)
        return link_up

    def _default_code(self):       
        return "".join(random.choices(OPT_CHAR,k=2))