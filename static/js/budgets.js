
function updateIncome() {

    // /year_income/<string:year_income>
    var year_income = document.getElementById("yearIncomeBox").value;
    alert("new year_income: " + year_income)
    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/year_income/" + year_income;

    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Updated Income to: $" + year_income)
        location.reload();
    }
}

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
        url = "http://inherentvice.pythonanywhere.com/site/transactions/" + month + "/" + year + "/" + category;
    } else {
        year = parts[1];
        url = "http://inherentvice.pythonanywhere.com/site/transactions/" + "ALL" + "/" + year + "/" + category;
    }
    window.open(url);
}