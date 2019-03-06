function deletePurchase(purchase_id) {

    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/" + purchase_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify({

    }));

    xhr.onload = function() {
        console.log("Deleted");
        location.reload();
        alert(this.responseText);
    }
}

function openUpdatePage(purchase_id) {
    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/site/add_purchase/" + purchase_id;
    window.open(url);
}