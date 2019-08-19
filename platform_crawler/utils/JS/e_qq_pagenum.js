
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

    ensureEle('#_side_detail #_detail_pager select', function(ele){     //选中分页，判断是不是每页100，不是就切换
        if(ele.value != 100) {
            ele.value = 100;
            var ev = document.createEvent("HTMLEvents");
            ev.initEvent("change", false, true);
            ele.dispatchEvent(ev);
        }
    });
})();
