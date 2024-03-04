(function($) {
    $(document).ready(function() {
        function updateMaterialOptions() {
            var categoryId = $('#id_category').val();
            var materialField = $('#id_material');
            var url = '/get_materials/?category_id=' + categoryId; // URL to fetch related materials
            var selectedMaterial = materialField.val(); // Store the currently selected material ID

            // Fetch related materials using AJAX
            $.getJSON(url, function(data) {
                materialField.empty(); // Clear existing options
                var materialExists = false; // Flag to check if the previously selected material exists in the new list
                $.each(data.materials, function(key, value) {
                    materialField.append($('<option></option>').attr('value', key).text(value));
                    if (key == selectedMaterial) {
                        materialExists = true; // The previously selected material exists in the new list
                    }
                });

                if (materialExists) {
                    materialField.val(selectedMaterial); // Re-select the previously selected material if it exists
                }
            });
        }

        $('#id_category').change(function() {
            updateMaterialOptions();
        });

        // Trigger initial update when the page loads
        updateMaterialOptions();
    });
})(django.jQuery);
