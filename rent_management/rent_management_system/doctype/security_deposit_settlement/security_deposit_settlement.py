# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class SecurityDepositSettlement(Document):
	def validate(self):
		if not self.tenant_space_allotment:
			return  # let the standard mandatory check report it

		self.validate_allotment()
		self.validate_duplicate()
		self.calculate_settlement()

	def validate_allotment(self):
		allotment = frappe.db.get_value(
			"Tenant Space Allotment",
			self.tenant_space_allotment,
			["docstatus", "status", "tenant", "room", "security_deposit", "deposit_collected", "vacate_date"],
			as_dict=True,
		)
		if allotment.docstatus != 1 or allotment.status != "Vacated":
			frappe.throw(_("The deposit can only be settled after the tenant has vacated the room."))

		if flt(allotment.security_deposit) <= 0:
			frappe.throw(_("Allotment {0} has no security deposit.").format(self.tenant_space_allotment))

		if not allotment.deposit_collected:
			frappe.throw(
				_("Mark the deposit as collected on Allotment {0} before settling it.").format(
					self.tenant_space_allotment
				)
			)

		draft_invoices = frappe.get_all(
			"Tenant Rent Invoice",
			filters={"tenant_space_allotment": self.tenant_space_allotment, "docstatus": 0},
			pluck="name",
		)
		if draft_invoices:
			frappe.throw(
				_("Submit or delete the draft Rent Invoices {0} before settling the deposit.").format(
					", ".join(draft_invoices)
				)
			)

		self.tenant = allotment.tenant
		self.room = allotment.room
		self.vacate_date = allotment.vacate_date
		self.security_deposit = allotment.security_deposit

	def validate_duplicate(self):
		existing = frappe.db.get_value(
			"Security Deposit Settlement",
			{
				"tenant_space_allotment": self.tenant_space_allotment,
				"docstatus": ("<", 2),
				"name": ("!=", self.name),
			},
		)
		if existing:
			frappe.throw(
				_("Deposit for this allotment is already settled in {0}.").format(
					frappe.get_desk_link("Security Deposit Settlement", existing, show_title_with_name=True)
				),
				frappe.DuplicateEntryError,
			)

	def calculate_settlement(self):
		self.outstanding_rent = sum(flt(d.outstanding_amount) for d in self.get_outstanding_invoices())
		self.total_deductions = sum(flt(d.amount) for d in self.deductions)

		available = flt(self.security_deposit) - self.total_deductions
		self.rent_adjusted = (
			min(self.outstanding_rent, max(available, 0)) if self.adjust_outstanding_rent else 0
		)
		self.refund_amount = max(available - self.rent_adjusted, 0)
		self.balance_payable_by_tenant = max(-available, 0) + self.outstanding_rent - self.rent_adjusted
		self.round_floats_in(
			self,
			[
				"outstanding_rent",
				"total_deductions",
				"rent_adjusted",
				"refund_amount",
				"balance_payable_by_tenant",
			],
		)

	@frappe.whitelist()
	def update_amounts(self):
		"""Recalculate the settlement while the form is being filled in."""
		self.validate_allotment()
		self.calculate_settlement()

	def get_outstanding_invoices(self):
		return frappe.get_all(
			"Tenant Rent Invoice",
			filters={
				"tenant_space_allotment": self.tenant_space_allotment,
				"docstatus": 1,
				"outstanding_amount": (">", 0),
			},
			fields=["name", "outstanding_amount"],
			order_by="from_date asc",
		)

	def on_submit(self):
		self.adjust_rent()
		frappe.db.set_value(
			"Tenant Space Allotment", self.tenant_space_allotment, "deposit_settlement", self.name
		)

	def on_cancel(self):
		# cancel the rent adjustments first so they don't block this cancellation
		for payment in frappe.get_all(
			"Rent Payment", filters={"deposit_settlement": self.name, "docstatus": 1}, pluck="name"
		):
			frappe.get_doc("Rent Payment", payment).cancel()
		frappe.db.set_value("Tenant Space Allotment", self.tenant_space_allotment, "deposit_settlement", None)

	def adjust_rent(self):
		"""Pay off outstanding invoices, oldest first, from the deposit."""
		remaining = flt(self.rent_adjusted)
		for invoice in self.get_outstanding_invoices():
			if remaining <= 0:
				break
			amount = min(remaining, flt(invoice.outstanding_amount))
			frappe.get_doc(
				{
					"doctype": "Rent Payment",
					"tenant": self.tenant,
					"rent_invoice": invoice.name,
					"payment_date": self.settlement_date,
					"mode_of_payment": "Security Deposit",
					"amount": amount,
					"deposit_settlement": self.name,
					"remarks": _("Adjusted from security deposit"),
				}
			).submit()
			remaining -= amount
