CREATE TABLE song(
id bigint primary key GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 1000000 CACHE 1 ),
songid varchar(255) not null,
name varchar(255) not null,
performer varchar(255) not null,
top_position int,
instnce int,
weeksonchart  int);

CREATE TABLE weekly(

id bigint not null,
weekid int not null,
url varchar(255) not null,
pos int not null,
top_pos_wk int not null);

CREATE TABLE weeks(
id bigint primary key GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 10000 CACHE 1 ),
weekinfo varchar(255) not null)


INSERT INTO song  (songid, name, performer,top_position,instnce,weeksonchart) VALUES ('Poor Little FoolRicky Nelson','Poor Little Fool', 'Ricky Nelson', 1, 1, 1);


select id, top_position, weeksonchart from song where songid = 'Poor Little FoolRicky Nelson' and instnce = 1
'http://www.billboard.com/charts/hot-100/1958-08-02', '8/2/1958', '1','Poor Little Fool', 'Ricky Nelson', 'Poor Little FoolRicky Nelson','1', '', '1'