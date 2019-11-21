

function openUpdatePage(recurrence_id) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/site/add_recurrence/" + recurrence_id;
    window.open(url);
}

function deleteRecurrence(recurrence_id) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/recurrence/" + recurrence_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({}));
    xhr.onload = function() {
        console.log("Deleted Recurrence Category");
        location.reload();
        alert(this.responseText);
    }
}
