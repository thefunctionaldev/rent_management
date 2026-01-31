# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


import frappe
from frappe.model.document import Document

class TenantSpaceAllotment(Document):
    def on_submit(self):
        if self.room and self.status == "Alloted":
            # Updating multiple fields in ONE database call
            frappe.db.set_value("Tenant Space", self.room, {
                "status": "Occupied",
                "tenant": self.tenant,
                "checkin_date": self.allotment_date
            })
            
            frappe.msgprint(f"Room {self.room} status updated to Occupied.")

    def on_cancel(self):
        if self.room and self.status == "Alloted":
            # Clearing fields on cancellation
            frappe.db.set_value("Tenant Space", self.room, {
                "status": "Available",
                "tenant": None,
                "checkin_date": None,
                "tenant_name": None
            })