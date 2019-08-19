(function(st, et){
    window.st = st;
    window.et = et;
    var gwXHR = window.XMLHttpRequest;
    var gwXHRProto = window.XMLHttpRequest.prototype;
    var gwXHRProtoSend = window.XMLHttpRequest.prototype.send;
    var gwXHRProtoOpen = window.XMLHttpRequest.prototype.open;

    if(!window.initOnce) {
        window.initOnce = true;

        Object.defineProperty(window, 'XMLHttpRequest', {
            enumerable: true,
            configurable: true,
            get: function(){
                return function(){
                    var gwXHRIns = null;
                    console.log('get XMLHttpRequest');
                    gwXHRIns = new gwXHR();

                    var islist=false;
                    gwXHRIns.open = function(){
                        var requrl = arguments[1];
                        if(/v2\/data\/Q\/plan\/list/i.test(requrl) || /v2\/data\/Q\/plan/i.test(requrl)) {
                            islist = true;
                        }
                        gwXHRProtoOpen.apply(this, arguments);
                    };

                    gwXHRIns.send = function(){
                        if(islist) {
                            var postdata = arguments[0];
                            postdata = decodeURIComponent(postdata);
                            postdata = postdata.replace(/^(beginTime=)([^\&]*)(\&endTime=)([^\&]*)(.*)$/i, function(m, m1, m2, m3, m4, m5){ 
                                return m1+(window.st.replace(/\//ig,''))+m3+(window.et.replace(/\//ig,''))+m5; 
                            });
                            gwXHRProtoSend.apply(this, [postdata]);
                        } else 
                            gwXHRProtoSend.apply(this, arguments);
                    };
                    
                    return gwXHRIns;
                };
            }
        });
    }


    setTimeout(function(){
        document.querySelector('.v2-picker-trigger').innerText = st + ' - ' +et;
        document.querySelector('.downTableBtn').click();
    }, 300);
 })('%s', '%s');
