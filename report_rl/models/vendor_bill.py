from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class APV(models.Model):
    _inherit='account.invoice'

    requested_by = fields.Char(string="Prepared By", default="Ms. Ada")
    approved_by = fields.Char(string="Approved By", default="Mae Ramos")
    checked_by = fields.Char(string="Checked By", default="BAVjr/BTN")
