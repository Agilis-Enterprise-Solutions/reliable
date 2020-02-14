# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class InheritAccountInvoiceValue(models.Model):
    _inherit="account.invoice"

    dr_no = fields.Char(string="DR No.")
