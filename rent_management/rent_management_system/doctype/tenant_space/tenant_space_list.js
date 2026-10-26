// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.listview_settings["Tenant Space"] = {
	add_fields: ["status"],
	get_indicator(doc) {
		const colors = {
			Available: "green",
			Reserved: "blue",
			Occupied: "orange",
			"Under Renovation": "gray",
		};
		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	},
};
