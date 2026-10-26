# Copyright (c) 2026, Shashank Dixit and Contributors
# See license.txt

from frappe.tests import IntegrationTestCase

from rent_management.rent_management_system.doctype.rent_payment.test_rent_payment import make_payment
from rent_management.rent_management_system.doctype.tenant_rent_invoice.test_tenant_rent_invoice import (
	make_invoice,
)
from rent_management.rent_management_system.doctype.tenant_space_allotment.test_tenant_space_allotment import (
	make_allotment,
	make_room,
)
from rent_management.rent_management_system.report.rent_outstanding.rent_outstanding import execute


class TestRentOutstanding(IntegrationTestCase):
	def test_aging(self):
		allotment = make_allotment(room=make_room(rent=3000), allotment_date="2026-01-01")
		january = make_invoice(allotment, "January", due_date="2026-01-05", submit=True)
		make_payment(january, 1000)
		make_invoice(allotment, "February", posting_date="2026-02-01", due_date="2026-03-20", submit=True)
		paid = make_invoice(allotment, "March", posting_date="2026-03-01", submit=True)
		make_payment(paid, 3000)

		_columns, data, _message, chart, summary = execute(
			{"as_on_date": "2026-03-10", "tenant": allotment.tenant}
		)
		rows = {row.billing_period: row for row in data}
		self.assertEqual(set(rows), {"January 2026", "February 2026"})

		january_row = rows["January 2026"]
		self.assertEqual(january_row.outstanding_amount, 2000)
		self.assertEqual(january_row.days_overdue, 64)
		self.assertEqual(january_row.range_61_90, 2000)
		self.assertEqual(rows["February 2026"].not_due, 3000)

		self.assertEqual(summary[0]["value"], 5000)
		self.assertEqual(summary[1]["value"], 2000)
		self.assertEqual(sum(chart["data"]["datasets"][0]["values"]), 5000)

		_columns, data, *_rest = execute(
			{"as_on_date": "2026-03-10", "tenant": allotment.tenant, "overdue_only": 1}
		)
		self.assertEqual([row.billing_period for row in data], ["January 2026"])
