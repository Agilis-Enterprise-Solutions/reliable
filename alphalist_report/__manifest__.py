# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "ALPHALIST OF PAYEES REPORT",
    'summary': 'Customized Report',
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
