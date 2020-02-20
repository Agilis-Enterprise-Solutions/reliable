# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "WITHHOLDING TAX REPORT",
    'summary': 'Customized Report',
    'category': 'Accounting',
    'author': 'Ralf Cabarogias',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'base','account_accountant','account','alphalist_report'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/withholding_tax.xml',

    ],
	'installable': True,
    'application': False,

}
