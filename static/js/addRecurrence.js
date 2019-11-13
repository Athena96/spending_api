

function deleteRecurrence(recurrence_id) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/recurrence/" + recurrence_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Deleted Recurrence Category");
        location.reload();
        alert(this.responseText);
    }
}

function addRecurrence() {
    var name = document.getElementById("nameTextBox").value;
    var amount = document.getElementById("amountTextBox").value;
    var recType = document.getElementById("recTypeTextBox").value;
    var startDate = document.getElementById("startDateTextBox").value;
    var endDate = document.getElementById("endDateTextBox").value;
    var daysTillRepeat = document.getElementById("daysTillRepeatTextBox").value;
    if (daysTillRepeat == "" || daysTillRepeat == null || daysTillRepeat == " ") {
        daysTillRepeat = null;
    }
    var dayOfMonth = document.getElementById("dayOfMonthTextBox").value;
    if (dayOfMonth == "" || dayOfMonth == null || dayOfMonth == " ") {
        dayOfMonth = null;
    }

    var description = document.getElementById("descriptionTextBox").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }

    var xhr = new XMLHttpRequest();
    var url_tmp = prefix + "/recurrence/" + name + "/" + amount + "/" + description + "/" + recType + "/" + startDate + "/" + endDate  + "/" + daysTillRepeat + "/" + dayOfMonth;
    var url = url_tmp.replace(" ", "%20");
    console.log(url_tmp);
    if (prefix == "http://inherentvice.pythonanywhere.com") {
        console.log("A");
        var passcode = document.getElementById("passcodeTextBox").value;
        xhr.withCredentials = true;
        xhr.open("POST", url);
        xhr.setRequestHeader("Authorization", ("Basic " + btoa(passcode)));
    } else {
        console.log("B");
        xhr.open("POST", url);
    }

    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
}

function updateRecurrence(recurrence_id) {
    var name = document.getElementById("nameTextBoxU").value;
    var amount = document.getElementById("amountTextBoxU").value;
    var recType = document.getElementById("recTypeTextBoxU").value;
    var startDate = document.getElementById("startDateTextBoxU").value;
    var endDate = document.getElementById("endDateTextBoxU").value;
    var daysTillRepeat = document.getElementById("daysTillRepeatTextBoxU").value;
    if (daysTillRepeat == "" || daysTillRepeat == null || daysTillRepeat == " ") {
        daysTillRepeat = null;
    }
    var dayOfMonth = document.getElementById("dayOfMonthTextBoxU").value;
    if (dayOfMonth == "" || dayOfMonth == null || dayOfMonth == " ") {
        dayOfMonth = null;
    }
    var description = document.getElementById("descriptionTextBoxU").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }

    var xhr = new XMLHttpRequest();
    var url_w_spc = prefix + "/recurrence/" + recurrence_id + "/" + name + "/" + amount + "/" + description + "/" + recType + "/" + startDate + "/" + endDate  + "/" + daysTillRepeat + "/" + dayOfMonth;
    var url = url_w_spc.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("PUT", url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    if (prefix == "http://inherentvice.pythonanywhere.com") {
        xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));
    }

    xhr.send(JSON.stringify({}));
}
