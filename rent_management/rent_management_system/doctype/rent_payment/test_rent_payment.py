# Copyright (c) 2026, Shashank Dixit and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, nowdate

from rent_management.rent_management_system.doctype.tenant_rent_invoice.test_tenant_rent_invoice import (
	make_invoice,
)
from rent_management.rent_management_system.doctype.tenant_space_allotment.test_tenant_space_allotment import (
	make_allotment,
	make_room,
)

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


def make_payment(invoice, amount, submit=True):
	payment = frappe.get_doc(
		{
			"doctype": "Rent Payment",
			"tenant": invoice.tenant,
			"rent_invoice": invoice.name,
			"amount": amount,
			"mode_of_payment": "Cash",
		}
	).insert()
	if submit:
		payment.submit()
	return payment


class IntegrationTestRentPayment(IntegrationTestCase):
	def setUp(self):
		allotment = make_allotment(room=make_room(rent=3000))
		self.invoice = make_invoice(allotment, due_date=add_days(nowdate(), 30), submit=True)

	def test_partial_and_full_payment(self):
		first = make_payment(self.invoice, 1000)
		self.invoice.reload()
		self.assertEqual(self.invoice.paid_amount, 1000)
		self.assertEqual(self.invoice.outstanding_amount, 2000)
		self.assertEqual(self.invoice.status, "Partly Paid")

		make_payment(self.invoice, 2000)
		self.invoice.reload()
		self.assertEqual(self.invoice.outstanding_amount, 0)
		self.assertEqual(self.invoice.status, "Paid")

		first.cancel()
		self.invoice.reload()
		self.assertEqual(self.invoice.paid_amount, 2000)
		self.assertEqual(self.invoice.status, "Partly Paid")

	def test_overpayment(self):
		self.assertRaises(frappe.ValidationError, make_payment, self.invoice, 3001)

	def test_wrong_tenant(self):
		other = make_allotment()
		payment = frappe.get_doc(
			{
				"doctype": "Rent Payment",
				"tenant": other.tenant,
				"rent_invoice": self.invoice.name,
				"amount": 100,
			}
		)
		self.assertRaises(frappe.ValidationError, payment.insert)

	def test_draft_invoice(self):
		draft = make_invoice(make_allotment())
		self.assertRaises(frappe.ValidationError, make_payment, draft, 100)

	def test_invoice_cannot_be_cancelled_with_payments(self):
		make_payment(self.invoice, 500)
		self.invoice.reload()
		self.assertRaises(frappe.LinkExistsError, self.invoice.cancel)
