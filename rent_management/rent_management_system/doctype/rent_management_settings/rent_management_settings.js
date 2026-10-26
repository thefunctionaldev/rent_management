// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rent Management Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Generate Invoices Now"), () => {
			const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
			frappe.prompt(
				[
					{
						fieldname: "billing_month",
						fieldtype: "Select",
						label: __("Billing Month"),
						options: moment.months(),
						default: moment(today).format("MMMM"),
						reqd: 1,
					},
					{
						fieldname: "billing_year",
						fieldtype: "Int",
						label: __("Billing Year"),
						default: today.getFullYear(),
						reqd: 1,
					},
					{
						fieldname: "submit",
						fieldtype: "Check",
						label: __("Submit Invoices"),
						default: frm.doc.auto_submit_invoices,
					},
				],
				(values) => {
					frappe.call({
						method: "rent_management.rent_management_system.doctype.rent_management_settings.rent_management_settings.generate_invoices_now",
						args: values,
						freeze: true,
					});
				},
				__("Generate Rent Invoices"),
				__("Generate")
			);
		});
	},
});
