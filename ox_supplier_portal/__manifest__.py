# -*- coding: utf-8 -*-
{
    'name': "Modulo Proveedores Portal - Odoo Xpert SAS",

    'summary': """
       Modulo Proveedores Portal""",

    'description': """
        Modulo Proveedores Portal
    """,

    'author': "Odoo Xpert SAS",
    'website': "https://www.odooxp.com",

    'category': 'Services',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'auth_signup', 'ox_res_partner_ext_co', 'purchase', 'sale', 'account'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/templates.xml',
        'views/portal_supplier.xml',
        'views/portal_signup.xml',
        'views/portal_login.xml',
        'views/res_partner.xml',
        'views/res_partner_supplier.xml',
        'views/res_partner_supplier_req.xml',
        'views/res_partner_supplier_policy.xml',
        'views/res_country.xml',
        'views/menus.xml',
        'views/portal_main.xml',
        'views/portal_evaluation.xml',
        'views/profile_data_update.xml',
        'views/portal_purchase_order.xml'
    ],

    'assets': {
        'web.assets_frontend':[
            'ox_supplier_portal/static/src/js/supplier_portal.js',
        ],
    },

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
