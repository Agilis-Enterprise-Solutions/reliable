from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class InheritSaleOrder(models.Model):
    _inherit='sale.order'

    @api.multi
    def action_confirm(self):
        res = super(InheritSaleOrder, self).action_confirm()
        stock = self.env['stock.picking'].search([('origin', '=', self.name)])
        for rec in stock:
            rec.write({
                'client_order_ref': self.client_order_ref,
            })
        return res

    @api.onchange("client_order_ref")
    def client_ref_duplicate(self):
        if self.client_order_ref:
            client_order = self.search([('client_order_ref', '=', self.client_order_ref),
                                     ('id','!=',self._origin.id)])
            _logger.info("\n\n\nPOTA %s\n\n\n"%(client_order))
            if client_order:
                return {
                    'warning': {
                        'title': "Duplicate Entry",
                        'message': "Client Order Reference has a Duplicate. Please Check the other Sale Order for Reference"
                    }
                }

    @api.model
    def create(self, vals):
        res = super(InheritSaleOrder, self).create(vals)
        for i in res:
            client_order = i.search([('client_order_ref', '=', i.client_order_ref),
                                     ('id','!=',i.id)])
            if client_order:
                raise UserError("Client Order Reference has a Duplicate. Please Check the other Sale Order for Reference")
        return res

class InheritStockPicking(models.Model):
    _inherit='stock.picking'

    client_order_ref = fields.Char("Customer Reference")
    dr_no = fields.Char("DR No.")
    dr_duplicate = fields.Boolean("Checker", default=False)
    check_out_by = fields.Char("Check out By")
    countersigned_by = fields.Char("Countersigned By")
    delivered_by = fields.Char("Delivered By")
    truck_no = fields.Char("Truck No.")
    job_no = fields.Char("Job No.")

    @api.model
    def create(self, vals):
        res = super(InheritStockPicking, self).create(vals)
        res.dr_no = False
        return res
    @api.onchange("dr_no")
    def _check_dr_duplicate(self):
        if self.dr_no:
            duplicate = self.search([('dr_no', '=', self.dr_no),
                                     ('id', '!=', self._context.get('active_id'))])
            if duplicate:
                self.dr_duplicate = True
                return {
                    'warning': {
                        'title': "Duplicate Entry",
                        'message': "Dr No. Has a Duplicate. Please Check the other Dr No for Reference"
                    }
                }
            else:
                self.dr_duplicate = False

    @api.constrains('dr_duplicate')
    def check_duplicate_true(self):
        if self.dr_duplicate:
            raise UserError("Dr No. Has a Duplicate. Please Check the other Dr No for Reference")
