// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rent Payment", {
	setup(frm) {
		frm.set_query("rent_invoice", () => ({
			filters: {
				docstatus: 1,
				outstanding_amount: [">", 0],
				...(frm.doc.tenant ? { tenant: frm.doc.tenant } : {}),
			},
		}));
	},

	rent_invoice(frm) {
		if (!frm.doc.rent_invoice) return;
		frappe.db
			.get_value("Tenant Rent Invoice", frm.doc.rent_invoice, [
				"tenant",
				"outstanding_amount",
			])
			.then(({ message }) => {
				if (!frm.doc.tenant) frm.set_value("tenant", message.tenant);
				frm.set_value("amount", message.outstanding_amount);
			});
	},
});
