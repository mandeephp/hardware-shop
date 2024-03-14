document.addEventListener('DOMContentLoaded', function() {
  const dateFilter = document.getElementById('purchase_date_filter'); // Adjust the ID to match your date input element

  // Check if the dateFilter element exists to avoid errors
  if (!dateFilter) {
    return;
  }

  dateFilter.addEventListener('change', function() {
    const selectedDate = this.value;

    // This selector targets the specific inline divs
    const purchaseSections = document.querySelectorAll('.djn-item.djn-module.djn-inline-form.has_original.inline-related.dynamic-form.grp-dynamic-form.djn-dynamic-form-accounts-purchase');

    purchaseSections.forEach(function(section) {
      // Retrieve the purchase date from the corresponding input field
      const purchaseDateInput = section.querySelector('input[name*="purchase_date"]');
      const purchaseDate = purchaseDateInput ? purchaseDateInput.value : null;

      if (purchaseDate === selectedDate) {
        section.classList.add('highlight');
        section.style.display = 'block'; // Ensure the section is visible
      } else {
        section.classList.remove('highlight');
        section.style.display = 'none'; // Hide the section
      }
    });
  });
});
