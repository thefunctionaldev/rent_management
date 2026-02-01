// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tenant Space Allotment", {
    refresh: function(frm) {
        // 1. Only show the button if the document is NOT new and is SUBMITTED
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            
            frm.add_custom_button(__('Create Rent Invoice'), function() {
                // 2. Open a new Rent Invoice and pre-fill it
                frappe.new_doc("Tenant Rent Invoice", {
                    "tenant": frm.doc.tenant,
                    "room": frm.doc.room, // Note: usually 'room' is the field name, not 'name'
                    "monthly_rent": frm.doc.rent_amount, 
                    "tenant_space_allotment": frm.doc.name
                });
            }, __("Create"));
        }
    }
});