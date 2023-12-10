$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res._id);
        $("#promotion_name").val(res.name);
        $("#promotion_description").val(res.description);
        $("#promotion_products_type").val(res.products_type);
        $("#promotion_code").val(res.promotion_code);
        if (res.require_code == true) {
            $("#promotion_require_code").val("true");
        } else {
            $("#promotion_require_code").val("false");
        }
        $("#promotion_start_date").val(res.start_date);
        $("#promotion_end_date").val(res.end_date);
        if (res.is_active == true) {
            $("#promotion_is_active").val("true");
        } else {
            $("#promotion_is_active").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_id").val("");
        $("#promotion_name").val("");
        $("#promotion_description").val("");
        $("#promotion_products_type").val("");
        $("#promotion_code").val("");
        $("#promotion_require_code").val("");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
        $("#promotion_is_active").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#promotion_name").val();
        let description = $("#promotion_description").val();
        let products_type = $("#promotion_products_type").val();
        let promotion_code = $("#promotion_code").val();
        let require_code = $("#promotion_require_code").val() == "true";
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();
        let is_active = $("#promotion_is_active").val() == "true";

        let data = {
            "name": name,
            "description": description,
            "products_type": products_type,
            "promotion_code": promotion_code,
            "require_code": require_code,
            "start_date": start_date,
            "end_date": end_date,
            "is_active": is_active
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {

        let promotion_id = $("#promotion_id").val();
        let name = $("#promotion_name").val();
        let description = $("#promotion_description").val();
        let products_type = $("#promotion_products_type").val();
        let promotion_code = $("#promotion_code").val();
        let require_code = $("#promotion_require_code").val() == "true";
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();
        let is_active = $("#promotion_is_active").val() == "true";

        let data = {
            "name": name,
            "description": description,
            "products_type": products_type,
            "promotion_code": promotion_code,
            "require_code": require_code,
            "start_date": start_date,
            "end_date": end_date,
            "is_active": is_active
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/promotions/${promotion_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Read a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Promotion
    // ****************************************

    $("#delete-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            $("#search-btn").click();
            flash_message("Promotion has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Activate a Promotion
    // ****************************************

    $("#activate-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/promotions/${promotion_id}/activate`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
        
    });

    // ****************************************
    // Deactivate a Promotion
    // ****************************************

    $("#deactivate-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/promotions/${promotion_id}/deactivate`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
        
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#promotion_name").val();
        let productsType = $("#promotion_products_type").val();
        let requireCode = $("#promotion_require_code").val();
        let startDate = $("#promotion_start_date").val();
        let endDate = $("#promotion_end_date").val();

        let queryString = ""

        function appendQueryParam(key, value) {
            if (queryString.length > 0) {
              queryString += '&' + key + '=' + value;
            } else {
              queryString += key + '=' + value;
            }
          }

          if (name) {
            appendQueryParam('name', name);
          }
          
          if (productsType) {
            appendQueryParam('products_type', productsType);
          }
          
          if (requireCode && requireCode.toLowerCase() !== 'all') {
            appendQueryParam('require_code', requireCode.toLowerCase() === 'true' ? 'true' : 'false');
          }
          
          if (startDate) {
            appendQueryParam('start_date', startDate);
          }
          
          if (endDate) {
            appendQueryParam('end_date', endDate);
          }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/promotions?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>';
            table += '<th>ID</th>';
            table += '<th>Name</th>';
            table += '<th>Description</th>';
            table += '<th>Products Type</th>';
            table += '<th>Promotion Code</th>';
            table += '<th>Require Code</th>';
            table += '<th>Start Date</th>';
            table += '<th>End Date</th>';
            table += '<th>Is Active</th>';
            table += '</tr></thead><tbody>';
            let firstPromotion = "";
            for(let i = 0; i < res.length; i++) {
                let promotion = res[i];
                table +=  `<tr id="row_${i}"><td>${promotion._id}</td><td>${promotion.name}</td><td>${promotion.description}</td><td>${promotion.products_type}</td><td>${promotion.promotion_code}</td><td>${promotion.require_code ? 'Yes' : 'No'}</td><td>${promotion.start_date}</td><td>${promotion.end_date}</td><td>${promotion.is_active ? 'Yes' : 'No'}</td></tr>`;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);
    
            flash_message("Success");
        });
    
        ajax.fail(function(res){
            flash_message(res.responseJSON.message);
        });
    
    });

})
