function openTransactionsPage(year, month, category) {
    var xhr = new XMLHttpRequest();
    var url = prefix + "/site/transactions" + "/year:" + year + "/month:" + month + "/category:" + category;
    window.open(url);
}