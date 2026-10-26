// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.listview_settings["Tenant Space Allotment"] = {
	add_fields: ["status"],
	get_indicator(doc) {
		const colors = { Draft: "red", Active: "green", Vacated: "gray", Cancelled: "red" };
		return [__(doc.status), colors[doc.status], "status,=," + doc.status];
	},
};
