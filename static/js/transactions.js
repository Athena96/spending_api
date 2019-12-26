
function deleteTransaction(transaction_id) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/transactions/" + transaction_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Deleted Transaction");
        location.reload();
        alert(this.responseText);
    }
}

function openUpdatePage(transaction_id) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/site/add_transaction/" + transaction_id;
    window.open(url);
}

function duplicateTransaction(transaction_id) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/site/add_transaction/" + transaction_id + "/true";
    window.open(url);
}
