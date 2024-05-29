frappe.ui.form.on('Library Transaction', {
  refresh: function(frm) {
  frm.add_custom_button('Fine', () => {
    d = new frappe.ui.Dialog({
    title: 'Pay Fine',
    fields: [
      {
        label: 'Amount',
        fieldname: 'total_fine',
        fieldtype: 'Currency'
      },
      {
        label: 'Date',
        fieldname: 'date',
        fieldtype: 'Date'
      },
    ],
    size: 'small', // small, large, extra-large
    primary_action_label: 'Submit',
    primary_action(values) {
      console.log(values);
      d.hide();
    }
  });
  d.show();// Ensure closing bracket here
});
frm.set_query('article', () => {
 return {
     filters: {
         Status: 'Available'
     }
 }
})
// change the filter method by passing a custom method
// Assuming you are working with Frappe framework
// frappe.ui.form.on('LibraryTransaction', {
//     fieldname: function(frm) {
//         frm.set_query('article', function() {
//             return {
//                 query: 'library_management.library_transaction.custom_query',
//                 filters: {
//                     Status: 'Available'
//                 }
//             };
//         });
//     }
// });


  }
});
// only message
// only message
// frappe.msgprint(__('Document updated successfully'));

// with options
// frappe.confirm('Are you sure you want to proceed?',
//     () => {
//         frappe.confirm(message, if_yes)
//     }, () => {
//         frappe.confirm(message, if_no)
//     })
