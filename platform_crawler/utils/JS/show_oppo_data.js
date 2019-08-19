
(function(json, type) {
    // var json =JSON.parse(data);
    if (json.code == 1001) {
        var result = json.data;
        var html = '';

        var curDt = null;
        var curExposeNum = null;
        var curDownNum = null;
        var curCost = null;

        for (var i = 0; i < result.length; i++) {

            curDt = parseInt(json.data[i].dt);
            curExposeNum = result[i].exposeNum;
            curDownNum = result[i].downNum;
            curCost = result[i].cost;

            html += '<tr class="tolist">';
            html += '<td class="col_date">'+ curDt + '</td>';
            if(type!=1){
                if(type!=2){
                    html += '<td class="col_ad">' + result[i].moduleName+ '</td>';
                }
                html += '<td class="col_application">'+ result[i].appName + '</td>';
            }
            html += '<td class="col_viewcount">'+ curExposeNum + '</td>';
            html += '<td class="col_download">'+ curDownNum + '</td>';
            html += '<td class="col_download1">'+ result[i].ctr + '%</td>';
            html += '<td class="col_xiaofei">'+ curCost + '</td>';
            html += '<td class="col_download2">'+ result[i].price + '</td>';
            html += '<td class="col_ecpm">'+ result[i].ecpm + '</td>';
            html += '</tr>';
        }
        $("#t1").empty();
        $("#t1").append(html);
    }
})