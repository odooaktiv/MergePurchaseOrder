# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class MergePurchaseOrder(models.TransientModel):
    _name = 'merge.purchase.order'

    merge_type = \
        fields.Selection([
            ('new_cancel',
             'Create new order and cancel all selected purchase orders'),
            ('new_delete',
             'Create new order and delete all selected purchase orders'),
            ('merge_cancel',
             'Merge order on existing selected order and cancel others'),
            ('merge_delete',
             'Merge order on existing selected order and delete others')],
            default='new_cancel')
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')

    @api.onchange('merge_type')
    def onchange_merge_type(self):
        res = {}
        for order in self:
            order.purchase_order_id = False
            if order.merge_type in ['merge_cancel', 'merge_delete']:
                purchase_orders = self.env['purchase.order'].browse(
                    self._context.get('active_ids', []))
                res['domain'] = {
                    'purchase_order_id':
                        [('id', 'in',
                          [purchase.id for purchase in purchase_orders])]
                }
            return res

    @api.multi
    def merge_orders(self):
        purchase_orders = self.env['purchase.order'].browse(
            self._context.get('active_ids', []))
        # existing_po_line = False
        if len(self._context.get('active_ids', [])) < 2:
            raise UserError(
                _('Please select atleast two purchase orders to perform '
                  'the Merge Operation.'))
        if any(order.state != 'draft' for order in purchase_orders):
            raise UserError(
                _('Please select Purchase orders which are in RFQ state '
                  'to perform the Merge Operation.'))
        partner = purchase_orders[0].partner_id.id
        if any(order.partner_id.id != partner for order in purchase_orders):
            raise UserError(
                _('Please select Purchase orders whose Vendors are same to '
                  ' perform the Merge Operation.'))
        # Update lines depending on the merge_type
        if self.merge_type == 'new_cancel' or self.merge_type == 'new_delete':
            po = self.env['purchase.order'].with_context({
                'trigger_onchange': True,
                'onchange_fields_to_trigger': [partner]
            }).create({'partner_id': partner})
            default = {'order_id': po.id}
        # 'merge_cancel': or other cases
        else:
            po = self.purchase_order_id
            default = {'order_id': self.purchase_order_id.id}

        existing_po_line = False
        for order in purchase_orders:
            if order == po and self.merge_type != 'new_cancel' and self.merge_type != 'new_delete':
                continue
            for line in order.order_line:
                # Debug
                msg = "MERGE_PURCHASE_ORDER ID: {} po.order_line: {} existing_po_line: {} {} {}".format(line.product_id,
                                                                                                        line.name,
                                                                                                        po.order_line,
                                                                                                        existing_po_line,
                                                                                                        order)
                _logger.info(msg)
                if po.order_line:
                    for poline in po.order_line:
                        if line.product_id == poline.product_id and line.price_unit == poline.price_unit:
                            existing_po_line = poline
                            break
                if existing_po_line:
                    # print the line that are merged following upstream version. (debugging purpose)
                    # Try: FIX issue https://github.com/odooaktiv/MergePurchaseOrder/issues/2 ?
                    msg = "Merge product existing line ID {} Product Name {}".format(existing_po_line.product_id,
                                                                                     existing_po_line.name)
                    _logger.debug(msg)
                    msg = "product line ID {} name {}".format(line.product_id, line.name)
                    _logger.debug(msg)
                    if line.product_id == existing_po_line.product_id:
                        # Merge only identical lines
                        existing_po_line.product_qty += line.product_qty
                        po_taxes = [tax.id for tax in existing_po_line.taxes_id]
                        # Fixme needs to be in [] ?
                        [po_taxes.append(tax.id) for tax in line.taxes_id]
                        existing_po_line.taxes_id = [(6, 0, po_taxes)]
                    else:
                        # prevent the bug case to forget the line
                        line.copy(default=default)
                else:
                    line.copy(default=default)
        for order in purchase_orders:
            if self.merge_type == 'new_cancel':
                order.button_cancel()
            if self.merge_type == 'new_delete':
                order.sudo().button_cancel()
                order.sudo().unlink()
            if self.merge_type == 'merge_cancel':
                order.sudo().button_cancel()
            if self.merge_type == 'merge_delete':
                order.sudo().button_cancel()
                order.sudo().unlink()
