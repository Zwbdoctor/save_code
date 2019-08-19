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
                        if(/qimengnew\/recallReport\/list/i.test(requrl)) {
                            requrl = requrl.replace(/^(.*)(startDate=)([^\&]*)(\&endDate=)([^\&]*)(.*)$/i, function(m, m1, m2, m3, m4, m5, m6){ 
                                return m1+m2+(window.st.replace(/\//ig,''))+m4+(window.et.replace(/\//ig,''))+m6; 
                            });
                            //requrl = requrl.replace(/^(.*)(startDate=)([^\&]*)(\&endDate=)([^\&]*)(&platForm=)([^\&]*)(&codeIds=)([^\&]*)(.*)$/i, function(a, a1, a2, a3, a4, a5, a6, a7, a8, a9, a0){
                            //    return a1 + a2+ (window.st.replace(/\//ig,'')) + a4 + (window.et.replace(/\//ig,'')) + a6 +'platform' + a8 + 'codeIds' + a0
                            //});
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
        document.querySelectorAll('.el-range-input')[0].value=st;
        document.querySelectorAll('.el-range-input')[1].value=et;
        document.querySelector('.el-button--primary').click();
    }, 300);
 })('%s', '%s');