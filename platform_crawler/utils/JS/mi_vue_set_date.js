(function(st, et){
    var inp = document.querySelectorAll('.data-picker input')[1];

    var sts = st.split('/');
    var date1 = new Date(sts[0], parseInt(sts[1])-1, sts[2]);
    var ets = et.split('/');
    var date2 = new Date(ets[0], parseInt(ets[1])-1, ets[2]);

    Object.defineProperty(Function.prototype, 'apply', {
        enumerable: true,
        configurable: true,
        get: function() {
            return function(){
                if(arguments[0] == inp && arguments[1][0]['type']=='datepicker-change') {    //替换vendor c.apply(o, e)
                    arguments[1] = [
                        new Event('datepicker-change'),
                        {
                            date1: date1,
                            date2: date2,
                            value: st+" ~ "+et
                        }
                    ];
                    this.call(arguments[0], ...arguments[1]);

                } else {
                    return this.call(arguments[0], ...arguments[1])
                }
            }
        }
    });

    //随便点击今天，用来触发trigger调用流程
    inp.click();
    setTimeout(function(){
        document.querySelector('a[data-days="today"]').click()
    }, 500);

    // var event = new Event('datepicker-change');     //模拟事件触发回调，但是参数传递则通过重写apply方法实现
    // inp.dispatchEvent(event);
})