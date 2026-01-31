// Copyright (c) 2026, Shashank Dixit and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Tenant", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Tenant', {
    aadhar_card_number: function(frm) {
        if (frm.doc.aadhar_card_number) {
            let aadhar = frm.doc.aadhar_card_number.replace(/\s/g, "");

            // 1. Instant First Digit Check
            if (aadhar.length > 0 && ['0', '1'].includes(aadhar[0])) {
                // Clear the field and alert the user immediately
                frm.set_value('aadhar_card_number', '');
                frappe.msgprint(__('Invalid Aadhaar: Cannot start with 0 or 1.'));
            }
            
            // 2. Length check only after user is done (optional UX improvement)
            if (aadhar.length > 12) {
                frappe.msgprint(__('Aadhaar cannot exceed 12 digits.'));
                frm.set_value('aadhar_card_number', aadhar.substring(0, 12));
            }
        }
    },

    validate: function(frm) {
        // This only runs once when the user clicks 'Save'
        if (frm.doc.aadhar_card_number) {
            let aadhar = frm.doc.aadhar_card_number.replace(/\s/g, "");
            
            if (aadhar.length !== 12) {
                frappe.msgprint(__('Final Check: Aadhaar must be exactly 12 digits.'));
                frappe.validated = false; // Stops the save
            }
        }
    }
});