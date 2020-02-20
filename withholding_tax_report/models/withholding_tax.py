from odoo import fields, models, api
from datetime import date
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountPrintWithholdingTax(models.TransientModel):
    _name = "account.withholding.tax"
    _description = "Print Withholding Tax"


    name = fields.Char("Ref", readonly=True)
    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    partner_id = fields.Many2one('res.partner',"Payee's Name", required=True)
    representative_id = fields.Many2one('hr.employee',
                                        "Authorized Representative",
                                        required=True)
    invoice_id = fields.Many2one('account.invoice', "Invoice", required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('generate', 'Generated'),
    ], string="Status", default="draft", readonly=True, copy=False)

    withholding_ids = fields.One2many('account.withholding.tax.lines','withholding_id')

    @api.onchange('invoice_id')
    def _duplicate_invoice(self):
        if self.invoice_id:
            duplicate = self.search([('invoice_id', '=', self.invoice_id.id),
                                     ('id', '!=', self._origin.id),
                                     ('state', '=', 'generate')])
            if duplicate:
                return {
                    'warning': {
                        'title': "Duplicate Entry",
                        'message': """This Invoice had been already Generated.
                        Please Check the other records for Reference"""
                    }
                }

    @api.model
    def create(self, vals):
        vals['date'] = date.today()
        vals['name'] = self.env['ir.sequence'].get('account.withholding.tax')
        return super(AccountPrintWithholdingTax, self).create(vals)

    @api.multi
    def generate_withholding_tax(self):
        for i in self.withholding_ids:
            i.unlink()

        duplicate = self.search([('invoice_id', '=', self.invoice_id.id),
                                 ('id', '!=', self.id),
                                 ('state', '=', 'generate')])
        if duplicate:
            raise UserError('''This Invoice had been already Generated.
            Please Check the other records for Reference''')

        data = []
        branch_code = ""
        for i in self:
            if i.partner_id.vat:
                branch_code = str(i.partner_id.vat[-3:])
            address = '%s %s %s'%(i.partner_id.street, i.partner_id.street2, i.partner_id.city)
            val= {
                'date' : date.today(),
                'vendor_tin' : i.partner_id.vat,
                'branch_code' : branch_code,
                'company_name' : i.partner_id.name,
                'address' : address,
                'tax_id' : [tax.name for tax in i.invoice_id.tax_line_ids][0],
                'base_amount' : [tax.base for tax in i.invoice_id.tax_line_ids][0],
                'ewt_rate' : [tax.percentage for tax in i.invoice_id.tax_line_ids][0],
                'tax_amount': [tax.amount_total for tax in i.invoice_id.tax_line_ids][0]
                }
            data.append([0, 0, val])

        return self.write({'withholding_ids': data,
                           'state': 'generate'})


class AccountPrintWithholdingTaxLines(models.TransientModel):
    _name = "account.withholding.tax.lines"
    _description = "Withholding Tax Lines"

    withholding_id = fields.Many2one('account.withholding.tax')
    date = fields.Date('Reporting Month')
    vendor_tin = fields.Char('Vendor TIN')
    branch_code = fields.Char('Branch Code')
    company_name = fields.Char('Company Name')
    address = fields.Text('Address')
    tax_id = fields.Char('ATC')
    base_amount = fields.Char('Base Amount')
    ewt_rate = fields.Char('EWT Rate')
    tax_amount = fields.Char('Tax Amount')
