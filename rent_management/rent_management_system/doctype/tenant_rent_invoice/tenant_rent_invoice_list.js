// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.listview_settings["Tenant Rent Invoice"] = {
	add_fields: ["status", "outstanding_amount", "due_date"],
	get_indicator(doc) {
		const colors = {
			Draft: "red",
			Unpaid: "orange",
			"Partly Paid": "yellow",
			Paid: "green",
			Overdue: "red",
			Cancelled: "red",
		};
		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	},
};
