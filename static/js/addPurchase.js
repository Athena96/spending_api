function addPurchase() {

    var item = document.getElementById("itemTextBox").value;
    var price = document.getElementById("priceTextBox").value;
    var category = document.getElementById("categoryTextBox").value;
    var date = document.getElementById("dateTextBox").value;
    var note = document.getElementById("noteTextBox").value;
    var passcode = document.getElementById("passcodeTextBox").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = "http://inherentvice.pythonanywhere.com/" + item + "/" + price + "/" + category + "/" + date + "/" + note;
    var url = url_tmp.replace(" ", "%20");

    xhr.withCredentials = true;
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));

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
    var passcode = document.getElementById("passcodeTextBox").value;

    xhr.withCredentials = true;
    xhr.open("PUT", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader("Authorization", "Basic " + btoa(passcode));
    xhr.send(JSON.stringify({

    }));

    xhr.onload = function() {
        console.log("Updated Purchase")
        console.log(this.responseText);
        location.reload();
        alert(this.responseText);
    }
}