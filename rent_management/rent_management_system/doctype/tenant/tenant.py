# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class Tenant(Document):
    def validate(self):
        # These call the methods defined below
        self.set_name()
        self.check_aadhar()

    def set_name(self):
        # Indented 4 spaces to stay inside the class
        parts = [self.first_name, self.middle_name, self.last_name]
        self.full_name = " ".join(filter(None, parts)).strip()

    def check_aadhar(self):
        # Indented 4 spaces to stay inside the class
        if not self.aadhar_card_number:
            return

        # Verhoeff Algorithm Tables
        d = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], 
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6], [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], 
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1], 
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], 
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        ]
        p = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], 
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2], [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], 
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1], 
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]

        # 1. Clean input
        aadhar = str(self.aadhar_card_number).replace(" ", "")

        # 2. Length Check
        if not aadhar.isdigit() or len(aadhar) != 12:
            frappe.throw(_("Aadhaar Number must be exactly 12 digits."))

        # 3. First Digit Rule
        if aadhar[0] in ['0', '1']:
            frappe.throw(_("Invalid Aadhaar: Cannot start with 0 or 1."))

        # 4. Verhoeff Checksum
        c = 0
        reversed_aadhar = aadhar[::-1]
        
        for i in range(len(reversed_aadhar)):
            # Ensure this loop is properly indented under check_aadhar
            c = d[c][p[i % 8][int(reversed_aadhar[i])]]

        if c != 0:
            frappe.throw(_("Aadhaar validation failed. The checksum is incorrect."))
        else:
           frappe.msgprint(
    msg=_("Aadhaar has been successfully verified against the Verhoeff checksum."),
    title=_("Verification Success"),
    indicator="green"
)