// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tenant Space Allotment", {
    refresh(frm) {
        if (!frm.is_new()) { // Only show button on saved records
            frm.add_custom_button(__('Create Rent Invoice'), function() {
                // Open a new Rent Invoice and pre-fill it
                frappe.new_doc("Tenant Rent Invoice", {
                    "tenant": frm.doc.tenant,
                    "room": frm.doc.name,
                    "monthly_rent": frm.doc.rent_amount // If you have this field
                });
            }, __("Create"));
        }
    },
});