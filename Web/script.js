$(document).ready(function () { // load json file using jquery ajax
//    $.getJSON('../jsonoutput.txt', function (data) {
    $.getJSON('../json2.txt', function (data) {
//    $.getJSON('data.json', function (data) {
//    $.getJSON('data.txt', function (data) {
        var output = '<ul>';
        $.each(data, function (key, val) {
            output += '<li>' + val.portfolioname + '</li>';
//            output += '<li>' + val.name + '</li>';
        });
        output += '</ul>';
        $('#update').html(output);  // replace all existing content
    });
});
