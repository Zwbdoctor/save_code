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

                    var isVerifyReq = false;
                    gwXHRIns.open = function(){
                        var requrl = arguments[1];
                        if(/api\/report\/planreport/i.test(requrl)) {
                            isVerifyReq = true;
                        }
                        gwXHRProtoOpen.apply(gwXHRIns, arguments);
                    };

                    gwXHRIns.send = function(){
                        if(isVerifyReq) {
                            console.log('now replace');
                            var postdata = arguments[0];
                            postdata = decodeURIComponent(postdata);
                            postdata = postdata.replace(/(range\"\:\")([^\"]*)/i, function(m, m1,m2){
                               return 'start":"' + window.st + '","end":"' + window.et;
                            });
                            console.log(postdata);
                            gwXHRProtoSend.apply(gwXHRIns, [postdata]);
                        } else
                            gwXHRProtoSend.apply(gwXHRIns, arguments);
                    };

                    return gwXHRIns;
                };
            }
        });
    }


    setTimeout(function(){
        document.querySelector('#dLabel span').textContent = '%s-%s'
		document.querySelector('#query').click()
    }, 200);
 })('%s', '%s')