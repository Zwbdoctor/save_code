
(function(){
    function ensureEle(tag, succCall){          //��ѯ����
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

    ensureEle('#_side_detail #_detail_pager select', function(ele){     //ѡ�з�ҳ���ж��ǲ���ÿҳ100�����Ǿ��л�
        if(ele.value != 100) {
            ele.value = 100;
            var ev = document.createEvent("HTMLEvents");
            ev.initEvent("change", false, true);
            ele.dispatchEvent(ev);
        }
    });
})();
