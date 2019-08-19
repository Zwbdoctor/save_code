//拦截请求，扩大每页条数； 方便截图  同时直接获取请求数据
//http://channel.360.cn/frontend/data/index?app_id=4&start_date=2018-10-06&end_date=2018-10-15&is_detail=true&sub_channel_id=540265  get请求

(function(st, et){
    window.st = st;    //因为第一次执行已经形成闭包，之后执行都不会形成闭包，所以第一次传递的参数会被永久保存，不可以修改。需要用全局属性暴露出来
    window.et = et;
    if(!window.gwXHRProtoOpen) {
        window.gwXHRProtoOpen = window.XMLHttpRequest.prototype.open;
        window.gwXHRProtoSend = window.XMLHttpRequest.prototype.send;
        
        Object.defineProperty(XMLHttpRequest.prototype, 'open', {
            enumerable: true,
            configurable: true,
            get: function(){
                return function(){
                    this._url = arguments[1];       //将请求url手动加到XMLHttpRequest上

                    if(/frontend\/data\/index/i.test(this._url) && !/has$/i.test(this._url)) {
                        console.log('open :', arguments);
                        var temp = arguments[1];
                        temp = temp.replace(/^(.*start_date=)([^\&]*)(&end_date=)([^\&]*)(.*)/i, function(m,m1,m2,m3,m4,m5){
                            return m1+ window.st +m3+ window.et +m5
                        });
                        temp += '&has'
                        arguments[1] = temp;
                        gwXHRProtoOpen.apply(this, arguments);

                        var _this = this;
                        var inter = setInterval(function(){
                            window.datasave = _this.responseText;
                            console.log(_this.responseText);
                            clearInterval(inter);
                        },500);
                    } else {
                        gwXHRProtoOpen.apply(this, arguments);
                    }
                }
            }
        });       
    }

    //触发发送请求
    console.log('参数：', st, et);
    document.querySelector('input[name="start_date"]').value = window.st;
    document.querySelector('input[name="end_date"]').value = window.et;
    document.querySelector('.well form>button').click();


})('%(datest)s', '%(dateet)s');
