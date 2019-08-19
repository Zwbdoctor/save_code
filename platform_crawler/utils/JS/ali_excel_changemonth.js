(function(year, month){
    window.onceFlag = false;
    if(!window.onceFlag) {
        var gwXHR = window.XMLHttpRequest;
        var gwXHRProto = window.XMLHttpRequest.prototype;
        var gwXHRProtoOpen = window.XMLHttpRequest.prototype.open;
        window.onceFlag = true;

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
                        if(/member\/balance\/history/i.test(requrl) && !/has$/i.test(this.requrl)) {
                            console.log('islist true');
                            islist = true;
                            requrl = requrl.replace(/^(.*year=)([^\&]*)(&month=)([^\&]*)(.*)/i, function(m,m1,m2,m3,m4,m5){
                                return m1+ year + m3 + month +m5
                            });
                            requrl += '&has'
                            arguments[1] = requrl;
                            gwXHRProtoOpen.apply(this, arguments);

                        } else
                            gwXHRProtoOpen.apply(this, arguments);
                    };
                    return gwXHRIns;
                };
            }
        });
    }

    document.querySelector('.ant-calendar-picker input').click();
    document.querySelector('.ant-calendar-picker input').value = year + '-' + (month<10 ? '0'+month : month);
    setTimeout(function(){
        document.querySelector('.ant-calendar-month-panel-month').click();
    }, 300);
})('%(year)s', '%(month)s');
