# -*- coding: utf-8 -*-
{
    'name': "Modulo Compras Comparativo - Odoo Xpert SAS",

    'summary': """
       Modulo Compras Comparativo""",

    'description': """
        Modulo Ventas Extendido
    """,

    'author': "Odoo Xpert SAS",
    'website': "https://www.odooxp.com",

    'category': 'Services',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'ox_res_partner_ext_co', 'hr', 'ox_supplier_portal'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/purchase_requisition_ord.xml',
        'views/purchase_requisition_rule.xml',
        'views/purchase_requisition_ord_concept.xml',
        'views/purchase_order_line.xml',
        'views/menus.xml',
        'wizards/wiz_event_req_line.xml',
        'wizards/wiz_event_notes.xml',
        'views/templates.xml',
    ],
}
