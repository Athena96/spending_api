function openUpdatePage(budget_id) {
    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/site/add_budget/" + budget_id;
    window.open(url);
}

function deleteBudget(budget_id) {

    var xhr = new XMLHttpRequest();
    var url = "http://inherentvice.pythonanywhere.com/budget/" + budget_id;
    xhr.open("DELETE", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
xhr.send(JSON.stringify({
}));
xhr.onload = function() {
  console.log("Deleted Budget Category")
  console.log(this.responseText);
  location.reload();
  alert(this.responseText);
}
}