(function($) {
    function toggleOtherPaymentTextField(row) {
        // Find the payment_type select within this row
        var $paymentTypeSelect = $(row).find('.field-payment_type select');
        // Find the other_payment_text div within this row
        var $otherPaymentText = $(row).find('.field-other_payment_text');

        // Show or hide the other_payment_text based on payment_type value or if text is present
        if ($paymentTypeSelect.val() === 'other' || $otherPaymentText.find('textarea, input').val().trim() !== '') {
            $otherPaymentText.show();
        } else {
            $otherPaymentText.hide();
        }
    }

    // When the DOM is ready, set up the initial state and event handlers
    $(document).ready(function() {
        // Set up initial state for each existing row
        $('.inline-related .form-row').each(function() {
            toggleOtherPaymentTextField(this);
        });

        // Event handler for when payment_type changes
        $('.inline-related').on('change', '.field-payment_type select', function() {
            toggleOtherPaymentTextField($(this).closest('.form-row'));
        });

        // Event handler for when a new form is added
        $(document).on('formset:added', function(event, $row, formsetName) {
            toggleOtherPaymentTextField($row);
            // Re-bind the change event to the new row
            $row.find('.field-payment_type select').change(function() {
                toggleOtherPaymentTextField($(this).closest('.form-row'));
            });
        });
    });
})(django.jQuery);
