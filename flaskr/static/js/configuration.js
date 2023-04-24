

$(document).ready(function () {
    $('#org-config').on('submit', function () {
        if (!this.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        this.classList.add('was-validated');
    });

    var sitesEditor = new $.fn.dataTable.Editor( {
        ajax: {
            create: {
                type: "POST",
                url:  "/configuration/sites",
                contentType: 'application/json',
                accept: 'application/json',
                dataType: "json",
                data: function ( d ) {
                    const keys = Object.keys(d['data']);
                    var jsonBody = [];
                    keys.forEach(key => {
                        jsonBody.push(
                            {
                                'site': d['data'][key]["url"],
                            }
                        );
                    });
                    return JSON.stringify( jsonBody );
                },
                success: function ( d ) {
                    let affectedTable = $('#sites-table').DataTable();
                    affectedTable.draw();
                },
            },
            edit: {
                type: "PUT",
                url:  "/configuration/sites/{id}",
                contentType: 'application/json',
                accept: 'application/json',
                dataType: "json",
                data: function ( d ) {
                    const keys = Object.keys(d['data']);
                    var jsonBody = [];
                    keys.forEach(key => {
                        jsonBody.push(
                            {
                                'site': d['data'][key]["url"]
                            }
                        );
                    });
                    return JSON.stringify( jsonBody );
                },
                success: function ( d ) {
                    let affectedTable = $('#sites-table').DataTable();
                    affectedTable.draw();
                },
            },
            remove: {
                type: "DELETE",
                url:  "/configuration/sites/{id}",
                success: function ( d ) {
                    let affectedTable = $('#sites-table').DataTable();
                    affectedTable.draw();
                },
            },
        },
        table: "#sites-table",
        idSrc:  'id',
        fields: [ {
                label: "URL:",
                name: "url",
                def: "https://{SITE}.atlassian.net",
                message: "Please enter your site URL! https://{SITE}.atlassian.net"
            }
        ]
    } );

    $('#sites-table').on( 'click', 'tbody td.row-edit', function (e) {
        sitesEditor.inline( sitesTable.cells(this.parentNode, '*').nodes(), {
            onBlur: 'submit'
        } );
    });

    $('#sites-table').on( 'click', 'tbody td.row-remove', function (e) {
        sitesEditor.remove( this.parentNode, {
            title: 'Delete record',
            message: 'Are you sure you wish to delete this record?',
            buttons: 'Delete'
        } );
    } );

    var sitesTable = $('#sites-table').DataTable({
        dom: '<"row"<"col-6"B>>rt<"row"<"col-6"i>>',
        ajax: {
            url: "/configuration/sites",
        },
        columns: [
            {
                data: null,
                defaultContent: '<i class="fa fa-pencil"/>',
                className: 'row-edit dt-center',
                orderable: false
            },
            { data: "url" },
            {
                data: null,
                defaultContent: '<i class="fa fa-trash"/>',
                className: 'row-remove dt-center',
                orderable: false
            },
        ],
        select: false,
        buttons: [ {
            extend: "createInline",
            editor: sitesEditor,
            formOptions: {
                submitTrigger: -1,
                submitHtml: '<i class="fa fa-play"/>'
            }
        } ]
    });

    $('#reload-product-btn').on('click', function () {
        $('#reload-product-btn').hide();
        $('#billing-table').hide();
        $('#reload-product-spinner-btn').show();
        $.ajax({
            url: '/configuration/load-products',
            method: 'post',
            success: function(d){
                let affectedTable = $('#billing-table').DataTable();
                affectedTable.draw();
                $('#reload-product-btn').show();
                $('#billing-table').show();
                $('#reload-product-spinner-btn').hide();
            }
        });
    });

    var billingEditor = new $.fn.dataTable.Editor( {
        ajax: {
            edit: {
                type: "PUT",
                url:  "/configuration/products/{id}",
                contentType: 'application/json',
                accept: 'application/json',
                dataType: "json",
                data: function ( d ) {
                    const keys = Object.keys(d['data']);
                    var jsonBody = [];
                    keys.forEach(key => {
                        jsonBody.push(
                            {
                                'site': d['data'][key]["site"],
                                'product': d['data'][key]["product"],
                                'plan': d['data'][key]["plan"],
                                'billing_cycle': d['data'][key]["billing_cycle"],
                                'next_billing': d['data'][key]["next_billing"],
                            }
                        );
                    });
                    return JSON.stringify( jsonBody );
                },
                success: function ( d ) {
                    let affectedTable = $('#billing-table').DataTable();
                    affectedTable.draw();
                },
            },
            remove: {
                type: "DELETE",
                url:  "/configuration/products/{id}",
                success: function ( d ) {
                    let affectedTable = $('#billing-table').DataTable();
                    affectedTable.draw();
                },
            },
        },
        table: "#billing-table",
        idSrc:  'id',
        fields: [ {
                label: "Site:",
                name: "site"
            }, {
                label: "Product:",
                name: "product",
            }, {
                label: "Plan:",
                name: "plan",
                type:  "select",
                options: [
                    { label: "", value: null },
                    { label: "Free", value: 'free' },
                    { label: "Standard",  value: 'standard' },
                    { label: "Premium",  value: 'premium' },
                ]
            }, {
                label: "Billing Cycle:",
                name: "billing_cycle",
                type:  "select",
                options: [
                    { label: "", value: null },
                    { label: "Monthly", value: 30 },
                    { label: "Yearly",  value: 365 }
                ]
            }, {
                label: "Next Bill Date:",
                name: "next_billing",
                type:  'datetime',
                def:   function () { return new Date(); }
            }
        ]
    } );

    $('#billing-table').on( 'click', 'tbody td.row-edit', function (e) {
        billingEditor.inline( billingTable.cells(this.parentNode, '*').nodes(), {
            onBlur: 'submit'
        } );
    });

    $('#billing-table').on( 'click', 'tbody td.row-remove', function (e) {
        billingEditor.remove( this.parentNode, {
            title: 'Delete record',
            message: 'Are you sure you wish to delete this record?',
            buttons: 'Delete'
        } );
    } );

    var billingTable = $('#billing-table').DataTable({
        dom: 'rt<"row"<"col-6"i>>',
        ajax: {
            url: "/configuration/products",
        },
        columns: [
            {
                data: null,
                defaultContent: '<i class="fa fa-pencil"/>',
                className: 'row-edit dt-center',
                orderable: false
            },
            { data: "site",
               editable: false},
            { data: "product" },
            { data: "plan" },
            { data: "billing_cycle" },
            { data: "next_billing" },
            {
                data: null,
                defaultContent: '<i class="fa fa-trash"/>',
                className: 'row-remove dt-center',
                orderable: false
            },

        ],
        select: false,
        buttons: [
            { extend: "edit",   editor: billingEditor },
            { extend: "remove", editor: billingEditor }
        ]
    });

});