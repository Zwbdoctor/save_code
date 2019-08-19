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
                        if(/dspsrv\/httpapi\/fetch_billing_account_details/i.test(requrl)) {
                            isVerifyReq = true;
                        }
                        gwXHRProtoOpen.apply(gwXHRIns, arguments);
                    };

                    gwXHRIns.send = function(){
                        if(isVerifyReq) {
                            console.log('now replace');
                            var postdata = arguments[0];
                            postdata = decodeURIComponent(postdata);
                            postdata = postdata.replace(/^(\{\"start_date\"\:\")([^\"]*)(\",\"end_date\"\:\")([^\"]*)(.*)$/i, function(m, m1, m2, m3, m4, m5){
                               return m1+window.st+m3+window.et+m5;
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
        document.querySelector('div[title="天"]').click();
        document.querySelector('ul[role="listbox"] li:nth-child(1)').click();
        document.querySelector('.ant-calendar-picker-input').innerHTML = '&emsp;&emsp;&emsp;'+window.st+'&emsp;~&emsp;'+window.et+'&emsp;&emsp;&emsp;';
    }, 200);
 })('%s', '%s');