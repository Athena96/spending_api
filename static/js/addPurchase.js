
function formatSingleDigit(digit) {
    if (digit < 10) {
        return "0"+digit;
    } else {
        return ""+digit;
    }
}

function addPurchase() {

    var item = document.getElementById("itemTextBox").value;
    var price = document.getElementById("priceTextBox").value;
    var category = document.getElementById("categoryTextBox").value;
    var date = document.getElementById("dateTextBox").value;
    if (date == "" || date == null) {
        var currentDate = new Date();

        var sec = formatSingleDigit(currentDate.getSeconds());
        var min = formatSingleDigit(currentDate.getMinutes());
        var hour = formatSingleDigit(currentDate.getHours());
        var date = formatSingleDigit(currentDate.getDate());
        var month = formatSingleDigit((currentDate.getMonth() + 1));
        var year = currentDate.getFullYear();
        date = year + "-" + month + "-" + date + " " + hour + ":" + min + ":" + sec;
    }
    var note = document.getElementById("noteTextBox").value;
    if (note == "" || note == null) {
        note = "--";
    }
    var passcode = document.getElementById("passcodeTextBox").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/" + item + "/" + price + "/" + category + "/" + date + "/" + note;
    var url = url_tmp.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));

    xhr.send(JSON.stringify({
    }));
    xhr.onload = function() {
        alert(this.responseText);
    }
}

function updatePurchase(purchase_id) {
    var item = document.getElementById("itemTextBoxU").value;
    var price = document.getElementById("priceTextBoxU").value;
    var category = document.getElementById("categoryTextBoxU").value;
    var date = document.getElementById("dateTextBoxU").value;
    var note = document.getElementById("noteTextBoxU").value;
    if (note == "" || note == null) {
        note = "--";
    }
    var passcode = document.getElementById("passcodeTextBoxU").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/" + purchase_id + "/" + item + "/" + price + "/" + category + "/" + date + "/" + note;
    var url = url_tmp.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("PUT", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));
    xhr.send(JSON.stringify({

    }));

    // xhr.onload = function() {
    //     console.log("Updated Purchase")
    //     console.log(this.responseText);
    //     location.reload();
    //     alert(this.responseText);
    // }
}