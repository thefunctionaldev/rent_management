// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Tenant Rent Invoice", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Tenant Rent Invoice', {
    tenant_space_allotment: function(frm) {
        if (frm.doc.tenant_space_allotment) {
            frappe.db.get_value('Tenant Space Allotment', frm.doc.tenant_space_allotment, 'allotment_date', (r) => {
                // Debugging: Check the console (F12) to see what 'r' actually contains
                console.log("Allotment Data:", r);

                if (r && r.allotment_date) {
                    // 1. Convert string to Date Object
                    let date_obj = frappe.datetime.str_to_obj(r.allotment_date);
                    //frappe.msgprint(__('Allotment Date: {0}', [r.allotment_date]));
                    // 2. Get the Month Name
                    let month_name = date_obj.toLocaleString('default', { month: 'long' });
                   // frappe.msgprint(__('Identified Month: {0}', [month_name]));
                   let year = date_obj.getFullYear();
                    
                    // 3. Set the value and show the message
                    frm.set_value('billing_month', month_name);
                    frm.set_value('billing_year', year);
                    
                   // frappe.msgprint(__('Billing Month identified as: {0}', [month_name]));
                } else {
                    console.error("Allotment Date field is empty or not found in the source DocType.");
                }
            });
        }
    }
});