from flask import Flask, render_template, request, Response, jsonify,redirect,url_for, session
from flask_cors import CORS, cross_origin
from pubsub import pub
import psycopg2
from _thread import start_new_thread
import time
import requests
import json
import csv 
import os
import sys
import datetime
import re
import spo


DATABASE_URL = os.environ['DATABASE_URL']

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_ORIGINS'] = '*'
app.config['SECRET_KEY']= 'dev'

# run in debug mode
app.debug = False
global local
local = False
playlist_item = []

test_running = False


uIn = 0             # URL index
wIn = 1             # Weekid Index
wpIn = 2            # Week position
sIn = 3             # song name index
pIn = 4             # performer index
sidIn = 5           # song ID index
iIn = 6             # Instance index
pwpIn = 7           # previous week position index
ppIn = 8            # peak position at that time index
wocIn = 9           # weeks on chart index


# ------------ create a listener ------------------

def listener1(arg1, arg2=None):
    print('Function listener1 received:')
    print('  arg1 =', arg1)
    start_new_thread ( load, ())
    return


# ------------ register listener ------------------

pub.subscribe(listener1, 'load')

  
def create_tables(cursor, db_conn):
    print("creating tables")
    sql_query = 'CREATE TABLE song (id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 1000000 CACHE 1 ),songid character varying(255) COLLATE pg_catalog."default" NOT NULL,name character varying(255) COLLATE pg_catalog."default" NOT NULL,performer character varying(255),top_position integer,instnce integer,weeksonchart integer, chartyear integer, spotify_trackid character varying(255), CONSTRAINT song_pkey PRIMARY KEY (id));'
    cursor.execute(sql_query)

    print("first table created")
    sql_query = 'CREATE INDEX "Name_index" ON song USING btree (name COLLATE pg_catalog."default" ASC NULLS LAST);' 
    cursor.execute(sql_query)
    
    sql_query = 'CREATE INDEX songid_index ON song USING btree (songid COLLATE pg_catalog."default" ASC NULLS LAST);' 
    cursor.execute(sql_query)

    sql_query = 'CREATE TABLE weekly (id bigint NOT NULL, weekid integer NOT NULL, url character varying(255) COLLATE pg_catalog."default" NOT NULL, pos integer NOT NULL, top_pos_wk integer NOT NULL);' 
    cursor.execute(sql_query)

    sql_query = 'CREATE INDEX id_index ON weekly USING btree (id ASC NULLS LAST);' 
    cursor.execute(sql_query)

    sql_query = 'CREATE TABLE weeks (id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 10000 CACHE 1 ), weekinfo character varying(255) COLLATE pg_catalog."default" NOT NULL,weekdate date,year int,CONSTRAINT weeks_pkey PRIMARY KEY (id));' 
    cursor.execute(sql_query)

    sql_query = 'CREATE TABLE performer (id bigint NOT NULL, performer character varying(255) NOT NULL);' 
    cursor.execute(sql_query)

    sql_query = 'CREATE INDEX perfor_index ON performer USING btree (performer ASC NULLS LAST);' 
    cursor.execute(sql_query)

    sql_query = 'CREATE TABLE stats (id bigint NOT NULL, popularity integer, dance float, energy float, loud float, speech float, accoustic float, liveness float, valence float, tempo float, CONSTRAINT stats_pkey PRIMARY KEY (id));'
    cursor.execute(sql_query)

    db_conn.commit()

    return 

def create_conn():
    if local :
        db_conn = psycopg2.connect(DATABASE_URL)
    else: 
        db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return db_conn


# load the tables
def load():

    global test_running
    print("before",test_running)
    if test_running: return

    test_running = True

    db_conn =  create_conn()

    cursor = db_conn.cursor()

    sql_query = "SELECT EXISTS(SELECT *  FROM information_schema.tables  WHERE  table_name = 'song');"
    cursor.execute(sql_query)
    record = cursor.fetchone()

    if record[0] == False : create_tables(cursor,db_conn)

    hot100 = os.path.join("data", "HotStuff.csv")

    with open(hot100, mode='r') as file:
        file.readline()  # skip the header

        # reading the CSV file
        csvFile = csv.reader(file)

        counter = 0
        for lines in csvFile:

            # remove slashes from song and songid
            lines[sIn] = re.sub("/", "-", lines[sIn])

            lines[sidIn] = re.sub("/", "-", lines[sidIn])

            lines[sIn] = re.sub("'", "", lines[sIn])

            lines[sidIn] = re.sub("'", "", lines[sidIn])

            weekid = datetime.datetime.strptime(str(lines[wIn]), '%m/%d/%Y')
            year = weekid.year

            if year > 2000 : continue   # ignore the new records for now.

            try:

                id = 0

                sql_query = """select id, top_position, weeksonchart, chartyear from song where songid = %s and instnce = %s """

                cursor.execute(sql_query,(lines[sidIn],int(lines[iIn])))

                record = cursor.fetchone()

                if record is None:
                    postgres_insert_query = """ INSERT INTO song (songid,  name, performer,top_position,instnce,weeksonchart, chartyear) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                    record_to_insert = (lines[sidIn], lines[sIn],lines[pIn],int(lines[ppIn]),int(lines[iIn]),int(lines[wocIn]),year)
                    cursor.execute(postgres_insert_query, record_to_insert)

                    # need to retrieve the id
                    sql_query = """select id, top_position, weeksonchart from song where songid = %s and instnce = %s """
                                    
                    cursor.execute(sql_query,(lines[sidIn],int(lines[iIn])))
                    record = cursor.fetchone()
                    id = record[0]
                else:
                    updated = False                     # set flag to false
                    id = record[0]
                    top_position = record[1]
                    weeksonchart = record[2]
                    chartyear = record[3]

                    if top_position > int(lines[ppIn]):     # save the top position of the song in the main record
                        top_position = int(lines[ppIn])
                        updated = True
                    if weeksonchart < int(lines[wocIn]):    # save the highest number of weeks on the chart
                        weeksonchart = int(lines[wocIn])
                        updated = True
                    if chartyear > year:            # save the first year that the song hit the charts
                        chartyear = year
                        updated = True

                    # update the record if a change is made
                    if updated:
                        sql_update_query = """UPDATE song set top_position = %s, weeksonchart = %s, chartyear = %s where id = %s"""
                        cursor.execute(sql_update_query,(top_position,weeksonchart,chartyear,id))

                # write to other tables

                sql_query = "select id from weeks where weekinfo = '" + str(lines[wIn]) + "'"

                cursor.execute(sql_query)
                record = cursor.fetchone()
                if record is None:

                    postgres_insert_query = "INSERT INTO weeks (weekinfo, weekdate, year) VALUES ('" + str(lines[wIn]) + "', '" + str(lines[wIn]) + "' , " + str(year) + ")"
                    cursor.execute(postgres_insert_query)

                    # need to retrieve the id
                    sql_query = "select id from weeks where weekinfo = '" + str(lines[wIn]) + "'"
                    cursor.execute(sql_query)
                    record = cursor.fetchone()

                weekid = record[0]

                # write the week specific information for the song
                sql_query = """select * from weekly where id = %s and weekid = %s"""
                cursor.execute(sql_query,(id, weekid))
                record = cursor.fetchone()

                # was a record found?
                if record is None:
                    postgres_insert_query = """ INSERT INTO weekly (id, weekid, url,pos,top_pos_wk) VALUES (%s,%s,%s,%s,%s)"""
                    record_to_insert = (id, weekid, lines[uIn],int(lines[wpIn]),int(lines[ppIn]))
                    cursor.execute(postgres_insert_query, record_to_insert)

                # find out if more than one performer for the song.  If so than split the performers out

                performer = lines[pIn]
                x = performer.count('/')

                if (( x < 1) or (x > 3)):
                    y = performer.count('&')
                    performer = re.sub("/", "-", performer)
                    if (( y < 1) or (y > 2)):
                        mperf = [re.sub("&", "-", performer)]
                    else:
                        mperf = performer.split('&')
                else:
                    mperf = performer.split('/')


                for performer in mperf:

                    # remove single quotes
                    performer = re.sub("'", "", performer)
                    # write to performer tables

                    sql_query = "select id from performer where performer = '" + performer + "' and id = " + str(id)

                    cursor.execute(sql_query)
                    record = cursor.fetchone()
                    if record == None:

                        postgres_insert_query = "INSERT INTO performer (id, performer) VALUES ('" + str(id) + "', '" + performer + "')"
                        cursor.execute(postgres_insert_query)

            except Exception:
                print(sys.exc_info())
                print("error occurred", sys.exc_info()[1])
                break

            else:
                db_conn.commit()
                counter += 1
                if counter % 10000 == 0: print("next record",counter)
        
                # if counter > 1: break

        cursor.close()
        db_conn.close()


    spotInfo = os.path.join("data", "Hot100AudioFeatures.csv")

    db_conn =  create_conn()

    cursor = db_conn.cursor()

    with open(spotInfo, mode='r',encoding='utf-8') as file:

        file.readline()  # skip the header

        # reading the CSV file
        csvFile = csv.reader(file)

        for lines in csvFile:

            # Remove slashes and single quotes
            if lines[4] == '': continue

            lines[0] = re.sub("/", "-", lines[0])

            lines[0] = re.sub("'", "", lines[0])

            try:

                # query for the song by the songid
                sql_query = "select id from song where songid = '" + lines[0] + "';"

                cursor.execute(sql_query)
                record = cursor.fetchone()

                if record is None : continue  # This record has not been pulled into the database 

                id = record[0]

                # add the track information to the songs database
                sql_update_query = """UPDATE song set spotify_trackId = %s where id = %s"""
                cursor.execute(sql_update_query,(str(lines[4]),str(id)))

                # check to see if the information is already in stats table?
                sql_query = "select EXISTS(select id from stats where id = " + str(id) + ");"

                cursor.execute(sql_query)
                record = cursor.fetchone()

                if record[0] : continue  # This record has been saved into the database 

                # if not make sure there is a value, default to 0 if needed for the fields we want.
                for i in range(9,21):
                    if lines[i] == '': lines[i]= 0

                # Save the entry in the stats table
                postgres_insert_query = "INSERT INTO stats (id, popularity, dance, energy, loud, speech, accoustic, liveness, valence, tempo) Values (" + str(id) + " , " +\
                str(lines[9]) + " , " + \
                str(lines[10]) + " , " + \
                str(lines[11]) + " , " + \
                str(lines[13]) + " , " + \
                str(lines[15]) + " , " + \
                str(lines[16]) + " , " + \
                str(lines[18]) + " , " + \
                str(lines[19]) + " , " + \
                str(lines[20]) + ");"

                # print(postgres_insert_query)

                cursor.execute(postgres_insert_query)
                db_conn.commit()

            except Exception:
                print(sys.exc_info())
                print("error occurred", sys.exc_info()[1])
                test_running = False
                break

            else:

                counter += 1
                if counter % 100 == 0: print("next record",counter)
  
        
    cursor.close()
    db_conn.close()

    test_running = False

    return


#function that filters vowels
def filterLetters(letter):
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',',']
    return (letter in letters)    

def searchSplit(result):
    result = ''
    for res in result:
        srchkey=res.split('=')
        lower = ''
        lower2 = ''

        if (srchkey[0] == 'name') or (srchkey[0] == 'performer'): 
            lower = "lower("
            lower2 = ") "

        if (srchkey[0] == 'performer'): 
            srchkey[0] = 'p.' + srchkey[0]

        if srchkey[1] != 'All': result += "and " + lower + srchkey[0] + lower2 + " = " + lower + "'" + check_string(srchkey[1]) + "'" + lower2
    return result


@app.route('/', methods=["GET"])
@app.route("/home")
def root():

    return render_template('/index.html')
    # return app.send_static_file("index.html")

@app.route('/spot', methods=["GET"])
def spot():
    token = session['token']
    return redirect('/spot.html?' + token)


@app.route('/spot2', methods=["GET"])
def spot2():

    return render_template('/spot2.html')


@app.route('/graph', methods=["GET"])
def graph():

    return render_template('/graph.html')


@app.route('/redirect', methods=["GET"])
def redirect():

    return render_template('/spot2.html')


# call the API to load the top 100 file and store into SQL DB if not there.
@app.route("/reload_top100_sql", methods=["GET","PUT"])
@cross_origin()
def reload_top100_sql():
    # access the top 100 collection

    pub.sendMessage('load', arg1=123)
    
    print('Publish something via pubsub')

    return redirect('/')

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/performer",  methods=["GET"])
@app.route("/get_top100_sql/performer/<performer>", methods=["GET"])
@cross_origin()
def get_top100_sql_performer(performer= '*'):

    # access the top 100 collection
    record = []
    db_conn2 =  create_conn()
    
    cursor2 = db_conn2.cursor()
    
    try:
        # check to see if the database and song table exists
        sql_query = "SELECT EXISTS(SELECT *  FROM information_schema.tables  WHERE  table_name = 'song');"
        cursor2.execute(sql_query)
        record = cursor2.fetchone()
        # return empty record 
        if record[0] == False : return jsonify(record)

        # Check to see what type of request is being asked.
        if performer != '*':
            performer = check_string(performer)         # escape any single quote characters
            sql_query = "select name, s.performer, top_position, chartyear, weeksonchart from song as s inner join performer as p on s.id = p.id where lower(p.performer) = lower('" + performer + "')"
        else:
            sql_query = "select distinct p.performer from performer as p"
            
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/song",  methods=["GET"])
@app.route("/get_top100_sql/song/<song>", methods=["GET"])
@cross_origin()
def get_top100_sql_song(song = '*'):

    # access the top 100 collection
    db_conn2 =  create_conn()
    
    cursor2 = db_conn2.cursor()
    record = []
    try:

        if song != '*':
            song = check_string(song)
            sql_query = "select name, performer, top_position, weeksonchart from song as s " 
            sql_query += "  where lower(name) = lower('" + song + "')"
        else:
            sql_query= "select distinct name from song as s "

        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)
    
# Check to see if the test has a single quote.  If it does escape it with another quote
def check_string(word):
    result = ''
    for x in word:
        if x == "'": 
            result += "'"               # escape the next character
        result += x                     # continue checking letters
    return result

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/song_details/<song>", methods=["GET"])
@cross_origin()
def get_top100_sql_song_details(song):

    # access the top 100 collection
    db_conn2 =  create_conn()
    
    cursor2 = db_conn2.cursor()

    try:
        song = check_string(song)   # need to add a single quote where necessary for query
        sql_query = "select s.id, name, s.performer, wk.weekinfo, w.pos, w.top_pos_wk, s.top_position, chartyear, instnce, weeksonchart, EXTRACT(WEEK FROM wk.weekdate),EXTRACT(ISOYEAR FROM wk.weekdate) from song as s" 
        sql_query += " inner join weekly w on s.id = w.id " 
        sql_query += " inner join weeks wk on w.weekid = wk.id where lower(name) = lower('" + song + "')"
        
        sql_query +=  " order by wk.weekdate asc "
        
        cursor2.execute(sql_query)
        record = cursor2.fetchall()

    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])
        record = []

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/search/",  methods=["GET"])
@app.route("/get_top100_sql/search/<path:searchInput>",  methods=["GET"])
@cross_origin()
def get_top100_sql_search(searchInput = '*'):

    record = []

    db_conn2 =  create_conn()
    
    cursor2 = db_conn2.cursor()

    # check to see if the database and song table exists
    sql_query = "SELECT EXISTS(SELECT *  FROM information_schema.tables  WHERE  table_name = 'song');"
    cursor2.execute(sql_query)
    record = cursor2.fetchone()
    # return empty record if no data in database
    if record[0] == False : return jsonify(record)

    sql_query_where = ''

    if searchInput != '*':
        # print("have data: " + searchInput)
        result = searchInput.split('/')

        index = 0
        for res in result:
            srchkey=res.split('=')
            lower = ''
            lower2 = ''
            if (srchkey[0] == 'name') or (srchkey[0] == 'performer'): 
                lower = "lower("
                lower2 = ") "

            if (srchkey[0] == 'performer'): 
                srchkey[0] = 'p.' + srchkey[0]

            if srchkey[1] != 'All': sql_query_where += "and " + lower + srchkey[0] + lower2 + " = " + lower + "'" + check_string(srchkey[1]) + "'" + lower2
            index += 1

    else:  # return all songs
        pass

    sql_order = " order by chartyear desc ,top_position , name "
    
    try:
        
        sql_query = "select name, s.performer, s.top_position, chartyear, weeksonchart  from song as s inner join performer as p on s.id = p.id " 
        if len(sql_query_where) != 0: sql_query += 'where 1=1 ' + sql_query_where
        sql_query += sql_order
        # print(sql_query)  
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/select/<path:selectInput>",  methods=["GET"])
@cross_origin()
def get_top100_sql_select(selectInput):

    record = []

    db_conn2 =  create_conn()
    
    cursor2 = db_conn2.cursor()


    # check to see if the database and song table exists
    sql_query = "SELECT EXISTS(SELECT *  FROM information_schema.tables  WHERE  table_name = 'song');"
    cursor2.execute(sql_query)
    record = cursor2.fetchone()
    # return empty record if no data in database
    if record[0] == False : return jsonify(record)
    print(selectInput)

    sql_query_where = ''
    result = selectInput.split('/')

    if len(result) == 1:
        sql_query = "select name, s.performer, s.top_position, chartyear, pos, spotify_trackid from song as s inner join weekly as wl on s.id = wl.id " + \
                    "inner join weeks as ws on ws.id= wl.weekid "
        sql_order = " order by wl.pos asc"
        sql_query_where = " and ws.weekdate='"+ result[0].split('=')[1] + "'"
    else:
        index = 0
        for res in result:
            srchkey=res.split('=')
            if srchkey[0] == 'start': continue
            lower = ''
            lower2 = ''
            if (srchkey[0] == 'name') or (srchkey[0] == 'performer'): 
                lower = "lower("
                lower2 = ") "

            if (srchkey[0] == 'performer'): 
                srchkey[0] = 'p.' + srchkey[0]

            if srchkey[1] != 'All': sql_query_where += "and " + lower + srchkey[0] + lower2 + " = " + lower + "'" + check_string(srchkey[1]) + "'" + lower2
            index += 1
        
        sql_order = " order by top_position asc, chartyear, weeksonchart desc OFFSET " + result[3].split('=')[1] + " limit 100"
    
       
        sql_query = "select name, s.performer, s.top_position, chartyear, weeksonchart, spotify_trackid from song as s inner join performer as p on s.id = p.id " 


    # access top 100 collection
    try:
        
        sql_query += 'where 1=1 ' + sql_query_where
        sql_query += sql_order
        print(sql_query)  
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/search_details/<path:searchInput>",  methods=["GET"])
@cross_origin()
def get_top100_sql_search_details(searchInput):


    record = []

    if searchInput == '': return jsonify(record)
    print("have data: " + searchInput)
    sql_query_where = ''
    result = searchInput.split('/')
    index = 0
    for res in result:
        srchkey=res.split('=')
        lower = ''
        lower2 = ''
        if (srchkey[0] == 'name') or (srchkey[0] == 'performer'): 
            lower = "lower("
            lower2 = ") "

        if (srchkey[0] == 'performer'): 
            srchkey[0] = 'p.' + srchkey[0]
            
        if srchkey[1] != 'All': sql_query_where += "and " + lower + srchkey[0] + lower2 + " = " + lower + "'" + check_string(srchkey[1]) + "'" + lower2
        index += 1
    # access top 100 collection
    db_conn2 =  create_conn()
    
    cursor2 = db_conn2.cursor()

    sql_order = " order by weekdate desc , name "
    
    try:
        
        sql_query = "select name, performer, s.top_position, weeksonchart, wk.weekinfo, w.pos,  wk.weekdate from song as s" 
        sql_query = " inner join performer as p on s.id = p.id"
        sql_query += " inner join weekly w on s.id = w.id " 
        sql_query += " inner join weeks wk on w.weekid = wk.id "
        if len(sql_query_where) != 0: sql_query += 'where 1=1 ' + sql_query_where
        sql_query += sql_order
        print(sql_query)  
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/weekid/")
@app.route("/get_top100_sql/weekid/<weekid>",  methods=["GET"])
@cross_origin()
def get_top100_sql_week(weekid = '*'):
    
    record = []
    # access top 100 collection
    db_conn2 =  create_conn()
    
    cursor2 = db_conn2.cursor()
    sql_query = ""


    if weekid == '*': 

        sql_query = "select weekinfo, TO_CHAR(weekdate, 'yyyy-mm-dd') from weeks order by weekdate desc" 
    else:
        sql_query_where = ' where weekdate = ' + weekid
        sql_query += sql_query_where

    try:
        
        cursor2.execute(sql_query)
        record = cursor2.fetchall()

    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()
    
    return jsonify(record)

@app.route("/submit/<path:spotifyHeader>", methods=["POST"])
@cross_origin()
def push_playlist(spotifyHeader):
    playlist_item = request.get_json()
    spotResults = spotifyHeader.split("/")
    print(spotResults[0],'name',spotResults[1])
    result = spo.test(spotResults[0],playlist_item,spotResults[1])
    print('results',result)
    # session['token'] = result
    return jsonify(result)

@app.route("/view", methods=["GET","POST"])
@cross_origin()
def view_playlist():

    if request.method == 'POST':
        session['playlist'] = request.get_json()
        print("playlist POST")
        return render_template('/view.html')

    else:
        print("This is a GET")
        return render_template('/view.html', result= session['playlist'])

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/partialsearch/<string:searchInput>",  methods=["GET"])
@cross_origin()
def get_top100_sql_partialsearch(searchInput):

    record = []

    db_conn2 =  create_conn()
    cursor2 = db_conn2.cursor()

    # print("have data: " + searchInput)
    result = searchInput.lower()

    sql_query_where = "where lower(p.performer) like '%" + result + "%' or lower(name) like '%" + result + "%'"

    sql_order = " order by chartyear desc ,top_position , name "
    
    try:

        sql_query = "select name, s.performer, s.top_position, chartyear, weeksonchart,spotify_trackid  from song as s inner join performer as p on s.id = p.id " 
        sql_query += sql_query_where
        sql_query += sql_order
        print(sql_query)  
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        print(sys.exc_info())
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)





if __name__ == "__main__":
    app.run()
