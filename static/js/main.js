$(document).ready(function() {
    function getLiveReading() {
        $.ajax({
            url: "/latest",
            cache: false
        })
        .done(function(data) {
            if (data) {
                tds = $("#live-data").children("td");
                tds.eq(0).text(data["value"] + " cm");
                md = moment(data["timestamp"] * 1000)
                tds.eq(1).text(md.format("MMM D, YYYY h:mm:ss A"));
            }
        });
    }

    getLiveReading();
    setInterval(getLiveReading, 2000);
});