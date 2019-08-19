(function(st, et){
    window.onceFlag = false;
    if(!window.onceFlag) {
        var gwXHR = window.XMLHttpRequest;
        var gwXHRProto = window.XMLHttpRequest.prototype;
        var gwXHRProtoSend = window.XMLHttpRequest.prototype.send;
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

                    var ischart=false, islist=false;
                    gwXHRIns.open = function(){
                        var requrl = arguments[1];
                        if(/request\.ajax\?path=appads\/GET\/report\/all\/chart/i.test(requrl)) {
                            // console.log('����url��', requrl);
                            ischart = true;
                        }
                        if(/request\.ajax\?path=appads\/GET\/report\/all\/list/i.test(requrl)) {
                            console.log('����url��', requrl);
                            islist = true;
                        }
                        gwXHRProtoOpen.apply(this, arguments);
                    };

                    gwXHRIns.send = function(){
                        if(ischart || islist) {  //�滻���ֲ���
                            var postdata = arguments[0];
                            postdata = decodeURIComponent(postdata);
                            postdata = postdata.replace(/^(.*startDate\"\:\")([^\"]*)(\",\"endDate\"\:\")([^\"]*)(.*)$/i, function(m, m1, m2, m3, m4, m5){ 
                                return m1+st+m3+et+m5; 
                            });
                            console.log('send�����滻��', postdata);
                            gwXHRProtoSend.apply(this, [postdata]);
                        } else 
                            gwXHRProtoSend.apply(this, arguments);
                    };
                    
                    return gwXHRIns;
                };
            }
        });
    }

    document.querySelector('.el-date-editor').click();
    setTimeout(function(){
        document.querySelector('.condition-list span').click();
        var editors = document.querySelectorAll('.el-date-editor');
        editors[0].querySelector('input').value = st;
        editors[1].querySelector('input').value = et;
    }, 300);
})('%s', '%s');
