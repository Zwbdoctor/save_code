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
                        console.log('==============requrl:', requrl);
                        if(/overture\/cash\/get_cash_flow/i.test(requrl)) {
                            requrl = requrl.replace(/^(.*)(start_date=)([^\&]*)(\&end_date=)([^\&]*)(.*)$/i, function(m, m1, m2, m3, m4, m5, m6){
                                return m1+m2+(window.st)+m4+(window.et)+m6;
                            });
                            arguments[1] = requrl;
                            console.log(arguments);
                        }
                        gwXHRProtoOpen.apply(this, arguments);
                    };
                    return gwXHRIns;
                };
            }
        });
    }


    setTimeout(function(){
        document.querySelector('#cash-cashflow-date span').innerHTML = window.st + '&nbsp;至&nbsp;' + window.et
        document.querySelector('.summary-item span').innerHTML = window.st + '&nbsp;至&nbsp;' + window.et
        document.querySelector('button.byted-btn.byted-btn-primary span').click();
    }, 300);
 })('%s', '%s');