from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class InheritAccountTax(models.Model):
    _inherit='account.tax'

    nature_of_income = fields.Char(string="Nature of Income")
    seq_no = fields.Integer(string="SEQNO.")

class InheritAccountInvoiceTax(models.Model):
    _inherit='account.invoice.tax'

    nature_of_income = fields.Char(string="Nature of Income",compute="_compute_noi_seq")
    seq_no = fields.Integer(string="SEQNO.",compute="_compute_noi_seq")
    percentage = fields.Integer(string="Perc",compute="_compute_noi_seq")


    @api.depends("name")
    def _compute_noi_seq(self):
        for rec in self:
            tax_id = rec.env['account.tax'].search([('name','=',rec.name)])
            for i in tax_id:
                rec.nature_of_income = i.nature_of_income
                rec.seq_no = i.seq_no
                rec.percentage = i.amount
