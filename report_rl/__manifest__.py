# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Customization Report",
    'summary': 'APV Report',
    'category': 'Accounting',
    'author': 'Ralf Cabarogias',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'base','account_accountant'
        ],
    'data': [
        'report/apv.xml',
        'views/vendor_bills.xml',

    ],
	'installable': True,
    'application': False,

}
