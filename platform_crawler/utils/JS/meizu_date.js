(function(st, et){
    var gwXHR = window.XMLHttpRequest;
    var gwXHRProtoOpen = window.XMLHttpRequest.prototype.open;
    Object.defineProperty(window, 'XMLHttpRequest', {
        enumerable: true,
        configurable: true,
        get: function(){
            return function() {
                var gwXHRIns = null;
                console.log('get XMLHttpRequest');
                gwXHRIns = new gwXHR();
                gwXHRIns.open = function(){
                    var requrl = arguments[1];
                    var newurl;
                    // console.log(requrl)
                    if(/console\/sponsor\/stat\/user/i.test(requrl) && !/.*hashandle=1$/i.test(requrl)) {
                        newurl = requrl.replace(/^(.*start_time=)([^&]*)(&end_time=)([^&]*)(.*)$/i, function(m, m1, m2, m3, m4, m5){
                            return m1+st+m3+et+m5;
                        });
                        arguments[1] = newurl + (newurl.indexOf('?')==-1 ? '?hashandle=1' : '&hashandle=1');
                        console.log('replace newurl:', newurl);
                    }
                    gwXHRProtoOpen.apply(gwXHRIns, arguments);
                };
                return gwXHRIns;
            }
        }
    });

    document.querySelector('.search .datepicker input').value = st+' ~ '+et;
    document.querySelector('.search .el-button').click();
})("%s", "%s");