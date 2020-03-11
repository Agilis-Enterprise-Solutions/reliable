from odoo import fields, models, api
from datetime import date
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountPrintWithholdingTax(models.Model):
    _name = "account.withholding.tax"
    _description = "Print Withholding Tax"


    name = fields.Char("Ref", readonly=True, store=True)
    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    partner_id = fields.Many2one('res.partner',
                                  string="Payees Name", required=True)
    representative_id = fields.Many2one('hr.employee',
                                        "Authorized Representative",
                                        required=True)
    invoice_id = fields.Many2many('account.invoice',
                                  string="Invoice", required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('generate', 'Generated'),
    ], string="Status", default="draft", readonly=True, copy=False)

    withholding_ids = fields.One2many('account.withholding.tax.lines','withholding_id_line',
                                      store=True)

    @api.model
    def create(self, vals):
        vals['date'] = date.today()
        vals['name'] = self.env['ir.sequence'].get('account.withholding.tax')
        return super(AccountPrintWithholdingTax, self).create(vals)

    @api.multi
    def generate_withholding_tax(self):
        for i in self.withholding_ids:
            i.unlink()

        for i in self:
            for invoice in i.invoice_id:
                _logger.info("\n\n\nValue %s\n\n\n"%(invoice.refund))

        # data = []
        # branch_code = ""
        # for i in self:
        #     for invoice in i.invoice_id:
        #         duplicate = self.search([('invoice_id', '=', invoice.id),
        #                                  ('id', '!=', self.id),
        #                                  ('state', '=', 'generate')])
        #         if duplicate:
        #             raise UserError('''This Invoice had been already Generated.
        #             Please Check the other records for Reference''')
        #
        #         for x in invoice.tax_line_ids:
        #             if i.partner_id.vat:
        #                 branch_code = str(i.partner_id.vat[-3:])
        #             address = '%s %s %s'%(i.partner_id.street if i.partner_id.street else "",
        #                                   i.partner_id.street2 if i.partner_id.street2 else "",
        #                                   i.partner_id.city if i.partner_id.city else "")
        #
        #             tax_id = self.env['account.tax'].search([('name','=',x.name),
        #                                                      ('nature_of_income','!=',False)])
        #             if tax_id:
        #                 val= {
        #                     'date' : date.today(),
        #                     'vendor_tin' : invoice.partner_id.vat,
        #                     'branch_code' : branch_code,
        #                     'company_name' : i.partner_id.name,
        #                     'address' : address,
        #                     'tax_id' : tax_id.id,
        #                     'base_amount' : x.base,
        #                     'ewt_rate' : abs(x.percentage),
        #                     'tax_amount': x.amount_total
        #                     }
        #                 data.append([0, 0, val])
        #
        # return self.write({'withholding_ids': data,
        #                    'state': 'generate'})


class AccountPrintWithholdingTaxLines(models.Model):
    _name = "account.withholding.tax.lines"
    _description = "Withholding Tax Lines"

    withholding_id_line = fields.Many2one('account.withholding.tax')
    date = fields.Date('Reporting Month')
    vendor_tin = fields.Char('Vendor TIN')
    branch_code = fields.Char('Branch Code')
    company_name = fields.Char('Company Name')
    address = fields.Text('Address')
    tax_id = fields.Many2one('account.tax','ATC', store=True)
    base_amount = fields.Char('Base Amount')
    ewt_rate = fields.Char('EWT Rate')
    tax_amount = fields.Char('Tax Amount')
