# Copyright (c) 2026, Shashank Dixit and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
import calendar
from frappe.email.queue import getdate
from frappe.model.document import Document
from frappe.utils.data import date_diff, get_last_day


class TenantRentInvoice(Document):
	def validate(self):
		if self.tenant_space_allotment:
			month_number = datetime.strptime(self.billing_month, "%B").month
			#frappe.msgprint(f"Month Number: {month_number}")
			month_range = calendar.monthrange(self.billing_year, month_number)
			days_in_month = month_range[1]

			# 2. Set the value so it shows in the DocType field
			self.total_days = days_in_month

			# 3. Print the message to verify
			#frappe.msgprint(f"Total Days in Billing Month: {self.total_days}")

		if self.tenant_space_allotment:
			allotment_date_str = frappe.db.get_value("Tenant Space Allotment",
				self.tenant_space_allotment,
				"allotment_date")

			if allotment_date_str:
				allotment_date = getdate(allotment_date_str)

				# 2. Find the Last Day of that specific month
				last_day_of_month = get_last_day(allotment_date)

				# 3. Calculate Days Stayed
				# We add +1 because if someone stays from 15th to 15th, it's 1 day.
				self.days_stayed = date_diff(last_day_of_month, allotment_date) + 1

				# 4. Verification Message
				#frappe.msgprint(f"Days Stayed in {self.billing_month}: {self.days_stayed}")
				# 5. Calculate Pro-rated Rent
				if self.total_days > 0:
					self.pro_rated_rent = (self.monthly_rent / self.total_days) * self.days_stayed
					self.final_amount = self.pro_rated_rent
					# 6. Verification Message
					#frappe.msgprint(f"Pro-rated Rent for {self.days_stayed} days: {self.pro_rated_rent}")
				else:
					frappe.msgprint("Total days in month is zero, cannot calculate pro-rated rent.")