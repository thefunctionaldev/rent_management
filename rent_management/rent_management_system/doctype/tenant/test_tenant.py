# Copyright (c) 2026, Shashank Dixit and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from rent_management.rent_management_system.doctype.tenant.tenant import (
	VERHOEFF_D,
	VERHOEFF_P,
	is_valid_verhoeff,
)

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []

VERHOEFF_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def make_aadhaar(first_11: str) -> str:
	"""Append the Verhoeff check digit to an 11 digit number."""
	c = 0
	for i, digit in enumerate(reversed(first_11)):
		c = VERHOEFF_D[c][VERHOEFF_P[(i + 1) % 8][int(digit)]]
	return first_11 + str(VERHOEFF_INV[c])


class IntegrationTestTenant(IntegrationTestCase):
	def test_full_name(self):
		tenant = frappe.get_doc(
			{"doctype": "Tenant", "first_name": "Ravi", "middle_name": "", "last_name": "Kumar"}
		).insert()
		self.assertEqual(tenant.full_name, "Ravi Kumar")

	def test_valid_aadhaar(self):
		aadhaar = make_aadhaar("23456789012")
		self.assertTrue(is_valid_verhoeff(aadhaar))
		tenant = frappe.get_doc(
			{"doctype": "Tenant", "first_name": "Asha", "aadhar_card_number": f"{aadhaar[:4]} {aadhaar[4:]}"}
		).insert()
		self.assertEqual(tenant.aadhar_card_number, aadhaar)

	def test_invalid_aadhaar(self):
		valid = make_aadhaar("23456789012")
		wrong_checksum = valid[:-1] + str((int(valid[-1]) + 1) % 10)
		for number in (wrong_checksum, "1" + valid[1:], "12345", "abcdefghijkl"):
			tenant = frappe.get_doc({"doctype": "Tenant", "first_name": "X", "aadhar_card_number": number})
			self.assertRaises(frappe.ValidationError, tenant.insert)
