
(function(json, type) {
    // var json =JSON.parse(data);
    if (json.code == 1001) {
        var result = json.data;
        var html = '';

        for (var i = 0; i < result.length; i++) {

            html += '<tr class="tolist">';
            html += '<td class="col_date">'+ result[i].time + '</td>';
            html += '<td class="col_viewcount">'+ result[i].exposeNum + '</td>';
            html += '<td class="col_download">'+ result[i].clickNum + '</td>';
            html += '<td>' + result[i].downClickNum + '</td>';
            html += '<td class="col_download1">'
                    + (result[i].exposeNum == 0 ? "0.00": (result[i].clickNum/ result[i].exposeNum * 100).toFixed(2)) + '%</td>';
            html += '<td class="col_xiaofei">'+ (result[i].income/100) + '</td>';
            html += '<td class="col_download2">'+ (result[i].clickNum == 0 ? "0.00": (result[i].income/100 / result[i].clickNum).toFixed(2)) + '</td>';
            html += '<td class="col_ecpm">'+ (result[i].exposeNum == 0 ? "0.00": (result[i].income/100 / result[i].exposeNum * 1000).toFixed(2)) + '</td>';
            html += '</tr>';
        }
        $("#t1").empty();
        $("#t1").append(html);
    }
})