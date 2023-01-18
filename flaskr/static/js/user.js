function includeInactive(value) {
    if ('URLSearchParams' in window) {
        var searchParams = new URLSearchParams(window.location.search);
        searchParams.set("includeInactive", value);
        window.location.search = searchParams.toString();
    }
};

function hideNonBillable(value) {
    if ('URLSearchParams' in window) {
        var searchParams = new URLSearchParams(window.location.search);
        searchParams.set("includeNonBillable", value);
        window.location.search = searchParams.toString();
    }
};

function showPois(value) {
    if ('URLSearchParams' in window) {
        var searchParams = new URLSearchParams(window.location.search);
        searchParams.set("showPois", value);
        window.location.search = searchParams.toString();
    }
};

function clearFilters() {
if ('URLSearchParams' in window) {
        var searchParams = new URLSearchParams(window.location.search);
        window.location.search = '';
    }
}

function rangeFilter(value) {
    if ('URLSearchParams' in window) {
        var searchParams = new URLSearchParams(window.location.search);
        searchParams.set("daysInactive", value);
        window.location.search = searchParams.toString();
    }
}

function rangeUpdateLabel(value) {
    if (value > 366) {
        document.getElementById('rangeLabel').innerHTML = "Never logged in";
    } else if (value == 366) {
        document.getElementById('rangeLabel').innerHTML = "Idle more then 1 year";
    } else {
        const now = new Date();
        const date = new Date();
        date.setDate(now.getDate() - value);
        document.getElementById('rangeLabel').innerHTML = "Idle more than " + value + " days (" + date.toLocaleDateString("de-DE") + ")";
    }
}

/* Formatting function for row details - modify as you need */
function format(d) {

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/user/" + d + "/products", false );
    xmlHttp.send( null );
    var products = JSON.parse(xmlHttp.responseText);
    var daysInactive;
    if ('URLSearchParams' in window) {
        var searchParams = new URLSearchParams(window.location.search);
        daysInactive = searchParams.get("daysInactive");
    }
    var table = '<table class="table table-striped" border="1">' +
                    '<thead>' +
                        '<tr>' +
                            '<th scope="col"></th>' +
                            '<th scope="col">Product</th>' +
                            '<th scope="col">URL</th>' +
                            '<th scope="col">Last Activity</th>' +
                        '</tr>' +
                    '</thead>' +
                    '<tbody>';
    for (let i = 0; i < products.length; i++) {
        table += '<tr>';
        var last_active;
        if (products[i].last_active === 'Never') {
            table += '<td><i class="fa-regular fa-gem text-primary"></i></td>';
        } else {
            table += '<td></td>';
        }
            table += '<td><a href="product/' + products[i].site_id + '?name=' + products[i].name + '">' + products[i].name + '</a></td>' +
                    '<td>' + products[i].url + '</td>' +
                    '<td>' + products[i].last_active + '</td>' +
                  '</tr>';
    }
    table += '</tbody></table>';


    return table;
}

$(document).ready(function () {
    var table = $('#user-table').DataTable({
        dom: "Bfrti"
    });
    // Add event listener for opening and closing details
    $('#user-table tbody').on('click', 'td.dt-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        } else {
            // Open this row
            row.child(format(row.data()[1])).show();
            tr.addClass('shown');
        }
    });
});