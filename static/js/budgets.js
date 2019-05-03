

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
    var category = parts[0];
    var month = "";
    var year = "";

    var xhr = new XMLHttpRequest();
    var url = "";


    if (parts.length == 3) {
        month = parts[1];
        year = parts[2];
        // .../year:2019/month:04                   all txns for april 2019
        // .../year:2019/month:04/category:grocery  all grocery txns for april 2019
        // .../year:2019                            all txns for 2019
        // .../year:2019/category:grocery           all grocery txns for 2019

        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/year:" + year + "/month:" + month + "/category:" + category;
    } else {
        year = parts[1];
        url = "http://inherentvice.pythonanywhere.com/site/transactions" + "/year:" + year + "/category:" + category;
    }
    window.open(url);
}