# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import werkzeug
from werkzeug.urls import url_encode
import json
from odoo import http, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError
from odoo.http import content_disposition, Controller, request, route, Response
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.purchase.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import CustomerPortal as CustomerPortalP
from odoo.addons.auth_signup.models.res_users import SignupError
import base64
from datetime import datetime, timedelta, date, time
import pathlib

import logging
_logger = logging.getLogger(__name__)

class SupplierPortal(Controller):

    @route(['/my/supplier/register'], type='http', auth='user', methods=['GET', 'POST'], cors='*', csrf=False, website=True)
    def supplier_register(self, **kw):

        values = {}      

        if request.httprequest.method == 'POST':

            try:
                partner_id = request.env.user.partner_id
                link_up = partner_id._get_link_up()
                request.update_env(1)

                form = int(kw.get('frp'))

                if form == 1:

                    country_id = int(kw.get('country_id'))
                    state_id = int(kw.get('state_id')) if int(kw.get('state_id')) != 0 else False
                    city_id = int(kw.get('city_id')) if int(kw.get('city_id')) != 0 else False
                    partner_street = kw.get('partner_street')
                    partner_mobile = kw.get('partner_mobile')
                    partner_web = kw.get('partner_web')
                    partner_email = kw.get('partner_email')
                    rep_leg_name = kw.get('rep_leg_name', False)
                    rep_leg_identification_type_id = kw.get('rep_leg_identification_type_id', False)
                    rep_leg_ref = kw.get('rep_leg_ref', False)
                    rep_leg_email = kw.get('rep_leg_email', False)
                    rep_leg_mobile = kw.get('rep_leg_mobile', False)

                    partner_id.write({
                        'country_id': country_id,
                        'state_id': state_id,
                        'city_id': city_id,
                    })

                    partner_id.street = partner_street
                    partner_id.mobile = partner_mobile
                    partner_id.website = partner_web
                    partner_id.email = partner_email

                    if rep_leg_name:

                        representante_legal_id = request.env['res.partner'].search([('ref','=',rep_leg_ref)])

                        if not representante_legal_id:
                            vals = {
                                'company_type': 'person',
                                'name': rep_leg_name,
                                'ref': rep_leg_ref,
                                'l10n_latam_identification_type_id': rep_leg_identification_type_id,
                                'mobile': rep_leg_mobile,
                                'email': rep_leg_email,
                            }

                            representante_legal_id = request.env['res.partner'].create(vals)

                        partner_id.representante_legal_id = representante_legal_id

                    if link_up:
                        link_up.info_proveedor = True

                if form == 2:

                    partner_f_position_id = kw.get('partner_f_position_id')
                    partner_maneja_retencion = kw.get('partner_maneja_retencion')
                    partner_economic_activity = kw.get('partner_economic_activity')
                    partner_society_id = kw.get('partner_society_id')

                    if partner_f_position_id:
                        fiscal_position_id = request.env['account.fiscal.position'].search([('id','=',partner_f_position_id)])
                        partner_id.property_account_position_id = fiscal_position_id

                    partner_id.retencion = True if partner_maneja_retencion == "True" else False

                    partner_society_id = request.env['res.partner.society'].search([('id','=',partner_society_id)])
                    partner_id.society_type_id = partner_society_id

                    eco_acts = partner_economic_activity.split(",")

                    for activity in eco_acts:

                        act = request.env['res.partner.economic.activity'].sudo().search([('code','=',str(activity))])

                        if act:
                            partner_id.economic_act_ids = [(4, act.id)] 

                    if link_up:
                        link_up.info_tributaria = True

                if form == 3:
                    
                    partner_account_bank = kw.get('partner_bank_id')
                    partner_account = kw.get('partner_account_bank')
                    partner_account_type = kw.get('partner_account_type')
                    partner_payment_term_id = kw.get('partner_payment_term_id')

                    bank_account_id = request.env['res.partner.bank'].search([('partner_id','=',partner_id.id), ('default_supplier','=',True)])
                    
                    if not bank_account_id:

                        vals = {
                            'partner_id': partner_id.id,
                            'acc_number': partner_account,
                            'bank_id': partner_account_bank,
                            'type_account': partner_account_type,
                            'default_supplier': True
                        }

                        bank_account_id = request.env['res.partner.bank'].create(vals)

                    partner_id.property_supplier_payment_term_id = request.env['account.payment.term'].search([('id','=',partner_payment_term_id)])

                    if link_up:
                        link_up.info_metodo_pago = True

                if form == 4:

                    dataJSON = json.loads(kw.get('ref_data'))

                    counter = 0

                    contact_to_del = []
                    contact_cr = []

                    for n in dataJSON:
                        ref_name = dataJSON[str(counter)].get('ref_name').upper()
                        ref_type = dataJSON[str(counter)].get('ref_type')
                        ref_cargo = dataJSON[str(counter)].get('ref_cargo').upper()
                        ref_street = dataJSON[str(counter)].get('ref_street').upper()
                        ref_mobile = dataJSON[str(counter)].get('ref_mobile')
                        ref_email = dataJSON[str(counter)].get('ref_email')
                        ref_res = int(dataJSON[str(counter)].get('ref_res'))
                        counter += 1

                        milliseconds = int(datetime.now().timestamp())
                        ref = 'CT' + str(milliseconds)

                        vals = {
                            'is_contact_customer': True,
                            'tipo_contacto': ref_type,
                            'name': ref_name,
                            'function': ref_cargo,
                            'street': ref_street,
                            'email': ref_email,
                            'mobile': ref_mobile,
                            'company_type': 'person',
                            'parent_id': partner_id.id,
                            'country_id': partner_id.country_id.id,
                            'state_id': partner_id.state_id.id,
                            'city_id': partner_id.city_id.id,
                            'ref': ref,
                        }

                        if ref_res == 0:
                            new_contact = request.env['res.partner'].create(vals)
                            contact_cr.append(new_contact.id)
                        if ref_res > 0:
                            contact_cr.append(ref_res)

                    contact_to_del = request.env['res.partner'].search([('parent_id','=',partner_id.id), ('id','not in',contact_cr)])
                    
                    for contact in contact_to_del:
                        contact.active = False

                    link_up.info_referencias = True

                if form == 5:

                    for line in link_up.line_ids:
                            key_b = 't_att@' + str(line.id)
                            for item in kw:
                                if key_b in item:
                                    attachment = kw.get(item, False)
                                    if attachment:
                                        ext = pathlib.Path(attachment.filename).suffix
                                        if ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
                                            return Response(str(json.dumps({'error': 'Solo se permiten archivos adjuntos con las siguientes extensiones (jpg, jpeg, png, pdf)'})), status=202)
                    
                    for line in link_up.line_ids:

                            key_b = 't_att@' + str(line.id)

                            for item in kw:

                                if key_b in item:

                                    attachment = kw.get(item, False)
                                    note = kw.get('t_note@' + str(line.id), False)

                                    if not attachment and not line.req_optional:
                                        return Response(str(json.dumps({'error': 'Uno o mas requisitos obligatorios no está correctamente diligenciado!'})), status=202)

                                    if attachment:
                                        
                                        ext = pathlib.Path(attachment.filename).suffix
                                        file_b64 = base64.b64encode(attachment.read())

                                        line.attach = file_b64
                                        line.note = note
                                        line.completed = True

                    link_up.info_requisitos = True

                if form == 6:

                    policies = request.env['res.partner.supplier.policy'].sudo().search([], order='name')

                    for pol in policies:
                        if not kw.get('partner_chk_policy_' + str(pol.id)):
                            return Response(str(json.dumps({'error': 'Debe aceptar todas las políticas para continuar!'})), status=202)

                    if link_up:
                        if not link_up.info_proveedor or not link_up.info_tributaria or not link_up.info_metodo_pago or not link_up.info_referencias or not link_up.info_requisitos:
                             return Response(str(json.dumps({'error': 'La aceptiación de poliíticas es el último paso del registro, primero diligencie las secciones anteriores para finalizar el proceso!!'})), status=202)

                        link_up.info_politicas = True

                if link_up._get_progress() == 100:
                    link_up.state = 'pre_validate'

                return Response(str(json.dumps({'message': 'Sección Actualizada', 'id': partner_id.id})), status=200)
            except Exception as e:
                return Response(str(json.dumps({'message': 'Unexpected error: {}'.format(str(e))})), status=500)

        if request.httprequest.method == 'GET':

            partner_id = request.env.user.partner_id

            states = request.env['res.country.state'].search([('country_id','=',49)], order='name asc')
            cities = request.env['res.city'].search([('state_id','=',partner_id.state_id.id)], order='name asc')
            fiscal_positions = request.env['account.fiscal.position'].search([], order='name asc')
            society_types = request.env['res.partner.society'].search([], order='name asc')
            banks = request.env['res.bank'].search([])
            payment_terms = request.env['account.payment.term'].search([])
            policies = request.env['res.partner.supplier.policy'].sudo().search([], order='name')


            country_states = []
            account_fiscal_positions = []
            city_states = []
            society_type_ids = []
            bank_ids = []
            payment_terms_ids = []
            partner_economic_activity_ids = []

            for state_id in states:
                country_states.append(state_id)

            for city_id in cities:
                city_states.append(city_id)

            for fiscal_position in fiscal_positions:
                account_fiscal_positions.append(fiscal_position)

            for society_type in society_types:
                society_type_ids.append(society_type)

            for bank in banks:
                bank_ids.append(bank)

            for term in payment_terms:
                payment_terms_ids.append(term)

            for act in partner_id.economic_act_ids:
                partner_economic_activity_ids.append(act.code)

            partner_economic_activity = '' + ','.join(partner_economic_activity_ids)

            link_up = partner_id._get_link_up()

            partner_bank_id = request.env['res.partner.bank'].search([('partner_id','=',partner_id.id), ('default_supplier','=',True)])
            
            if partner_id:

                values.update({
                    'company_type': partner_id.company_type,
                    'partner_id': partner_id.id,
                    'partner_name': partner_id.name,
                    'l10n_latam_identification_type_id': partner_id.l10n_latam_identification_type_id.id,
                    'partner_email': partner_id.email,
                    'partner_mobile': partner_id.mobile,
                    'partner_street': partner_id.street,
                    'partner_state_id': partner_id.state_id.id if partner_id.state_id else 0,
                    'partner_city_id': partner_id.city_id.id if partner_id.city_id else 0,
                    'partner_f_position_id': partner_id.property_account_position_id.id,
                    'partner_society_id': partner_id.society_type_id.id,
                    'partner_economic_activity': partner_economic_activity,

                    'partner_bank_id': partner_bank_id.bank_id.id if partner_bank_id else 0,
                    'partner_account_bank': partner_bank_id.acc_number,
                    'partner_account_type': partner_bank_id.type_account,
                    'partner_payment_term_id': partner_id.property_supplier_payment_term_id.id,

                    'partner_web': partner_id.website,
                    'partner_ref_contact': partner_id.ref,
                    'rep_leg_name': partner_id.representante_legal_id.name,
                    'rep_leg_identification_type_id': partner_id.representante_legal_id.l10n_latam_identification_type_id.id,
                    'rep_leg_ref': partner_id.representante_legal_id.ref,
                    'rep_leg_email': partner_id.representante_legal_id.email,
                    'rep_leg_mobile': partner_id.representante_legal_id.mobile,
                    'partner_maneja_retencion': partner_id.retencion,
                    'country_states': country_states,
                    'city_states': city_states,
                    'fiscal_positions': account_fiscal_positions,
                    'partner_society_t': society_type_ids,
                    'partner_banks': bank_ids,
                    'payment_terms_ids': payment_terms_ids,
                    'contact_ids': partner_id.child_ids,
                    'requirements': link_up.line_ids,
                    'note': partner_id._get_link_up().note if partner_id._get_status_supplier() == 'requires_specifications' else '',
                    'supplier_policies': policies,
                })

        return request.render("ox_supplier_portal.supplier", values)

    @route(['/my/supplier/evaluation'], type='http', auth='user', methods=['GET'], cors='*', csrf=False, website=True)
    def get_supplier_evaluation(self, **kw):
        
        values = {}

        partner_id = request.env.user.partner_id

        evaluations = request.env['purchase.supplier.eval'].sudo().search([('partner_id','=',partner_id.id), ('state','=','evaluated')])
        evals = []

        for ev in evaluations:
            evals.append({
                'id': ev.id,
                'code': ev.name,
                'period': ev.period,
                'date': ev.fecha_evaluacion,
                'calification': ev.calification,
                'supplier_eval': dict(ev._fields['clasificacion_proveedor'].selection).get(ev.clasificacion_proveedor),
                'url': '/my/supplier/evaluation/' + str(ev.id)
            })

        values.update({
            'page_name': 'supplier_eval_page',
            'evaluations': evals,
        })

        return request.render("ox_supplier_portal.portal_supplier_eval", values)

    @http.route('/my/supplier/evaluation/<int:report_id>', methods=['GET'], csrf=False, type='http', auth="user", website=True)
    def supplier_evaluation_print(self, report_id = 0, **kw):

        partner_id = request.env.user.partner_id

        evaluation = request.env['purchase.supplier.eval'].sudo().search([('id','=',report_id), ('partner_id','=', partner_id.id)])

        if not evaluation:
            return request.redirect("/my/supplier/evaluation")

        pdf = request.env['ir.actions.report']._render_qweb_pdf('ox_supplier_evaluation.report_supplier_evaluation', report_id) 
        b64_pdf = base64.b64encode(pdf[0])

        if b64_pdf:
            pdf = base64.b64decode(b64_pdf)
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)

    @route(['/my/data'], type='http', auth='user', methods=['GET', 'POST'], cors='*', csrf=False, website=True)
    def admin_data_profile(self, resend_code = 0, **kw):

        values = {}

        # if request.httprequest.method == 'POST':

        #     try:
        #         partner_id = request.env.user.partner_id
        #         request.update_env(1)

        #         form = int(kw.get('frp'))

        #         if form == 1:

        #             country_id = int(kw.get('country_id'))
        #             state_id = int(kw.get('state_id')) if int(kw.get('state_id')) != 0 else False
        #             city_id = int(kw.get('city_id')) if int(kw.get('city_id')) != 0 else False
        #             partner_street = kw.get('partner_street')
        #             partner_mobile = kw.get('partner_mobile')
        #             partner_web = kw.get('partner_web')
        #             partner_email = kw.get('partner_email')
        #             rep_leg_name = kw.get('rep_leg_name')
        #             rep_leg_identification_type_id = kw.get('rep_leg_identification_type_id')
        #             rep_leg_ref = kw.get('rep_leg_ref')
        #             rep_leg_email = kw.get('rep_leg_email')
        #             rep_leg_mobile = kw.get('rep_leg_mobile')

        #             partner_id.write({
        #                 'country_id': country_id,
        #                 'state_id': state_id,
        #                 'city_id': city_id,
        #             })

        #             partner_id.street = partner_street
        #             partner_id.mobile = partner_mobile
        #             partner_id.email = partner_email
        #             if partner_web:
        #                 partner_id.website = partner_web

        #             representante_legal_id = request.env['res.partner'].search([('ref','=',rep_leg_ref)])

        #             if not representante_legal_id and kw.get('rep_leg_ref', False):

        #                 vals = {
        #                     'company_type': 'person',
        #                     'name': rep_leg_name,
        #                     'ref': rep_leg_ref,
        #                     'l10n_latam_identification_type_id': rep_leg_identification_type_id,
        #                     'mobile': rep_leg_mobile,
        #                     'email': rep_leg_email,
        #                 }

        #                 representante_legal_id = request.env['res.partner'].create(vals)

        #                 partner_id.representante_legal_id = representante_legal_id

        #             if kw.get('partner_image[0][0]', False):
        #                 name = kw.get('partner_image[0][0]').filename      
        #                 file = kw.get('partner_image[0][0]')
        #                 file_b64 = base64.b64encode(file.read())
        #                 partner_id.image_1920 = file_b64
                    
        #             partner_id.last_update_portal = datetime.now()

        #         return Response(str(json.dumps({'message': 'Sección Actualizada', 'id': partner_id.id})), status=200)
        #     except Exception as e:
        #         return Response(str(json.dumps({'message': 'Unexpected error: {}'.format(str(e))})), status=500)

        if request.httprequest.method == 'GET':

            mode = 10

            partner_id = request.env.user.partner_id
            partner_image = partner_id.image_1920

            # if partner_id.image_1920:
            #     res_id = request.env['ir.attachment'].sudo().search([('res_model','=','res.partner'), ('res_field','=','image_1920')], limit=1)
            #     partner_image = res_id.id if res_id else 0
            states = request.env['res.country.state'].search([('country_id','=',49)], order='name asc')
            cities = request.env['res.city'].search([('state_id','=',partner_id.state_id.id)], order='name asc')
            country_states = []
            city_states = []

            for state_id in states:
                country_states.append(state_id)

            for city_id in cities:
                city_states.append(city_id)

            if partner_id:

                values.update({
                    'company_type': partner_id.company_type,
                    'partner_id': partner_id.id,
                    'partner_name': partner_id.name,
                    'l10n_latam_identification_type_id': partner_id.l10n_latam_identification_type_id.id,
                    'partner_last_update': partner_id.last_update_portal.strftime("%Y/%m/%d") if partner_id.last_update_portal else 'Sin Actualizar',
                    'partner_email': partner_id.email if partner_id.email != partner_id.ref else False,
                    'partner_mobile': partner_id.mobile,
                    'partner_street': partner_id.street,
                    'partner_state_id': partner_id.state_id.id if partner_id.state_id else 0,
                    'partner_city_id': partner_id.city_id.id if partner_id.city_id else 0,
                    'partner_web': partner_id.website,
                    'partner_ref_contact': partner_id.ref,
                    'rep_leg_name': partner_id.representante_legal_id.name,
                    'rep_leg_identification_type_id': partner_id.representante_legal_id.l10n_latam_identification_type_id.id,
                    'rep_leg_ref': partner_id.representante_legal_id.ref,
                    'rep_leg_email': partner_id.representante_legal_id.email,
                    'rep_leg_mobile': partner_id.representante_legal_id.mobile,
                    'partner_maneja_retencion': partner_id.retencion,
                    'country_states': country_states,
                    'city_states': city_states,
                    'contact_ids': partner_id.child_ids,
                    'partner_image_val': partner_image,
                })

        return request.render("ox_supplier_portal.profile_data_update", values)

    @http.route(['/my/purchase/<int:order_line_id>/price'], methods=['POST'], type='http', auth="user", website=True)
    def supplier_price_update(self, order_line_id=None, access_token=None, **kw):

        nw_price = kw.get('price', 0)
        line = request.env['purchase.order.line'].sudo().search([('id','=',order_line_id)])
        order_id = line.order_id.id if line else 0

        try:
            order_sudo = CustomerPortalP._document_check_access(SupplierPortal,'purchase.order', order_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        try:
            line_id = int(line.id)
        except ValueError:
            return request.redirect(order_sudo.get_portal_url())

        if not line:
            return request.redirect(order_sudo.get_portal_url())
        
        line.price_unit = nw_price

        return request.redirect('/my/purchase/' + str(order_id) + '?access_token=' + access_token)

    @http.route(['/my/purchase/<int:order_id>/approve'], methods=['POST'], type='http', auth="user", website=True)
    def supplier_status_update(self, order_id=None, access_token=None, **kw):

        try:
            order_sudo = CustomerPortalP._document_check_access(SupplierPortal,'purchase.order', order_id, access_token)
            order_sudo.state = 'to approve'

        except (AccessError, MissingError):
            return request.redirect('/my')
        
        return request.redirect('/my/purchase/' + str(order_id) + '?access_token=' + access_token)

class AuthSignupHomeExt(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):

        kw.update({'password': kw.get('login', 0)})
        kw.update({'confirm_password': kw.get('login', 0)})
        request.params['password'] = kw.get('login', 0)
        request.params['confirm_password'] = kw.get('login', 0)

        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                ref_partner = kw.get('login', 0)
                user_exist = request.env['res.users'].search([('login','=',ref_partner), ('ref','!=',0)])

                # if user_exist:
                #     qcontext['error'] = "Ya existe un nombre usuario con la cuenta a crear!"
                #     raise ValidationError("Ya existe un nombre usuario con la cuenta a crear!")                

                self.do_signup(qcontext)
                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )

                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)

                if user_sudo:

                    identification_type_id = request.env['l10n_latam.identification.type'].search([('id','=', kw.get('l10n_latam_identification_type_id' or 0))])
                    user_sudo.partner_id.company_type = 'person' if identification_type_id.name != 'NIT' else 'company'
                    user_sudo.partner_id.ref = ref_partner
                    user_sudo.partner_id.l10n_latam_identification_type_id = identification_type_id

                    user_sudo.partner_id.last_visit = 'customer'
                    user_sudo.partner_id.email = False

                    if user_sudo.partner_id.l10n_latam_identification_type_id.name != 'NIT':

                        partner_name = user_sudo.partner_id.name
                        name_parts = partner_name.split()

                        first_name = False
                        other_name = False
                        last_name = False
                        second_last_name = False

                        if len(name_parts) < 2:
                            first_name = name_parts[0]
                        elif len(name_parts) < 3:
                            first_name = name_parts[0]
                            last_name = name_parts[1]
                        elif len(name_parts) < 4:
                            first_name = name_parts[0]
                            other_name = name_parts[1]
                            last_name = name_parts[2]
                        else:
                            first_name = name_parts[0]
                            other_name = name_parts[1]
                            last_name = name_parts[2]
                            second_last_name = name_parts[3]

                        user_sudo.partner_id.primer_nombre = first_name
                        user_sudo.partner_id.otros_nombres = other_name
                        user_sudo.partner_id.primer_apellido = last_name
                        user_sudo.partner_id.segundo_apellido = second_last_name

                

                #if user_sudo and template:
                #    template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response
    
    def _prepare_signup_values(self, qcontext):
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        return values

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = self._prepare_signup_values(qcontext)
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    def _signup_with_values(self, token, values):
        login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        pre_uid = request.session.authenticate(request.db, login, password)
        if not pre_uid:
            raise SignupError(_('Authentication Failed.'))

class CustomerPortalExt(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        PurchaseOrder = request.env['purchase.order']
        SupplierEval = request.env['purchase.supplier.eval']

        if 'rfq_count' in counters:
            values['rfq_count'] =  PurchaseOrder.sudo().search_count([('partner_id', '=', partner.id), ('state', 'in', ('sent', 'to approve'))])

        if 'purchase_count' in counters:
            values['purchase_count'] = PurchaseOrder.sudo().search_count([('partner_id', '=', partner.id), ('state', 'in', ('sale', 'done'))])
        
        if 'supplier_eval_count' in counters:
            values['supplier_eval_count'] = SupplierEval.search_count([('partner_id','=',partner.id)])
        
            
        if values.get('rfq_count') == 0:
            values['rfq_count'] = '0'

        if values.get('purchase_count') == 0:
            values['purchase_count'] = '0'
        
        if values.get('supplier_eval_count') == 0:
            values['supplier_eval_count'] = '0'

        return values

    @http.route(['/my/rfq', '/my/rfq/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requests_for_quotation(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        return self._render_portal(
            "purchase.portal_my_purchase_rfqs",
            page, date_begin, date_end, sortby, filterby,
            [('state', 'in', ('sent','to approve'))],
            {},
            None,
            "/my/rfq",
            'my_rfqs_history',
            'rfq',
            'rfqs'
        )

class SupplierRegisterExt(CustomerPortal):

    @route('/my/request_supplier_register', type='http', auth='user', website=True, methods=['POST'])
    def validate_register_supplier(self, **post):
        partner = request.env.user.partner_id
        status_supplier = partner._get_status_supplier()
        if request.httprequest.method == 'POST':
            if status_supplier == 'none':
                partner._create_linkup_supplier()
        return request.redirect('/my')