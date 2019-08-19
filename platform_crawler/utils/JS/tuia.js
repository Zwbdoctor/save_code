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
                        console.log('====before change==========requrl:', requrl);
                        if(/advert\/queryAdvertData/i.test(requrl)) {
                            requrl = requrl.replace(/^(.*)(startDate=)([^\&]*)(\&endDate=)([^\&]*)(.*)$/i, function(m, m1, m2, m3, m4, m5, m6){
                                return m1+m2+(window.st)+m4+(window.et)+m6;
                            });
                            arguments[1] = requrl;
                            console.log('====after change==========requrl:', requrl);
                            setTimeout(function(){
                                document.querySelector('input[placeholder="开始日期"]').value = window.st;
                                document.querySelector('input[placeholder="结束日期"]').value = window.et;
                            }, 500);
                        }
                        gwXHRProtoOpen.apply(this, arguments);
                    };

                    return gwXHRIns;
                };
            }
        });
    }


    setTimeout(function(){
        document.querySelector('.search-btn').click();
    }, 100);
 })('%s', '%s');