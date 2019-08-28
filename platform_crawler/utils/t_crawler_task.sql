-- 查询所有任务
select id, platform, account, status
from t_crawler_task
where createTime like '2018-10-11%'
order by platform, account;

-- 查询重复的任务
select id, platform,status, account, count(account) c
from t_crawler_task
where createTime like '2018-10-11%'
group by account
having c > 1;

-- 未执行过的重复任务，随便保留一个就行，反正都没有执行过
delete
from t_crawler_task
where id in (select b.id
             from (select id, platform, account, count(account) c
                   from t_crawler_task
                   where createTime like '2018-12-08%'
                     and status = 1
                   group by account
                   having c > 1) b);

-- 执行过的重复任务，保留成功执行的任务，删掉未执行的
delete
from t_crawler_task
where createTime like '2018-12-08%'
  and status = 1
  and account in (select b.account
                  from (select id, platform, account, count(account) c
                        from t_crawler_task
                        where createTime like '2018-12-08%'
                        group by account
                        having c > 1) b);

--------------------------------------------------------

select id,category,platform,account,password,loginUrl
from t_crawler_task
where category in ('CPA', 'MSG')
    and status in (1)
    and createTime like '2019-03-06%'
group by account order by platform,account;

select platform,account,time_to_sec(timediff(updateCookieTime,getTaskTime)) diff, getTaskTime, timediff(updateCookieTime, getTaskTime) diff2
from t_crawler_task
where createTime > '2019-03-12'
having(diff > 1800)
order by platform,account;
---------------------------------------------------------
update t_crawler_task
set status=3,updateCookieTime='2019-03-11 12:19:05',updateTime='2019-03-11 12:19:05'
where
    status=1 and createTime like '2019-03-11%';

select id,category,platform,account,password,loginUrl
from t_crawler_task
where updateCookieTime='2019-03-11 12:19:05' and updateTime='2019-03-11 12:19:05';
---------------------------------------------------------
update t_crawler_task set status=1 where status=2 and createTime > '2019-06-03';
---------------------------------------------------------
-- 账号对应的AE，产品
select distinct(acctNo),AEName,productName from t_execute_order_info where acctNo in (2365493663,3012181760);

select l.platform,l.account, r.acctNo, r.AEName, r.productName
from t_crawler_task l left join t_execute_order_info r on l.account = r.acctNo where l.createTime > '2019-08-28' and l.status in (4);


