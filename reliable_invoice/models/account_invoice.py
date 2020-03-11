# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class InheritAccountInvoiceValue(models.Model):
    _inherit="account.invoice"

    dr_no = fields.Char(string="DR No.")
    prepared_by = fields.Char(string="Prepared By")
    checked_by = fields.Char(string="Checked By")
    refund_bool = fields.Boolean(compute='_compute_refund_bool', string='Refund', store=True)

    @api.multi
    @api.depends("number")
    def _compute_refund_bool(self):
        for s in self:
            refund = self.search([('origin', '=', s.number)])
            if refund:
                s.refund_bool = True


class AccountPaymentOfficialReceipt(models.Model):
    _inherit="account.payment"

    official_receipt_no = fields.Char(string="Official Receipt No.")

class OfficialReceiptGroup(models.TransientModel):
    _inherit = "account.register.payments"

    official_receipt_no = fields.Char(string="Official Receipt No.")

    @api.multi
    def create_payments(self):
        res = super(OfficialReceiptGroup, self).create_payments()
        payment = self.env['account.payment'].search([])
        for k,v in res.items():
            if k == "res_id":
                for rec in payment:
                    if rec.id == v:
                        rec.write({
                            'official_receipt_no': self.official_receipt_no
                        })
        return res
