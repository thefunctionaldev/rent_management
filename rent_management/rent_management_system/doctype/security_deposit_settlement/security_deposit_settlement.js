// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Security Deposit Settlement", {
	setup(frm) {
		frm.set_query("tenant_space_allotment", () => ({
			filters: {
				docstatus: 1,
				status: "Vacated",
				deposit_collected: 1,
				deposit_settlement: ["is", "not set"],
			},
		}));
	},

	onload(frm) {
		if (frm.is_new() && frm.doc.tenant_space_allotment) update_amounts(frm);
	},

	tenant_space_allotment: update_amounts,
	adjust_outstanding_rent: update_amounts,
});

frappe.ui.form.on("Security Deposit Deduction", {
	amount: update_amounts,
	deductions_remove: update_amounts,
});

function update_amounts(frm) {
	if (frm.doc.docstatus === 0 && frm.doc.tenant_space_allotment) {
		frm.call("update_amounts");
	}
}
