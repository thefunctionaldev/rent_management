# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class TenantSpaceAllotment(Document):
	def validate(self):
		self.validate_room_is_free()
		self.set_defaults_from_room()
		if self.docstatus == 0:
			self.status = "Draft"

	def validate_room_is_free(self):
		room_status = frappe.db.get_value("Tenant Space", self.room, "status")
		if room_status in ("Occupied", "Under Renovation"):
			frappe.throw(
				_("Room {0} is {1} and cannot be allotted.").format(frappe.bold(self.room), room_status)
			)

		active_allotment = frappe.db.get_value(
			"Tenant Space Allotment",
			{"room": self.room, "docstatus": 1, "status": "Active", "name": ("!=", self.name)},
		)
		if active_allotment:
			frappe.throw(
				_("Room {0} is already allotted via {1}.").format(
					frappe.bold(self.room),
					frappe.get_desk_link(
						"Tenant Space Allotment", active_allotment, show_title_with_name=True
					),
				)
			)

	def set_defaults_from_room(self):
		if not self.rent_amount:
			self.rent_amount = frappe.db.get_value("Tenant Space", self.room, "room_rent")

		if not self.security_deposit and self.room_type:
			deposit_applicable, security_deposit = frappe.db.get_value(
				"Tenant Space Type", self.room_type, ["deposit_applicable", "security_deposit"]
			)
			if deposit_applicable:
				self.security_deposit = security_deposit

	def on_submit(self):
		self.db_set("status", "Active")
		frappe.db.set_value(
			"Tenant Space",
			self.room,
			{
				"status": "Occupied",
				"tenant": self.tenant,
				"tenant_name": self.tenant_name,
				"checkin_date": self.allotment_date,
				"current_allotment": self.name,
			},
		)
		frappe.msgprint(_("Room {0} is now Occupied.").format(frappe.bold(self.room)), alert=True)

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		self.release_room()

	@frappe.whitelist()
	def vacate(self, vacate_date=None):
		"""Mark the tenant as moved out and free up the room."""
		if self.docstatus != 1 or self.status != "Active":
			frappe.throw(_("Only an active allotment can be vacated."))

		vacate_date = getdate(vacate_date or today())
		if vacate_date < getdate(self.allotment_date):
			frappe.throw(_("Vacate Date cannot be before the Allotment Date."))

		self.db_set({"status": "Vacated", "vacate_date": vacate_date})
		self.release_room()
		frappe.msgprint(_("Room {0} is now Available.").format(frappe.bold(self.room)), alert=True)

	def release_room(self):
		# only touch the room if it still points to this allotment
		if frappe.db.get_value("Tenant Space", self.room, "current_allotment") in (self.name, None, ""):
			frappe.db.set_value(
				"Tenant Space",
				self.room,
				{
					"status": "Available",
					"tenant": None,
					"tenant_name": None,
					"checkin_date": None,
					"current_allotment": None,
				},
			)
