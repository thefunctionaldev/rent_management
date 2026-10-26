// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tenant Rent Invoice", {
	setup(frm) {
		frm.set_query("tenant_space_allotment", () => ({
			filters: { docstatus: 1, status: ["in", ["Active", "Vacated"]] },
		}));
	},

	onload(frm) {
		if (frm.is_new() && !frm.doc.billing_month) {
			const posting_date = frappe.datetime.str_to_obj(
				frm.doc.posting_date || frappe.datetime.get_today()
			);
			frm.set_value("billing_month", moment(posting_date).format("MMMM"));
			frm.set_value("billing_year", posting_date.getFullYear());
		}
	},

	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.outstanding_amount > 0) {
			frm.add_custom_button(
				__("Rent Payment"),
				() => {
					frappe.new_doc("Rent Payment", {
						tenant: frm.doc.tenant,
						rent_invoice: frm.doc.name,
						amount: frm.doc.outstanding_amount,
					});
				},
				__("Create")
			);
			frm.page.set_inner_btn_group_as_primary(__("Create"));
		}
	},

	discount_amount: calculate_total,
});

frappe.ui.form.on("Tenant Rent Invoice Charge", {
	amount: calculate_total,
	charges_remove: calculate_total,
});

// rough client-side preview; the server recalculates everything on save
function calculate_total(frm) {
	const total_charges = (frm.doc.charges || []).reduce((sum, row) => sum + flt(row.amount), 0);
	frm.set_value("total_charges", total_charges);
	if (frm.doc.pro_rated_rent) {
		frm.set_value(
			"final_amount",
			flt(frm.doc.pro_rated_rent) + total_charges - flt(frm.doc.discount_amount)
		);
	}
}
