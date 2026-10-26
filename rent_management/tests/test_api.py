# Copyright (c) 2026, Shashank Dixit and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from rent_management import api
from rent_management.rent_management_system.doctype.tenant_rent_invoice.test_tenant_rent_invoice import (
	make_invoice,
)
from rent_management.rent_management_system.doctype.tenant_space_allotment.test_tenant_space_allotment import (
	make_room,
)


def make_user(email, roles=()):
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": "Api", "send_welcome_email": 0}
		).insert()
	user = frappe.get_doc("User", email)
	if roles:
		user.add_roles(*roles)
	return email


class TestRentApi(IntegrationTestCase):
	def setUp(self):
		self.manager = make_user("api.manager@example.com", ["Rent Manager"])
		self.outsider = make_user("no.role@example.com")
		frappe.set_user(self.manager)

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_requires_rent_role(self):
		frappe.set_user(self.outsider)
		for method in (api.get_boot, api.get_dashboard, api.get_rooms, api.get_tenants, api.get_deposits):
			self.assertRaises(frappe.PermissionError, method)
		self.assertFalse(api.has_app_permission())

	def test_move_in_bill_and_collect(self):
		room = make_room(rent=6000, deposit=12000)
		tenant = api.save_tenant({"first_name": "Api", "last_name": "Tenant", "mobile_no": "+91 90000 00000"})
		allotment = api.allot_room(tenant, room.name, "2026-01-01", deposit_collected=1)

		rooms = {r.name: r for r in api.get_rooms()}
		self.assertEqual(rooms[room.name].status, "Occupied")
		self.assertEqual(rooms[room.name].current_allotment, allotment)

		invoice = api.create_invoice(
			allotment,
			"January",
			2026,
			charges=[{"charge_type": "Electricity", "amount": 500}, {"charge_type": "Water", "amount": 0}],
			posting_date="2026-01-01",
			due_date="2026-01-05",
			submit=1,
		)
		detail = api.get_invoice(invoice)
		self.assertEqual(detail["invoice"].final_amount, 6500)
		self.assertEqual(len(detail["invoice"].charges), 1)  # zero-amount rows are dropped

		api.record_payment(invoice, 4000, "UPI", reference_no="UTR1")
		self.assertEqual(frappe.db.get_value("Tenant Rent Invoice", invoice, "outstanding_amount"), 2500)

		tenant_view = api.get_tenant(tenant)
		self.assertEqual(tenant_view["totals"]["paid"], 4000)
		self.assertEqual(tenant_view["totals"]["outstanding"], 2500)
		listed = {str(t.name): t for t in api.get_tenants(search="Api Tenant")}
		self.assertEqual(listed[str(tenant)].room, room.name)

		outstanding = api.get_outstanding(as_on_date="2026-01-20", tenant=tenant)
		self.assertEqual(outstanding["rows"][0].outstanding_amount, 2500)
		self.assertEqual(sum(b["amount"] for b in outstanding["buckets"]), 2500)

		# move out and settle the deposit against the unpaid rent
		api.vacate_room(allotment, "2026-01-31")
		self.assertEqual([p.name for p in api.get_deposits()["pending"]], [allotment])
		preview = api.preview_settlement(allotment, deductions=[{"reason": "Cleaning", "amount": 500}])
		self.assertEqual(preview["rent_adjusted"], 2500)
		self.assertEqual(preview["refund_amount"], 9000)
		api.settle_deposit(
			allotment, deductions=[{"reason": "Cleaning", "amount": 500}], mode_of_refund="UPI"
		)
		self.assertEqual(frappe.db.get_value("Tenant Rent Invoice", invoice, "status"), "Paid")

	def test_dashboard_and_invoice_list(self):
		room = make_room(rent=3000)
		allotment = frappe.get_doc(
			"Tenant Space Allotment",
			api.allot_room(api.save_tenant({"first_name": "Dash"}), room.name, "2026-01-01"),
		)
		make_invoice(allotment, "January", due_date="2026-01-05", submit=True)
		draft = make_invoice(allotment, "February", posting_date="2026-02-01")

		dashboard = api.get_dashboard()
		self.assertGreaterEqual(dashboard["outstanding"]["overdue_count"], 1)
		self.assertGreaterEqual(dashboard["draft_invoices"], 1)
		self.assertEqual(len(dashboard["trend"]), 6)

		result = api.get_invoices(status="Draft", search=room.name)
		self.assertEqual([i.name for i in result["invoices"]], [draft.name])
		self.assertEqual(result["counts"].get("Overdue"), 1)

		api.delete_invoice(draft.name)
		self.assertFalse(frappe.db.exists("Tenant Rent Invoice", draft.name))

	def test_rooms_and_types(self):
		room_type = api.create_room_type({"type": "Api Suite", "standard_rent": 15000})
		room = api.create_room({"room_number": "API-1", "floor": "Ground", "room_type": room_type})
		self.assertEqual(frappe.db.get_value("Tenant Space", room, "room_rent"), 15000)
