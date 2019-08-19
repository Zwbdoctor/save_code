//起始日期
var inpStartDate = document.querySelector('div[ng-model="dateRange.startDate"] input');
inpStartDate.value = '2018/08/05';
var evsd = document.createEvent("HTMLEvents");  
evsd.initEvent("change", false, true);  
inpStartDate.dispatchEvent(evsd);  

//终止日期
var inpEndDate = document.querySelector('div[ng-model="dateRange.endDate"] input');
inpEndDate.value = '2018/08/07';
var evsd = document.createEvent("HTMLEvents");  
evsd.initEvent("change", false, true);  
inpEndDate.dispatchEvent(evsd);  

//计算页面高度
document.body.offsetHeight
