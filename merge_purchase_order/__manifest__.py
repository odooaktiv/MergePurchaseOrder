# -*- coding: utf-8 -*-

{
    'name': 'Merge Purchase Order',
    'category': 'Purchases',
    'version': '10.0.1.0.1',
    'summary': 'This module will merge purchase order.',
    'website': 'http://www.aktivsoftware.com',
    'author': 'Aktiv Software',
    'license': 'AGPL-3',
    'description': 'Merge Purchase Order',

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
