# -*- coding: utf-8 -*-
# models/survey_survey_inherit.py
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    # -----------------------------
    # Campos de configuración
    # -----------------------------
    audience_category_ids = fields.Many2many(
        "res.partner.category",
        "survey_audience_category_rel",
        "survey_id",
        "category_id",
        string="Públicos objetivo",
        help="Selecciona etiquetas de contactos (ej.: Empleados, Clientes, Estudiantes).",
        groups="base.group_user",  # Solo visible/legible en backend
    )

    response_deadline = fields.Datetime(
        string="Fecha límite de respuesta",
        help="Fecha y hora hasta la cual se aceptan respuestas a esta encuesta.",
        groups="base.group_user",  # Solo backend
    )

    # Modo calificable
    is_gradable = fields.Boolean(
        string="Calificable",
        help="Activa el modo calificable. Se calculará un puntaje final con base en las respuestas y el peso de cada pregunta.",
        groups="base.group_user",
    )

    # % mínimo para aprobar (0..100). Se usa solo cuando is_gradable = True
    min_score = fields.Float(
        string="Puntaje mínimo",
        help="Puntaje mínimo en porcentaje (0–100) para aprobar la encuesta. Solo aplica si la encuesta es calificable.",
        default=0.0,
        groups="base.group_user",
    )

    # -----------------------------
    # Validaciones y onchanges
    # -----------------------------
    @api.constrains('response_deadline')
    def _check_response_deadline_future(self):
        for rec in self:
            if rec.response_deadline and rec.response_deadline < fields.Datetime.now():
                raise ValidationError(_("La fecha límite de respuesta no puede estar en el pasado."))

    @api.constrains('min_score', 'is_gradable')
    def _check_min_score_range(self):
        for rec in self:
            if rec.is_gradable:
                if rec.min_score < 0.0 or rec.min_score > 100.0:
                    raise ValidationError(_("El puntaje mínimo debe estar entre 0 y 100."))

    @api.onchange('is_gradable')
    def _onchange_is_gradable(self):
        # Si se desactiva “Calificable”, el mínimo deja de aplicar; lo reseteamos.
        if not self.is_gradable:
            self.min_score = 0.0

    @api.model
    def default_get(self, fields_list):
        return super().default_get(fields_list)

    # =========================
    # Helpers público objetivo
    # =========================
    def _employee_private_address_field(self):
        """
        Devuelve el nombre del campo de dirección privada del empleado según la versión:
        posibles: 'private_address_id' (nuevo), 'address_home_id' (viejo), 'home_address_id' (algunas bases).
        """
        if "hr.employee" not in self.env:
            return None
        Employee = self.env["hr.employee"]
        for candidate in ("private_address_id", "address_home_id", "home_address_id"):
            if candidate in Employee._fields:
                return candidate
        return None

    def _partners_from_employees(self):
        """Partners asociados a empleados (usuario y dirección privada) sin romper entre versiones."""
        if "hr.employee" not in self.env:
            return self.env["res.partner"].browse()

        Employee = self.env["hr.employee"]
        employees = Employee.search([("active", "=", True)])
        partners = self.env["res.partner"].browse()

        # Partner del usuario del empleado (si existe)
        if "user_id" in Employee._fields:
            partners |= employees.mapped("user_id.partner_id")

        # Dirección privada según el campo disponible en tu versión
        private_field = self._employee_private_address_field()
        if private_field:
            partners |= employees.mapped(private_field)

        return partners.filtered(lambda p: p)

    def _partners_from_customers(self):
        """Partners marcados como clientes (compatibilidad con distintos campos)."""
        Partner = self.env["res.partner"]
        dom = [("active", "=", True)]
        if "customer_rank" in Partner._fields:
            dom += [("customer_rank", ">", 0)]
        elif "is_customer" in Partner._fields:
            dom += [("is_customer", "=", True)]
        elif "customer" in Partner._fields:
            dom += [("customer", "=", True)]
        return Partner.search(dom)

    def _partners_from_suppliers(self):
        """Partners marcados como proveedores (compatibilidad con distintos campos)."""
        Partner = self.env["res.partner"]
        dom = [("active", "=", True)]
        if "supplier_rank" in Partner._fields:
            dom += [("supplier_rank", ">", 0)]
        elif "is_supplier" in Partner._fields:
            dom += [("is_supplier", "=", True)]
        elif "supplier" in Partner._fields:
            dom += [("supplier", "=", True)]
        return Partner.search(dom)

    def _partners_from_category(self, category):
        """Partners que tienen la etiqueta dada."""
        return self.env["res.partner"].search([
            ("category_id", "in", category.id),
            ("active", "=", True),
        ])

    def _is_category_kind(self, category, kind):
        """
        Reconoce categorías especiales por nombre o xmlid:
        kind ∈ {'employee','customer','supplier'}
        """
        name = (category.name or "").lower()
        if kind == "employee":
            keys = ("emplead", "employee")
        elif kind == "customer":
            keys = ("cliente", "customer")
        else:
            keys = ("proveedor", "supplier")
        if any(k in name for k in keys):
            return True
        # por xmlid si existiera
        try:
            xmlid = category.get_external_id().get(category.id, "")
        except Exception:
            xmlid = ""
        if xmlid:
            if kind == "employee" and "employee" in xmlid:
                return True
            if kind == "customer" and "customer" in xmlid:
                return True
            if kind == "supplier" and "supplier" in xmlid:
                return True
        return False

    def _collect_target_partners(self):
        """
        Une los partners a invitar según audience_category_ids:
        - Empleados   → hr.employee (dirección privada / partner del usuario)
        - Clientes    → res.partner con marca de cliente
        - Proveedores → res.partner con marca de proveedor
        - Otras tags  → partners con esa etiqueta
        """
        Partner = self.env["res.partner"]
        all_partners = Partner.browse()
        for survey in self:
            partners = Partner.browse()
            for cat in survey.audience_category_ids:
                if self._is_category_kind(cat, "employee"):
                    partners |= self._partners_from_employees()
                elif self._is_category_kind(cat, "customer"):
                    partners |= self._partners_from_customers()
                elif self._is_category_kind(cat, "supplier"):
                    partners |= self._partners_from_suppliers()
                else:
                    partners |= self._partners_from_category(cat)
            all_partners |= partners
        # Quitar inactivos y duplicados
        return all_partners.filtered(lambda p: p.active)

    # =========================
    # Botón: asignar público
    # =========================
    def action_assign_audience(self):
        UserInput = self.env["survey.user_input"].sudo()

        for survey in self:
            if not survey.audience_category_ids:
                raise ValidationError(_("Selecciona al menos un 'Público objetivo'."))

            partners = survey._collect_target_partners()
            if not partners:
                raise ValidationError(_("No se encontraron contactos para el público objetivo seleccionado."))

            existing = UserInput.search([
                ("survey_id", "=", survey.id),
                ("partner_id", "in", partners.ids),
            ])
            existing_partner_ids = set(existing.mapped("partner_id").ids)

            to_create = []
            for partner in partners:
                if partner.id in existing_partner_ids:
                    continue
                vals = {
                    "survey_id": survey.id,
                    "partner_id": partner.id,
                    "state": "new",
                }
                if "email" in UserInput._fields:
                    vals["email"] = partner.email or False
                to_create.append(vals)

            if to_create:
                UserInput.create(to_create)

        # ⚠️ Cambios aquí: usar 'list' en lugar de 'tree', y definir 'views'
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Participaciones"),
            "res_model": "survey.user_input",
            "view_mode": "list,form",                # <-- Antes: "tree,form"
            "views": [(False, "list"), (False, "form")],
            "target": "current",
            "domain": [("survey_id", "=", self.id)],
            "context": {
                "default_survey_id": self.id,
                "search_default_survey_id": self.id,
            },
        }


class ResPartnerCategory(models.Model):
    _inherit = "res.partner.category"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Si se crea una etiqueta desde el widget de encuestas SIN parent,
        la colgamos bajo 'Públicos objetivo' (si existe la raíz del módulo).
        """
        new_vals = []
        root = self.env.ref("survey_extension.category_public_target_root", raise_if_not_found=False)
        for vals in vals_list:
            vals = dict(vals)
            if not vals.get("parent_id") and root:
                vals["parent_id"] = root.id
            new_vals.append(vals)
        return super().create(new_vals)
