
function deleteBudget(budget_id) {
    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/budget/" + budget_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Deleted Budget Category")
        location.reload();
        alert(this.responseText);
    }
}

function openUpdatePage(budget_id) {
    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/site/add_budget/" + budget_id;
    window.open(url);
}

function openPurhcasesPage(info) {
    var parts = info.split("#");
    var title = parts[0];
    var category = parts[1];
    var month = "";
    var year = "";

    var xhr = new XMLHttpRequest();
    var url = "";
    if (title == "month_year") {
        month = parts[2];
        year = parts[3];
        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/year:" + year + "/month:" + month + "/category:" + category;
    } else if (title == "year") {
        year = parts[2];
        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/year:" + year + "/category:" + category;
    } else if (title == "period") {
        var start_date = parts[1];
        var end_date = parts[2];
        var category = parts[3];
        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/start_date:" + start_date + "/end_date:" + end_date + "/category" + category;
    }
    window.open(url);
}
