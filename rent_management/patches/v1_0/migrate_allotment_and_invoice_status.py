import frappe
from frappe.utils import flt

from rent_management.rent_management_system.doctype.tenant_rent_invoice.tenant_rent_invoice import get_status


def execute():
	"""Map old allotment statuses (Alloted / Ready to Allot) and fill invoice payment fields."""
	allotment = frappe.qb.DocType("Tenant Space Allotment")
	for docstatus, status in ((0, "Draft"), (1, "Active"), (2, "Cancelled")):
		(
			frappe.qb.update(allotment)
			.set(allotment.status, status)
			.where(allotment.docstatus == docstatus)
			.where(allotment.status.isnull() | allotment.status.isin(["", "Alloted", "Ready to Allot"]))
		).run()

	for room in frappe.get_all(
		"Tenant Space", filters={"status": "Occupied", "current_allotment": ("is", "not set")}, pluck="name"
	):
		active = frappe.db.get_value(
			"Tenant Space Allotment",
			{"room": room, "docstatus": 1, "status": "Active"},
			order_by="allotment_date desc",
		)
		if active:
			frappe.db.set_value("Tenant Space", room, "current_allotment", active, update_modified=False)

	for invoice in frappe.get_all(
		"Tenant Rent Invoice",
		fields=["name", "docstatus", "final_amount", "paid_amount", "due_date"],
	):
		invoice.outstanding_amount = flt(invoice.final_amount) - flt(invoice.paid_amount)
		frappe.db.set_value(
			"Tenant Rent Invoice",
			invoice.name,
			{
				"paid_amount": flt(invoice.paid_amount),
				"outstanding_amount": invoice.outstanding_amount,
				"status": get_status(invoice),
			},
			update_modified=False,
		)
