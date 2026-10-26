# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt


class RentPayment(Document):
	def validate(self):
		if not self.rent_invoice:
			return  # let the standard mandatory check report it

		invoice = frappe.db.get_value(
			"Tenant Rent Invoice",
			self.rent_invoice,
			["docstatus", "tenant", "outstanding_amount"],
			as_dict=True,
		)
		if invoice.docstatus != 1:
			frappe.throw(
				_("Rent Invoice {0} must be submitted before recording a payment.").format(self.rent_invoice)
			)

		# Tenant is autoincrement-named, so the link value may be an int or a str
		if cstr(invoice.tenant) != cstr(self.tenant):
			frappe.throw(
				_("Rent Invoice {0} does not belong to Tenant {1}.").format(self.rent_invoice, self.tenant)
			)

		if flt(self.amount) <= 0:
			frappe.throw(_("Amount must be greater than zero."))

		if flt(self.amount) > flt(invoice.outstanding_amount):
			frappe.throw(
				_("Amount {0} is more than the outstanding amount {1} of Rent Invoice {2}.").format(
					frappe.format_value(self.amount, {"fieldtype": "Currency"}),
					frappe.format_value(invoice.outstanding_amount, {"fieldtype": "Currency"}),
					self.rent_invoice,
				)
			)

	def on_submit(self):
		self.update_invoice()

	def on_cancel(self):
		self.update_invoice()

	def update_invoice(self):
		frappe.get_doc("Tenant Rent Invoice", self.rent_invoice).update_paid_amount()
