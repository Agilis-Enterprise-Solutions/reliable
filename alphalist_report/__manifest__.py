# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Customization Report",
    'summary': 'ALPHALIST OF PAYEES REPORT',
    'category': 'Accounting',
    'author': 'Ralf Cabarogias',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'base','account_accountant','account'
        ],
    'data': [
        'wizard/alphalist_payees.xml',
        'views/account_invoice.xml',

    ],
	'installable': True,
    'application': False,

}
