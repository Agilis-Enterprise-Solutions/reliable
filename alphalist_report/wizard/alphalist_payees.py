from odoo import fields, models
import logging
import re
from itertools import tee, islice, chain

_logger = logging.getLogger(__name__)


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

class AccountPrintAlphalistPayees(models.TransientModel):
    _name = "account.alphalist.payees"
    _description = "Account Print Alphalist of Payees"

    msg = fields.Char(default="ALPHALIST OF PAYEES SUBJECT TO EXPANDED W/HOLDING TAX")

    date_from = fields.Date("Start Date")
    date_to = fields.Date("End Date")


class alphalistxlsxreport(models.AbstractModel):
    _name = 'report.report_rl.alphalistxlsxreport'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, records):

        border = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'border': 1,
            'bold': True})
        content = workbook.add_format({
            'align': 'center',
            'text_wrap': True,
            'valign': 'vcenter'})
        bold = workbook.add_format({
            'align': 'center',
            'text_wrap': True,
            'valign': 'vcenter',
            'bold': True})
        left = workbook.add_format({
            'align': 'left',
            'text_wrap': True,
            'border': 1})

        bold.set_num_format('0.00')



        payee = workbook.add_worksheet("Alphalist of Payees")

        payee.set_column('A:A', 10)
        payee.set_column('B:B', 25)
        payee.set_column('C:C', 25)
        payee.set_column('D:D', 16)
        payee.set_column('E:E', 25)
        payee.set_column('F:F', 13)
        payee.set_column('G:G', 16)
        payee.set_column('H:H', 18)

        payee.merge_range('A2:C2', "ACCOUNTS PAYABLE SUPPLIER",left)
        payee.merge_range('A3:C3', "ALPHALIST OF PAYEES SUBJECT TO EXPANDED W/ HOLDING TAX",left)

        payee.write(6, 0, "SEQNO.",border)
        payee.write(6, 1, "TIN NO.",border)
        payee.write(6, 2, "NAME OF PAYEES",border)
        payee.write(6, 3, "ATC",border)
        payee.write(6, 4, "NATURE OF INCOME",border)
        payee.write(6, 5, "BASE AMT.",border)
        payee.write(6, 6, "(%)PERCENTAGE",border)
        payee.write(6, 7, "AMT.W/HELD",border)

        row = 7
        column = 0

        sequence_list = []
        vendor_name = []
        total_base_tax = 0
        total_amount_tax = 0
        grand_base_tax = 0
        grand_amount_tax = 0
        noi_total_tax_dict = {}
        noi_total_tax_list = []

        for rec in records:
            context_id = rec._context
            current_uid= context_id.get('uid')
            company = rec.env['res.users'].browse(current_uid)
            payee.merge_range('A1:C1', company.company_id.name,left)
            date_from = "From: " + str(rec.date_from)
            date_to = "To: " + str(rec.date_to)
            payee.write(3, 1, date_from, left)
            payee.write(3, 2, date_to, left)

            invoices_tax = rec.env['account.invoice.tax'].search([])

            for ven in invoices_tax:
                if ven.invoice_id.state not in ('draft','cancel'):
                    vendor_name.append(ven.invoice_id.partner_id.name)
            vendor_name = list(dict.fromkeys(vendor_name))

            alpha_dict = {seq: [] for seq in vendor_name}
            for seq in vendor_name:
                for tax in invoices_tax:
                    if seq == tax.invoice_id.partner_id.name and (tax.invoice_id.state not in ('draft','cancel')):
                        if (tax.invoice_id.date_invoice >= rec.date_from
                            and tax.invoice_id.date_invoice <= rec.date_to and tax.invoice_id.origin == False
                            and tax.nature_of_income != False):
                            alpha_dict[seq].append([tax.seq_no,
                                                    tax.invoice_id.partner_id.vat,
                                                    tax.invoice_id.partner_id.name,
                                                    tax.name,
                                                    tax.nature_of_income,
                                                    tax.base,
                                                    abs(tax.percentage),
                                                    tax.amount_total
                                                     ])
                            refund = self.env['account.invoice'].search([
                                ('origin','=',tax.invoice_id.number),
                                ('origin','!=',False)])
                            if refund:
                                if (refund.origin == tax.invoice_id.number and
                                    refund.partner_id.name == tax.invoice_id.partner_id.name):
                                    alpha_dict[seq].append([tax.seq_no,
                                                            tax.invoice_id.partner_id.vat,
                                                            tax.invoice_id.partner_id.name,
                                                            tax.name,
                                                            tax.nature_of_income,
                                                            '('+str(tax.base)+')',
                                                            abs(tax.percentage),
                                                            tax.amount_total
                                                             ])
            alpha_dict={key:value for key,value in alpha_dict.items() if value}
            alpha_list = [value for value in alpha_dict.values() if value]
            alpha_list_new = []
            for l in alpha_list:
                for x in l:
                    alpha_list_new.append(x)
            for past,present,future in previous_and_next(alpha_list_new):
                payee.write_row(row, column, present, content)
                if isinstance(present[5],str):
                    total_base_tax = total_base_tax - past[5]
                    grand_base_tax = grand_base_tax - past[5]
                else:
                    total_base_tax += present[5]
                    grand_base_tax += present[5]
                total_amount_tax += present[7]
                grand_amount_tax += present[7]
                row+=1
                try:
                    if present[2] != future[2]:
                        payee.write(row, 1, "PERCENT TOTAL", bold)
                        payee.write(row, 5, total_base_tax, bold)
                        payee.write(row, 7, total_amount_tax, bold)
                        total_base_tax = 0
                        total_amount_tax = 0
                        row+=1
                except TypeError:
                    payee.write(row, 1, "PERCENT TOTAL", bold)
                    payee.write(row, 5, total_base_tax, bold)
                    payee.write(row, 7, total_amount_tax, bold)
                    payee.write(row + 1, 1, "GRAND TOTAL", bold)
                    payee.write(row + 1, 2, "--------->", bold)
                    payee.write(row + 1, 5, grand_base_tax, bold)
                    payee.write(row + 1, 7, grand_amount_tax, bold)
                    payee.write(row + 4, 0, "SUMMARY:", bold)
                    payee.write(row + 5, 1, "ATC#", bold)
                    payee.write(row + 5, 2, "NATURE", bold)
                    payee.write(row + 5, 3, "BASE AMOUNT", bold)
                    payee.write(row + 5, 4, "%", bold)
                    payee.write(row + 5, 5, "AMOUNT", bold)
                    new_row = row + 6
            sequence_tax = rec.env['account.tax'].search([])
            for sequence in sequence_tax:
                if sequence.seq_no:
                    sequence_list.append(sequence.seq_no)

            alphalist_dict = {seq: [] for seq in sequence_list}
            for sequence in sequence_list:
                for tax in invoices_tax:
                    if sequence == tax.seq_no and (tax.invoice_id.state not in ('draft','cancel')):
                        if (tax.invoice_id.date_invoice >= rec.date_from
                            and tax.invoice_id.date_invoice <= rec.date_to and tax.invoice_id.origin == False):
                            alphalist_dict[sequence].append([tax.seq_no,
                                                             tax.invoice_id.partner_id.vat,
                                                             tax.invoice_id.partner_id.name,
                                                             tax.name,
                                                             tax.nature_of_income,
                                                             tax.base,
                                                             abs(tax.percentage),
                                                             tax.amount_total
                                                             ])
                            refund = self.env['account.invoice'].search([
                                ('origin','=',tax.invoice_id.number),
                                ('origin','!=',False)])
                            if refund:
                                if (refund.origin == tax.invoice_id.number and
                                    refund.partner_id.name == tax.invoice_id.partner_id.name):
                                    alphalist_dict[sequence].append([tax.seq_no,
                                                                     tax.invoice_id.partner_id.vat,
                                                                     tax.invoice_id.partner_id.name,
                                                                     tax.name,
                                                                     tax.nature_of_income,
                                                                     '('+str(tax.base)+')',
                                                                     abs(tax.percentage),
                                                                     tax.amount_total
                                                                     ])
            alphalist_dict={key:value for key,value in alphalist_dict.items() if value}
            alphalist = [value for value in alphalist_dict.values() if value]
            alphalist_new = []
            for l in alphalist:
                for x in l:
                    alphalist_new.append(x)

            total_base_tax_summary = 0
            total_amount_tax_summary = 0
            for past,present,future in previous_and_next(alphalist_new):
                if isinstance(present[5],str):
                    total_base_tax_summary = total_base_tax_summary - past[5]
                    total_amount_tax_summary = total_amount_tax_summary - past[7]
                else:
                    total_base_tax_summary += present[5]
                    total_amount_tax_summary += present[7]
                row+=1
                try:
                    if present[0] != future[0]:
                        noi_total_tax_dict[present[4]] = [total_base_tax_summary,
                                                          total_amount_tax_summary]
                        total_base_tax_summary = 0
                        total_amount_tax_summary = 0
                        row+=1
                except TypeError:
                    noi_total_tax_dict[present[4]] = [total_base_tax_summary,
                                                      total_amount_tax_summary]

                    sequence = rec.env['account.tax'].search([])

                    sequence_dict_summary = {}
                    sequence_list_summary = []
                    for seq in sequence:
                        if seq.seq_no:
                            sequence_dict_summary[seq.name] = [seq.nature_of_income,
                                                               abs(seq.amount)]

                    for key,value in sequence_dict_summary.items():
                        temp = [key,value]
                        sequence_list_summary.append(temp)

                    for key,value in noi_total_tax_dict.items():
                        temp = [key,value]
                        noi_total_tax_list.append(temp)

                    int_count = 1
                    for x in sequence_list_summary:
                        for total in noi_total_tax_list:
                            if x[int_count][0] == total[0]:
                                payee.write(new_row, 1, x[0], content)
                                payee.write(new_row, 2, x[int_count][0], content)
                                payee.write(new_row, 3, total[int_count][0], bold)
                                payee.write(new_row, 4, x[int_count][1], content)
                                payee.write(new_row, 5, total[int_count][1], bold)
                                new_row += 1
