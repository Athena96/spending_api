

function addTransaction() {
    var title = document.getElementById("titleTextBox").value;
    var category = document.getElementById("mySelectCategory").value;
    var final_cat = category;

    var amount = document.getElementById("amountTextBox").value;
    var varTxnTrackingCode = document.getElementById("paymentMethod").value;
    if (varTxnTrackingCode == "" || varTxnTrackingCode == null || varTxnTrackingCode == " ") {
        varTxnTrackingCode = null;
    }

    var transactionType = document.getElementById("transactionTypeTextBox").value;
    if (transactionType == "" || transactionType == null || transactionType == " ") {
        transactionType = null;
    }



    var date = document.getElementById("dateTextBox").value;
    if (date == "" || date == null) {
        var currentDate = new Date();
        var sec = formatSingleDigit(currentDate.getSeconds());
        var min = formatSingleDigit(currentDate.getMinutes());
        var hour = formatSingleDigit(currentDate.getHours());
        var day = formatSingleDigit(currentDate.getDate());
        var month = formatSingleDigit((currentDate.getMonth() + 1));
        var year = currentDate.getFullYear();
        date = year + "-" + month + "-" + day + " " + hour + ":" + min + ":" + sec;
    }
    var description = document.getElementById("descriptionTextBox").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    } else {
        description = description.replace("/", "-");
    }

    var xhr = new XMLHttpRequest();
    var url_tmp = prefix + "/transactions/" + title + "/" + amount + "/" + final_cat + "/" + date + "/" + description + "/" + varTxnTrackingCode + "/" + transactionType;
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

    xhr.setRequestHeader("cache-control", "no-cache");
    xhr.send(JSON.stringify({}));
    window.open('transactions');
}

function updateTransaction(transaction_id) {

    var title = document.getElementById("titleTextBoxU").value;
    var amount = document.getElementById("amountTextBoxU").value;
    var varTxnTrackingCode = document.getElementById("paymentMethodU").value;
    if (varTxnTrackingCode == "" || varTxnTrackingCode == null || varTxnTrackingCode == " ") {
        varTxnTrackingCode = null;
    }

    var transactionType = document.getElementById("transactionTypeTextBoxU").value;
    if (transactionType == "" || transactionType == null || transactionType == " ") {
        transactionType = null;
    }

    var category = document.getElementById("mySelectCategoryU").value;
    var date = document.getElementById("dateTextBoxU").value;
    var description = document.getElementById("descriptionTextBoxU").value;
    if (description == "" || description == null || description == " ") {
        description = null;
    } else {
        description = description.replace("/", "-");
    }
    var passcode = document.getElementById("passcodeTextBoxU").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = prefix + "/transactions/" + transaction_id + "/" + title + "/" + amount + "/" + category + "/" + date + "/" + description + "/" + varTxnTrackingCode + "/" + transactionType;
    var url = url_tmp.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("PUT", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    if (prefix == "http://inherentvice.pythonanywhere.com") {
        xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));
    }
    xhr.send(JSON.stringify({}));
}

function formatSingleDigit(digit) {
    if (digit < 10) {
        return "0"+digit;
    } else {
        return ""+digit;
    }
}
