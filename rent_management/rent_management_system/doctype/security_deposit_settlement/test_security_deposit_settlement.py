# Copyright (c) 2026, Shashank Dixit and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from rent_management.rent_management_system.doctype.rent_payment.test_rent_payment import make_payment
from rent_management.rent_management_system.doctype.tenant_rent_invoice.test_tenant_rent_invoice import (
	make_invoice,
)
from rent_management.rent_management_system.doctype.tenant_space_allotment.test_tenant_space_allotment import (
	make_allotment,
	make_room,
)

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


def make_settlement(allotment, deductions=(), submit=False, **kwargs):
	settlement = frappe.get_doc(
		{
			"doctype": "Security Deposit Settlement",
			"tenant_space_allotment": allotment.name,
			"settlement_date": "2026-02-15",
			"deductions": [{"reason": reason, "amount": amount} for reason, amount in deductions],
			"mode_of_refund": "Bank Transfer",
			**kwargs,
		}
	).insert()
	if submit:
		settlement.submit()
	return settlement


def make_vacated_allotment(rent=3000, deposit=10000, collected=1):
	allotment = make_allotment(
		room=make_room(rent=rent),
		allotment_date="2026-01-01",
		security_deposit=deposit,
		deposit_collected=collected,
		deposit_collected_on="2026-01-01" if collected else None,
	)
	allotment.vacate("2026-02-10")
	return allotment


class IntegrationTestSecurityDepositSettlement(IntegrationTestCase):
	def test_settle_with_rent_adjustment_and_refund(self):
		allotment = make_vacated_allotment()
		january = make_invoice(allotment, "January", submit=True)
		make_payment(january, 1000)
		february = make_invoice(allotment, "February", posting_date="2026-02-10", submit=True)
		self.assertEqual(february.final_amount, 1071.43)  # 10 of 28 days

		settlement = make_settlement(allotment, deductions=[("Cleaning", 500)])
		self.assertEqual(settlement.security_deposit, 10000)
		self.assertEqual(settlement.outstanding_rent, 3071.43)
		self.assertEqual(settlement.total_deductions, 500)
		self.assertEqual(settlement.rent_adjusted, 3071.43)
		self.assertEqual(settlement.refund_amount, 6428.57)
		self.assertEqual(settlement.balance_payable_by_tenant, 0)

		settlement.submit()
		for invoice in (january, february):
			invoice.reload()
			self.assertEqual(invoice.status, "Paid")
		payments = frappe.get_all(
			"Rent Payment",
			filters={"deposit_settlement": settlement.name, "docstatus": 1},
			fields=["mode_of_payment", "amount"],
		)
		self.assertEqual(sorted(p.amount for p in payments), [1071.43, 2000])
		self.assertEqual({p.mode_of_payment for p in payments}, {"Security Deposit"})
		self.assertEqual(
			frappe.db.get_value("Tenant Space Allotment", allotment.name, "deposit_settlement"),
			settlement.name,
		)

		# the adjustment payments can only be reversed through the settlement
		payment = frappe.get_doc("Rent Payment", {"deposit_settlement": settlement.name, "amount": 2000})
		self.assertRaises(frappe.ValidationError, payment.cancel)

		settlement.cancel()
		january.reload()
		self.assertEqual(january.outstanding_amount, 2000)
		self.assertFalse(frappe.db.get_value("Tenant Space Allotment", allotment.name, "deposit_settlement"))
		self.assertFalse(
			frappe.get_all("Rent Payment", filters={"deposit_settlement": settlement.name, "docstatus": 1})
		)

	def test_without_rent_adjustment(self):
		allotment = make_vacated_allotment()
		make_invoice(allotment, "January", submit=True)
		settlement = make_settlement(allotment, adjust_outstanding_rent=0, submit=True)
		self.assertEqual(settlement.rent_adjusted, 0)
		self.assertEqual(settlement.refund_amount, 10000)
		self.assertEqual(settlement.balance_payable_by_tenant, 3000)

	def test_deductions_more_than_deposit(self):
		allotment = make_vacated_allotment(deposit=1000)
		make_invoice(allotment, "January", submit=True)
		settlement = make_settlement(allotment, deductions=[("Damages", 1500)])
		self.assertEqual(settlement.rent_adjusted, 0)
		self.assertEqual(settlement.refund_amount, 0)
		self.assertEqual(settlement.balance_payable_by_tenant, 3500)

	def test_requires_vacated_allotment(self):
		allotment = make_allotment(
			security_deposit=5000, deposit_collected=1, deposit_collected_on="2026-01-01"
		)
		self.assertRaises(frappe.ValidationError, make_settlement, allotment)

	def test_requires_collected_deposit(self):
		allotment = make_vacated_allotment(collected=0)
		self.assertRaises(frappe.ValidationError, make_settlement, allotment)

	def test_draft_invoice_blocks_settlement(self):
		allotment = make_vacated_allotment()
		make_invoice(allotment, "January")
		self.assertRaises(frappe.ValidationError, make_settlement, allotment)

	def test_duplicate_settlement(self):
		allotment = make_vacated_allotment()
		make_settlement(allotment)
		self.assertRaises(frappe.DuplicateEntryError, make_settlement, allotment)
