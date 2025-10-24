# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tools.translate import _
from odoo.tools import email_normalize
from odoo.exceptions import UserError

from odoo import api, fields, models, Command


_logger = logging.getLogger(__name__)

class PortalWizardUserExt(models.TransientModel):
    _inherit = 'portal.wizard.user'

    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': self.email,
            'login': self.email,
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })

    def action_grant_access_portal(self):
        """Grant the portal access to the partner.

        If the partner has no linked user, we will create a new one in the same company
        as the partner (or in the current company if not set).

        An invitation email will be sent to the partner.
        """

        for userportal in self:

            self.ensure_one()

            if userportal.is_portal or userportal.is_internal:
                raise UserError(_('The partner "%s" already has the portal access.', userportal.partner_id.name))

            group_portal = self.env.ref('base.group_portal')
            group_public = self.env.ref('base.group_public')
            user_sudo = userportal.user_id.sudo()

            if not user_sudo:

                # create a user if necessary and make sure it is in the portal group
                company = userportal.partner_id.company_id or self.env.company
                user_sudo = self.sudo().with_company(company.id)._create_user()

            if not user_sudo.active or not userportal.is_portal:
                user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id), (3, group_public.id)]})
                # prepare for the signup process
                user_sudo.partner_id.signup_prepare()

            return user_sudo
        
        return False