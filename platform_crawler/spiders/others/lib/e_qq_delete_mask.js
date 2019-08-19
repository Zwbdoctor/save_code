
(function(){
    function ensureEle(tag, succCall){          //轮询查找
        succCall = succCall || function(){};
        var bo = document.querySelectorAll(tag);
        var latecy = 0, timer;
        if(bo && bo.length>0)
            latecy = 0;
        else
            latecy = 500;
        function insertDom(){
            clearTimeout(timer);
            timer = setTimeout(function(){
                bo = document.querySelectorAll(tag);
                if(!bo || bo.length<=0){
                    insertDom();
                    return;
                }
                succCall(bo);
            }, latecy);
        }
        insertDom();
    }

    function removeEles(eles) {
        Array.prototype.forEach.call(eles, function(item, idx){
            item.remove();
        });
    }

    //进入step提示
    ensureEle('.gdt-mask', function(eles){
        removeEles(eles);
    });
    ensureEle('#__gdt_greenhand', function(eles){
        removeEles(eles);
    });

    //通用
    ensureEle('.qz_mask', function(eles){
        removeEles(eles);
    });
    ensureEle('.qz_dialog_layer', function(eles){
        removeEles(eles);
    });
})();
