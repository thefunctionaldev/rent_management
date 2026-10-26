# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

# Verhoeff algorithm tables, used for the Aadhaar checksum
VERHOEFF_D = (
	(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
	(1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
	(2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
	(3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
	(4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
	(5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
	(6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
	(7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
	(8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
	(9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)
VERHOEFF_P = (
	(0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
	(1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
	(5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
	(8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
	(9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
	(4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
	(2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
	(7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)


class Tenant(Document):
	def validate(self):
		self.set_full_name()
		self.check_aadhar()

	def set_full_name(self):
		parts = [self.first_name, self.middle_name, self.last_name]
		self.full_name = " ".join(filter(None, parts)).strip()

	def check_aadhar(self):
		if not self.aadhar_card_number:
			return

		aadhar = str(self.aadhar_card_number).replace(" ", "")

		if not aadhar.isdigit() or len(aadhar) != 12:
			frappe.throw(_("Aadhaar Number must be exactly 12 digits."))

		if aadhar[0] in ("0", "1"):
			frappe.throw(_("Invalid Aadhaar: Cannot start with 0 or 1."))

		if not is_valid_verhoeff(aadhar):
			frappe.throw(_("Aadhaar validation failed. The checksum is incorrect."))

		self.aadhar_card_number = aadhar

		if self.has_value_changed("aadhar_card_number"):
			frappe.msgprint(
				msg=_("Aadhaar has been successfully verified against the Verhoeff checksum."),
				title=_("Verification Success"),
				indicator="green",
			)


def is_valid_verhoeff(number: str) -> bool:
	c = 0
	for i, digit in enumerate(reversed(number)):
		c = VERHOEFF_D[c][VERHOEFF_P[i % 8][int(digit)]]
	return c == 0
