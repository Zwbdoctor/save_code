
(function(){
    function ensureEle(tag, succCall){          //轮询查找
        succCall = succCall || function(){};
        var bo = document.querySelector(tag);
        var latecy = 0, timer;
        if(!!bo) 
            latecy = 0;
        else
            latecy = 500;
        function insertDom(){
            clearTimeout(timer);
            timer = setTimeout(function(){
                bo = document.querySelector(tag);
                if(!bo){
                    insertDom();
                    return;
                }
                succCall(bo);
            }, latecy);
        }
        insertDom();
    }

    ensureEle('.gdt-mask', function(ele){
        ele.remove();
    });
    ensureEle('#__gdt_greenhand', function(ele){        //e.qq 完善资料
        ele.remove();
    });
})();
