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