
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger("_name_")


class InheritSaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):

        res = super(InheritSaleAdvancePaymentInv, self).create_invoices()
        sale =  self.env['sale.order'].browse(self._context.get('active_id'))
        stock = self.env['stock.picking'].search([
            ('origin','=',sale.name),
            ('picking_type_code','=','outgoing'),
            ('state','=','done')])[0]
        invoice = self.env['account.invoice'].search([
            ('origin','=',sale.name),
            ('type','=','out_invoice')])[0]
        
        invoice.write({
            'dr_no' :  stock.dr_no
        })
        return res
