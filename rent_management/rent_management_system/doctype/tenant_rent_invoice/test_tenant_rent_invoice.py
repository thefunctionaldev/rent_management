# Copyright (c) 2026, Shashank Dixit and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from rent_management.rent_management_system.doctype.tenant_space_allotment.test_tenant_space_allotment import (
	make_allotment,
	make_room,
)

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


def make_invoice(allotment, billing_month="January", billing_year=2026, submit=False, **kwargs):
	invoice = frappe.get_doc(
		{
			"doctype": "Tenant Rent Invoice",
			"tenant_space_allotment": allotment.name,
			"billing_month": billing_month,
			"billing_year": billing_year,
			"posting_date": kwargs.pop("posting_date", "2026-01-01"),
			**kwargs,
		}
	).insert()
	if submit:
		invoice.submit()
	return invoice


class IntegrationTestTenantRentInvoice(IntegrationTestCase):
	def test_full_month(self):
		allotment = make_allotment(room=make_room(rent=3000), allotment_date="2025-12-20")
		invoice = make_invoice(allotment)
		self.assertEqual(str(invoice.tenant), str(allotment.tenant))
		self.assertEqual(invoice.room, allotment.room)
		self.assertEqual(invoice.total_days, 31)
		self.assertEqual(invoice.days_stayed, 31)
		self.assertEqual(invoice.pro_rated_rent, 3000)
		self.assertEqual(invoice.final_amount, 3000)
		self.assertEqual(invoice.status, "Draft")

	def test_first_month_is_pro_rated(self):
		allotment = make_allotment(room=make_room(rent=3100), allotment_date="2026-03-15")
		invoice = make_invoice(allotment, "March", posting_date="2026-03-15")
		self.assertEqual(str(invoice.from_date), "2026-03-15")
		self.assertEqual(invoice.days_stayed, 17)
		self.assertEqual(invoice.pro_rated_rent, 1700)

	def test_later_month_is_billed_in_full(self):
		# previously every month was pro-rated from the allotment date
		allotment = make_allotment(room=make_room(rent=3100), allotment_date="2026-03-15")
		invoice = make_invoice(allotment, "May", posting_date="2026-05-01")
		self.assertEqual(invoice.days_stayed, 31)
		self.assertEqual(invoice.pro_rated_rent, 3100)

	def test_vacate_month_is_pro_rated(self):
		allotment = make_allotment(room=make_room(rent=3000), allotment_date="2026-01-01")
		allotment.vacate("2026-04-10")
		invoice = make_invoice(allotment, "April", posting_date="2026-04-10")
		self.assertEqual(str(invoice.to_date), "2026-04-10")
		self.assertEqual(invoice.days_stayed, 10)
		self.assertEqual(invoice.pro_rated_rent, 1000)

		self.assertRaises(frappe.ValidationError, make_invoice, allotment, "May")

	def test_month_before_allotment(self):
		allotment = make_allotment(allotment_date="2026-03-15")
		self.assertRaises(frappe.ValidationError, make_invoice, allotment, "February")

	def test_charges_and_discount(self):
		allotment = make_allotment(room=make_room(rent=3000))
		invoice = make_invoice(
			allotment,
			charges=[
				{"charge_type": "Electricity", "amount": 450},
				{"charge_type": "Water", "amount": 150},
			],
			discount_amount=100,
		)
		self.assertEqual(invoice.total_charges, 600)
		self.assertEqual(invoice.final_amount, 3500)
		self.assertEqual(invoice.outstanding_amount, 3500)

	def test_missing_mandatory_fields(self):
		invoice = frappe.get_doc({"doctype": "Tenant Rent Invoice", "billing_month": "January"})
		self.assertRaises(frappe.MandatoryError, invoice.insert)

	def test_duplicate_invoice(self):
		allotment = make_allotment()
		make_invoice(allotment)
		self.assertRaises(frappe.DuplicateEntryError, make_invoice, allotment)

	def test_due_date_from_settings(self):
		frappe.db.set_single_value("Rent Management Settings", "rent_due_day", 7)
		allotment = make_allotment()
		invoice = make_invoice(allotment)
		self.assertEqual(str(invoice.due_date), "2026-01-07")

		# never before the posting date
		invoice = make_invoice(allotment, "February", posting_date="2026-02-10")
		self.assertEqual(str(invoice.due_date), "2026-02-10")

	def test_submit_sets_status(self):
		allotment = make_allotment()
		invoice = make_invoice(allotment, due_date=frappe.utils.add_days(frappe.utils.nowdate(), 30))
		invoice.submit()
		self.assertEqual(invoice.status, "Unpaid")

		overdue = make_invoice(allotment, "February", posting_date="2026-02-01", due_date="2026-02-05")
		overdue.submit()
		self.assertEqual(overdue.status, "Overdue")
