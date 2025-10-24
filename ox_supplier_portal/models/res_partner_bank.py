# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError

dict_status = [('pre_registered', 'Pre-Inscrito'), ('pre_validate', 'En Validación'), ('requires_specifications', 'Requiere Especificaciones'), 
        ('done', 'Aprobado'), ('refused', 'Rechazado'), ('under_renovation', 'En Renovación')]

class ResPartnerBankExt(models.Model):
    _inherit = 'res.partner.bank'

    default_supplier = fields.Boolean(string='Cuenta Proveedor Portal')
    