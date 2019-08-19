(function(st, et){
    if(jQuery('#daterange') && 
        jQuery('#daterange').data('daterangepicker') && 
        ('setStartDate' in jQuery('#daterange').data('daterangepicker'))
    ) {
        jQuery('#daterange').data('daterangepicker').setStartDate(st);
        jQuery('#daterange').data('daterangepicker').setEndDate(et);
        document.querySelector('.applyBtn').click();

    } else {
        let settime = Date.now();
        localStorage.setItem('list_sdate', '{"data":"'+st+'","_time":'+settime+',"_expire":31308148}');
        localStorage.setItem('list_edate', '{"data":"'+et+'","_time":'+settime+',"_expire":31308148}');
        location.reload();
    }
})('2018-09-01', '2018-09-10');