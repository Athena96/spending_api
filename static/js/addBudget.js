function addBudget() {
    var category = document.getElementById("categoryTextBox").value;
    var amount = document.getElementById("amountTextBox").value;
    var amountFrequency = document.getElementById("amountFrequencyTextBox").value;
    var description = document.getElementById("descriptionTextBox").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }

    var passcode = document.getElementById("passcodeTextBox").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/budget/" + category + "/" + amount + "/" + amountFrequency + "/" + description;
    var url = url_tmp.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));

    xhr.send(JSON.stringify({}));
    // xhr.onload = function() {
    //     console.log("Added Budget")
    //     console.log(this.responseText);
    //     location.reload();
    //     alert(this.responseText);
    // }

}

function updateBudget(budget_id) {
    var category = document.getElementById("categoryTextBoxU").value;
    var amount = document.getElementById("amountTextBoxU").value;
    var amountFrequency = document.getElementById("amountFrequencyTextBoxU").value;
    var description = document.getElementById("descriptionTextBoxU").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    }

    var passcode = document.getElementById("passcodeTextBox").value;

    var xhr = new XMLHttpRequest();
    var url_w_spc = "http://inherentvice.pythonanywhere.com/budget/" + budget_id + "/" + category + "/" + amount + "/" + amountFrequency + "/" + description;
    var url = url_w_spc.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("PUT", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));

    xhr.send(JSON.stringify({

    }));

    // xhr.onload = function() {
    //     console.log("Updated Budget")
    //     console.log(this.responseText);
    //     location.reload();
    //     alert(this.responseText);
    // }
}