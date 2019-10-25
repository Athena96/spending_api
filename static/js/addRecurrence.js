

function deleteRecurrence(recurrence_id) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/recurrences/" + recurrence_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Deleted Recurrence Category")
        location.reload();
        alert(this.responseText);
    }
}

function addRecurrence() {
    var category = document.getElementById("categoryTextBox").value;
    var amount = document.getElementById("amountTextBox").value;
    var amountFrequencies = document.getElementsByName("amountFrequencyRadioButtons");
    var selectedAmountFrequency;
    for(var i = 0; i < amountFrequencies.length; i++) {
        if(amountFrequencies[i].checked)
            selectedAmountFrequency = amountFrequencies[i].value;
    }
    alert(selectedAmountFrequency)
    var startDate = document.getElementById("startDateTextBox").value;
    var endDate = document.getElementById("endDateTextBox").value;

    var description = document.getElementById("descriptionTextBox").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }

    var xhr = new XMLHttpRequest();
    var url_tmp = prefix + "/recurrences/" + category + "/" + amount + "/" + selectedAmountFrequency + "/" + description + "/" + startDate + "/" + endDate;
    var url = url_tmp.replace(" ", "%20");

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
    var category = document.getElementById("categoryTextBoxU").value;
    var amount = document.getElementById("amountTextBoxU").value;
    var amountFrequencies = document.getElementsByName("amountFrequencyRadioButtonsU");
    var selectedAmountFrequency;
    for(var i = 0; i < amountFrequencies.length; i++) {
        if(amountFrequencies[i].checked)
            selectedAmountFrequency = amountFrequencies[i].value;
    }    var startDate = document.getElementById("startDateTextBoxU").value;
    var endDate = document.getElementById("endDateTextBoxU").value;

    var description = document.getElementById("descriptionTextBoxU").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }

    var xhr = new XMLHttpRequest();
    var url_w_spc = prefix + "/recurrences/" + recurrence_id + "/" + category + "/" + amount + "/" + amountFrequency + "/" + description + "/" + startDate + "/" + endDate;
    var url = url_w_spc.replace(" ", "%20");

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

    xhr.setRequestHeader("cache-control", "no-cache");
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
}
