# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Reliable Invoice Additional",
    'summary': 'Additinal Fields and Validations',
    'category': 'Invoice',
    'author': 'Ralf Cabarogias',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'account'
        ],
    'data': [
        'views/account_invoice.xml',

    ],
	'installable': True,
    'application': False,

}
