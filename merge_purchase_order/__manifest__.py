# -*- coding: utf-8 -*-

{
    'name': 'Merge Purchase Order',
    'category': 'Purchases',
    'summary': 'This module will merge purchase order.',
    'version': '13.0.1.0.1',
    'website': 'http://www.aktivsoftware.com',
    'author': 'Aktiv Software',
    'description': 'Merge Purchase Order',
    'license': "AGPL-3",

    'depends': ['purchase', 'stock', 'l10n_us'],
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
