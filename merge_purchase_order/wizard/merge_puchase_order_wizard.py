# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError
import logging

_logger = logging.getLogger(__name__)


class MergePurchaseOrder(models.TransientModel):
    _name = "merge.purchase.order"

    merge_type = fields.Selection(
        [
            ("new_cancel", "Create new order and cancel all selected purchase orders"),
            ("new_delete", "Create new order and delete all selected purchase orders"),
            (
                "merge_cancel",
                "Merge order on existing selected order and cancel others",
            ),
            (
                "merge_delete",
                "Merge order on existing selected order and delete others",
            ),
        ],
        default="new_cancel",
    )

    purchase_order_id = fields.Many2one("purchase.order", "Purchase Order")

    @api.onchange("merge_type")
    def onchange_merge_type(self):
        res = {}
        for order in self:
            order.purchase_order_id = False
            if order.merge_type in ["merge_cancel", "merge_delete"]:
                purchase_orders = self.env["purchase.order"].browse(
                    self._context.get("active_ids", [])
                )
                res["domain"] = {
                    "purchase_order_id": [
                        ("id", "in", [purchase.id for purchase in purchase_orders])
                    ]
                }
            return res

    def process_po(
        self,
        purchase_orders,
        partner,
        create_new_po=False,
        cancel_po=False,
        sudo_cancel_po=False,
        sudo_cancel_rfq=False,
        sudo_delete_rfq=False,
    ):

        if create_new_po:
            po = (
                self.env["purchase.order"]
                .with_context(
                    {"trigger_onchange": True, "onchange_fields_to_trigger": [partner]}
                )
                .create({"partner_id": partner})
            )
            default = {"order_id": po.id}
        else:
            po = self.purchase_order_id
            default = {"order_id": self.purchase_order_id.id} 
        
        existing_po_line = False

        for order in purchase_orders:
            if order == po:
                if sudo_cancel_rfq or sudo_delete_rfq:
                    continue
            for line in order.order_line:
                if po.order_line:
                    for po_line in po.order_line:
                        if (
                            line.product_id == po_line.product_id
                            and line.price_unit == po_line.price_unit
                        ):
                            existing_po_line = po_line
                            break
                            
                # # attach any products attachments
                att_ids = self.env["ir.attachment"].search([('res_id', '=', order.id)])
                    
                for att in att_ids:
                    self.env["ir.attachment"].search([('id', '=', att.id)]).write(
                        {
                            "res_name": po.name,
                            "res_id": po.id,
                            "res_model": "purchase.order",
                        }
                    )    
                    
                if existing_po_line:
                    existing_po_line.product_qty += line.product_qty
                    po_taxes = [tax.id for tax in existing_po_line.taxes_id]
                    [po_taxes.append((tax.id)) for tax in line.taxes_id]
                    existing_po_line.taxes_id = [(6, 0, po_taxes)]
                else:
                    line.copy(default=default)

        for order in purchase_orders:
            # for PO's
            if cancel_po:
                order.button_cancel()
            if sudo_cancel_po:
                order.sudo().button_cancel()
                order.sudo().unlink()
            # For RFQ's
            if sudo_cancel_rfq:
                if order != po:
                    order.sudo().button_cancel()
            if sudo_delete_rfq:
                if order != po:
                    order.sudo().button_cancel()
                    order.sudo().unlink()

    @api.multi
    def merge_orders(self):

        purchase_orders = self.env["purchase.order"].browse(
            self._context.get("active_ids", [])
        )

        partner = purchase_orders[0].partner_id.id

        if len(self._context.get("active_ids", [])) < 2:
            raise UserError(
                _(
                    "Please select atleast two purchase orders to perform "
                    "the Merge Operation."
                )
            )
        if any(order.state != "draft" for order in purchase_orders):
            raise UserError(
                _(
                    "Please select Purchase orders which are in RFQ state "
                    "to perform the Merge Operation."
                )
            )

        if any(order.partner_id.id != partner for order in purchase_orders):
            raise UserError(
                _(
                    "Please select Purchase orders whose Vendors are same to "
                    " perform the Merge Operation."
                )
            )

        if self.merge_type == "new_cancel":         
            self.process_po(
                purchase_orders,
                partner,
                create_new_po=True,
                cancel_po=True,
            )

        elif self.merge_type == "new_delete":
            self.process_po(
                purchase_orders,
                partner,
                create_new_po=True,
                cancel_po=True,
            )

        elif self.merge_type == "merge_cancel":
            self.process_po(
                purchase_orders,     
                partner,      
                sudo_cancel_rfq=True,
            )

        else:
            self.process_po(
                purchase_orders,
                partner,               
                sudo_delete_rfq=True,
            )
