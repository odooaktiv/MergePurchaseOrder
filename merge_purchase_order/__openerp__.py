# -*- coding: utf-8 -*-

{
    'name': 'Merge Purchase Order',
    'category': 'Purchase',
    'version': '9.0.1.0.1',
    'summary': 'This module will merge purchase order.',
    'website': 'http://www.aktivsoftware.com',
    'author': 'Aktiv Software',
    'description': 'Merge Purchase Order',
    'license': "AGPL-3",

    'depends': [
        'purchase',
        'stock'
    ],

    'data': [
        'wizard/merge_puchase_order_wizard_view.xml',
    ],

    'images': [
        'static/description/banner.jpg',
    ],

    'auto_install': False,
    'installable': True,
    'application': False

}
