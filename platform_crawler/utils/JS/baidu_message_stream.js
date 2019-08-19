(function(st, et){
    var gwXHR = window.XMLHttpRequest;
    var gwXHRProtoSend = window.XMLHttpRequest.prototype.send;
    var gwXHRProtoOpen = window.XMLHttpRequest.prototype.open;
    Object.defineProperty(window, 'XMLHttpRequest', {
        enumerable: true,
        configurable: true,
        get: function(){
            return function() {
                var gwXHRIns = null;
                console.log('get XMLHttpRequest');
                gwXHRIns = new gwXHR();

                var isVerifyReq = false;
                gwXHRIns.open = function(){
                    var requrl = arguments[1];
                    if(/request.ajax\?path=pluto\/GET\/mars\/reportdata/i.test(requrl)) {
                        isVerifyReq = true;
                    }
                    gwXHRProtoOpen.apply(gwXHRIns, arguments);
                };

                gwXHRIns.send = function(){
                    if(isVerifyReq) {
                        console.log('now replace');
                        var postdata = arguments[0];
                        postdata = decodeURIComponent(postdata);
                        postdata = postdata.replace(/^(.*pageSize\"\:)([^,]*)(.*starttime\"\:\")([^\"]*)(\",\"endtime\"\:\")([^\"]*)(.*)$/i, function(m, m1, m2, m3, m4, m5, m6,m7){ 
                            return m1+100+m3+st+m5+et+m7; 
                        });
                        gwXHRProtoSend.apply(gwXHRIns, [postdata]);
                    } else 
                        gwXHRProtoSend.apply(gwXHRIns, arguments);
                };
                
                return gwXHRIns;
            }
        }
    });

    document.querySelector('.time-dim-day').click();
    setTimeout(function(){
        document.querySelector('.feed-report-filter-header-label-container').innerText = st+' - '+et;
    }, 300);
})('%(datest)s', '%(dateet)s');