(function(){
    function ensureEle(tag, succCall){
        succCall = succCall || function(){};
        var bo = document.querySelectorAll(tag);
        var latecy = 0, timer;
        if(bo && bo.length>0)
            latecy = 0;
        else
            latecy = 900;
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

    ensureEle('.dialog', function(eles){
        removeEles(eles);
    });
 })
