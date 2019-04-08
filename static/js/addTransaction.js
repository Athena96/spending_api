
function formatSingleDigit(digit) {
    if (digit < 10) {
        return "0"+digit;
    } else {
        return ""+digit;
    }
}

function addTransaction() {

    var title = document.getElementById("titleTextBox").value;
    var amount = document.getElementById("amountTextBox").value;
    //var category = document.getElementById("categoryTextBox").value;
    var category = document.getElementById("mySelectCategory").value;
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

    var data = null;
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function () {
        if (this.readyState === 4) {
            console.log(this.responseText);
        }
    });

    var url_tmp = "http://inherentvice.pythonanywhere.com/" + title + "/" + amount + "/" + category + "/" + date + "/" + note;
    var url = url_tmp.replace(" ", "%20");

    xhr.open("POST", url);
    xhr.setRequestHeader("Authorization", ("Basic " + btoa(passcode)));
    xhr.setRequestHeader("cache-control", "no-cache");
    xhr.send(data);

    // var settings = {
    //     "async": true,
    //     "crossDomain": true,
    //     "url": "http://inherentvice.pythonanywhere.com/NEW2/0.0/test/2019-03-20%2020:20:00/this%20is%20not%20null",
    //     "method": "POST",
    //     "headers": {
    //     "Authorization": "Basic ",
    //     "cache-control": "no-cache",
    //     }
    // }

    // $.ajax(settings).done(function (response) {
    //     console.log(response);
    // });
}

function updateTransaction(transaction_id) {
    var title = document.getElementById("titleTextBoxU").value;
    var amount = document.getElementById("amountTextBoxU").value;
    var category = document.getElementById("mySelectCategoryU").value;
    var date = document.getElementById("dateTextBoxU").value;
    var note = document.getElementById("noteTextBoxU").value;
    if (note == "" || note == null) {
        note = "--";
    }
    var passcode = document.getElementById("passcodeTextBoxU").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/" + transaction_id + "/" + title + "/" + amount + "/" + category + "/" + date + "/" + note;
    var url = url_tmp.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("PUT", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));
    xhr.send(JSON.stringify({

    }));

    // xhr.onload = function() {
    //     console.log("Updated Transaction")
    //     console.log(this.responseText);
    //     location.reload();
    //     alert(this.responseText);
    // }
}