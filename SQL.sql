drop table if exists bookmarks_history;
create table bookmarks_history(
     bid                            integer primary key autoincrement,
     pid                            int default 0,
     plevel                         varchar(100),
     pos                            int default 0,
     btype                          tinyint,
     title                          varchar(200), 
     url                            varchar(4096),
     enjoy                          tinyint default 0,
     create_time                    datetime,
     update_time                    datetime,
     last_visit_time                datetime
);
drop table if exists bookmarks_current;
create table bookmarks_current(
     bid                            integer primary key,
     pid                            int default 0,
     plevel                         varchar(100),
     pos                            int default 0,
     btype                          tinyint,
     title                          varchar(200), 
     url                            varchar(4096),
     enjoy                          tinyint default 0,
     create_time                    datetime,
     update_time                    datetime,
     last_visit_time                datetime
);
drop table if exists merge_rec;
create table merge_rec(
    client_id                       varchar2(100),
    brower                          varchar2(30),
    file                            varchar2(1000),
    md5                             varchar2(100),
    create_time                     datetime default (datetime('now', 'localtime'))
);
drop table if exists bid_mapping;
create table bid_mapping (
     bid                            int, 
     new_bid                        int,
     level                          varchar(100)
);
