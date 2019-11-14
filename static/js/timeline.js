function setStartingBal() {
    var startingBal = document.getElementById("startingBalTxtBox").value;

    var xhr = new XMLHttpRequest();
    var url_tmp = prefix + "/timeline/" + startingBal;
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
    window.open('timeline');
}
