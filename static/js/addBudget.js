
function addBudget() {
  // for adding budgets under a parent budget.
  // e.g.
  // add grocery: start=jan 1 2019 end = dec 31 2019
  // update grocery: start=jan 1 2019 end = jun 01 2019
  // add grocery: start=jun 02 2019 end = dec 31 2019

    var category = document.getElementById("categoryTextBox").value;
    var amount = document.getElementById("amountTextBox").value;
    var amountFrequency = document.getElementById("amountFrequencyTextBox").value;
    var startDate = document.getElementById("startDateTextBox").value;
    var endDate = document.getElementById("endDateTextBox").value;

    var description = document.getElementById("descriptionTextBox").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }
    var passcode = document.getElementById("passcodeTextBox").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/budget/" + category + "/" + amount + "/" + amountFrequency + "/" + description + "/" + startDate + "/" + endDate;
    var url = url_tmp.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));
    xhr.send(JSON.stringify({}));
}

function updateBudget(budget_id) {
    var category = document.getElementById("categoryTextBoxU").value;
    var amount = document.getElementById("amountTextBoxU").value;
    var amountFrequency = document.getElementById("amountFrequencyTextBoxU").value;
    var startDate = document.getElementById("startDateTextBoxU").value;
    var endDate = document.getElementById("endDateTextBoxU").value;

    var description = document.getElementById("descriptionTextBoxU").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }
    var passcode = document.getElementById("passcodeTextBox").value;

    var xhr = new XMLHttpRequest();
    var url_w_spc = "http://inherentvice.pythonanywhere.com/budget/" + budget_id + "/" + category + "/" + amount + "/" + amountFrequency + "/" + description + "/" + startDate + "/" + endDate;
    var url = url_w_spc.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("PUT", url, true);
    xhr.setRequestHeader("cache-control", "no-cache");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));
    xhr.send(JSON.stringify({}));
}
