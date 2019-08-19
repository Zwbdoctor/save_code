(function(){
    let settime = Date.now();
    localStorage.setItem('list_sdate', '{"data":"2018-08-07","_time":'+settime+',"_expire":31308148}');
    localStorage.setItem('list_edate', '{"data":"2018-08-12","_time":'+settime+',"_expire":31308148}');
    location.reload();
})();