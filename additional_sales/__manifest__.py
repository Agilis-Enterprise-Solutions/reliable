# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Sales Additional",
    'summary': 'Additinal Fields and Validations',
    'category': 'Sales',
    'author': 'Ralf Cabarogias',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'sale','stock',
        ],
    'data': [
        'views/sale_order.xml',

    ],
	'installable': True,
    'application': False,

}
