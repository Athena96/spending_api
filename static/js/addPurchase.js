function addPurchase() {

    var item = document.getElementById("itemTextBox").value;
    var price = document.getElementById("priceTextBox").value;
    var category = document.getElementById("categoryTextBox").value;
    var date = document.getElementById("dateTextBox").value;
    var note = document.getElementById("noteTextBox").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/" + item + "/" + price + "/" + category + "/" + date + "/" + note;
    var url = url_tmp.replace(" ", "%20");


    var usrNmPwd;
    var entry = prompt("Please enter the password:", "here");

    if (entry == null || entry == "") {
        usrNmPwd = "User cancelled the prompt.";
        location.reload();
        return;
    } else {
        usrNmPwd = entry;
    }
    xhr.withCredentials = true;
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(usrNmPwd));

    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Added Purchase");
        console.log(this.responseText);
        location.reload();
        alert(this.responseText);
    }
}

function updatePurchase(purchase_id) {
    var item = document.getElementById("itemTextBoxU").value;
    var price = document.getElementById("priceTextBoxU").value;
    var category = document.getElementById("categoryTextBoxU").value;
    var date = document.getElementById("dateTextBoxU").value;
    var note = document.getElementById("noteTextBoxU").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/" + purchase_id + "/" + item + "/" + price + "/" + category + "/" + date + "/" + note;
    var url = url_tmp.replace(" ", "%20");

    var usrNmPwd;
    var entry = prompt("Please enter the password:", "here");

    if (entry == null || entry == "") {
        usrNmPwd = "User cancelled the prompt.";
    } else {
        usrNmPwd = entry;
    }
    xhr.withCredentials = true;
    xhr.open("PUT", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(usrNmPwd));
    xhr.send(JSON.stringify({

    }));

    xhr.onload = function() {
        console.log("Updated Purchase")
        console.log(this.responseText);
        location.reload();
        alert(this.responseText);
    }
}