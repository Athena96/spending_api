

function openUpdatePage(budget_id) {
    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/site/add_budget/" + budget_id;
    window.open(url);
}

function deleteBudget(budget_id) {

    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/budget/" + budget_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Deleted Budget Category")
        console.log(this.responseText);
        location.reload();
        alert(this.responseText);
    }
}

function openPurhcasesPage(info) {

    var parts = info.split("#");
    var category = parts[1];
    var month = "";
    var year = "";

    var xhr = new XMLHttpRequest();
    var url = "";
    var title = parts[0];

    if (title == "month_year") {
        month = parts[2];
        year = parts[3];
        // .../year:2019/month:04                   all txns for april 2019
        // .../year:2019/month:04/category:grocery  all grocery txns for april 2019
        // .../year:2019                            all txns for 2019
        // .../year:2019/category:grocery           all grocery txns for 2019

        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/year:" + year + "/month:" + month + "/category:" + category;
    } else if (title == "year") {
        year = parts[2];
        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/year:" + year + "/category:" + category;
    } else if (title == "special") {
        var special_category = parts[1];
        var special_frequency = parts[2];
        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/special_category:" + special_category + "/special_frequency:" + special_frequency;
    }
    window.open(url);
}