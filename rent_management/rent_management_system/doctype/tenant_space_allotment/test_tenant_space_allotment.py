# Copyright (c) 2026, Shashank Dixit and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


def make_room(rent=3000, deposit=None):
	room_type = frappe.get_doc(
		{
			"doctype": "Tenant Space Type",
			"type": "Test Type " + frappe.generate_hash(length=6),
			"standard_rent": rent,
			"deposit_applicable": 1 if deposit else 0,
			"security_deposit": deposit,
		}
	).insert()
	return frappe.get_doc(
		{
			"doctype": "Tenant Space",
			"room_number": "T-" + frappe.generate_hash(length=6),
			"floor": "Ground",
			"room_type": room_type.name,
		}
	).insert()


def make_tenant():
	return frappe.get_doc({"doctype": "Tenant", "first_name": "Test", "last_name": "Tenant"}).insert()


def make_allotment(room=None, tenant=None, allotment_date="2026-01-01", submit=True, **kwargs):
	allotment = frappe.get_doc(
		{
			"doctype": "Tenant Space Allotment",
			"tenant": (tenant or make_tenant()).name,
			"room": (room or make_room()).name,
			"allotment_date": allotment_date,
			**kwargs,
		}
	).insert()
	if submit:
		allotment.submit()
	return allotment


class IntegrationTestTenantSpaceAllotment(IntegrationTestCase):
	def test_rent_and_deposit_from_room(self):
		room = make_room(rent=4500, deposit=9000)
		allotment = make_allotment(room=room, submit=False)
		self.assertEqual(allotment.rent_amount, 4500)
		self.assertEqual(allotment.security_deposit, 9000)
		self.assertEqual(allotment.status, "Draft")

	def test_submit_occupies_room(self):
		allotment = make_allotment()
		self.assertEqual(allotment.status, "Active")
		room = frappe.get_doc("Tenant Space", allotment.room)
		self.assertEqual(room.status, "Occupied")
		self.assertEqual(str(room.tenant), str(allotment.tenant))
		self.assertEqual(room.current_allotment, allotment.name)

	def test_room_cannot_be_allotted_twice(self):
		allotment = make_allotment()
		room = frappe.get_doc("Tenant Space", allotment.room)
		self.assertRaises(frappe.ValidationError, make_allotment, room=room)

	def test_vacate_frees_room(self):
		allotment = make_allotment()
		self.assertRaises(frappe.ValidationError, allotment.vacate, "2025-12-31")

		allotment.vacate("2026-02-15")
		allotment.reload()
		self.assertEqual(allotment.status, "Vacated")
		self.assertEqual(str(allotment.vacate_date), "2026-02-15")
		self.assertEqual(frappe.db.get_value("Tenant Space", allotment.room, "status"), "Available")

		# room can now be allotted again
		make_allotment(room=frappe.get_doc("Tenant Space", allotment.room), allotment_date="2026-03-01")

	def test_cancel_frees_room(self):
		allotment = make_allotment()
		allotment.cancel()
		self.assertEqual(allotment.status, "Cancelled")
		room = frappe.get_doc("Tenant Space", allotment.room)
		self.assertEqual(room.status, "Available")
		self.assertFalse(room.tenant)


class IntegrationTestRentManagerRole(IntegrationTestCase):
	def test_rent_manager_permissions(self):
		email = "rent.manager@example.com"
		if not frappe.db.exists("User", email):
			frappe.get_doc(
				{"doctype": "User", "email": email, "first_name": "Rent", "send_welcome_email": 0}
			).insert()
		user = frappe.get_doc("User", email)
		user.add_roles("Rent Manager")

		for doctype in (
			"Tenant",
			"Tenant Space",
			"Tenant Space Allotment",
			"Tenant Rent Invoice",
			"Rent Payment",
			"Security Deposit Settlement",
		):
			self.assertTrue(frappe.has_permission(doctype, "create", user=email), doctype)
		for doctype in ("Tenant Space Allotment", "Tenant Rent Invoice", "Rent Payment"):
			self.assertTrue(frappe.has_permission(doctype, "submit", user=email), doctype)
		self.assertTrue(frappe.has_permission("Rent Management Settings", "write", user=email))
