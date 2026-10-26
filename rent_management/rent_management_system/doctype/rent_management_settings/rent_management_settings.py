# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from rent_management.rent_management_system.billing import generate_invoices


class RentManagementSettings(Document):
	def validate(self):
		if self.rent_due_day and self.rent_due_day > 31:
			frappe.throw(_("Rent Due Day of Month must be between 1 and 31."))


@frappe.whitelist()
def generate_invoices_now(billing_month: str, billing_year: int, submit: bool = False):
	frappe.only_for("System Manager")
	created = generate_invoices(billing_month, billing_year, submit=frappe.utils.cint(submit))
	frappe.msgprint(
		_("{0} Rent Invoice(s) created for {1} {2}.").format(len(created), billing_month, billing_year)
	)
	return created
