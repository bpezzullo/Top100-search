select * from song order by name, performer asc LIMIT 100 

select * from weekly;

select * from weeks;

INSERT INTO weeks (weekinfo) VALUES ()
select id from weeks where weekinfo = '10/11/1958'
select id from weeks where weekinfo = '8/2/1958'

select * from song as s
inner join weekly as w on s.id=w.id
 where w.id = 175
 
 select distinct * from song LIMIT 100;
 
 select id, name, top_position, instnce, weeksonchart from song where performer =
 'The Beatles'
 
select id, performer, top_position, instnce, weeksonchart from song as s  where s.name
= '*'
select name, performer, s.top_position, weeksonchart, wk.weekinfo, w.pos  from song as s inner join weekly w on s.id = w.id  inner join weeks wk on w.weekid = wk.id where 1=1 and lower(performer)  = lower('The Animals')

select name, performer, s.top_position, weeksonchart, wk.weekinfo, w.pos  from song as s inner join weekly w on s.id = w.id  inner join weeks wk on w.weekid = wk.id where 1=1 and lower(name)  = lower(Don't Let Me Down) and lower(performer)  = lower('The Animals')

select name, performer, s.top_position, weeksonchart, wk.weekinfo, w.pos  from song as s inner join weekly w on s.id = w.id  inner join weeks wk on w.weekid = wk.id where 1=1 and lower(name)  = lower('Don''t Let Me Down') 

select  name, performer, s.top_position, weeksonchart, wk.weekinfo, w.pos  from song as s inner join weekly w on s.id = w.id  inner join weeks wk on w.weekid = wk.id order by weekid desc, name asc limit 100
