from flask import Flask, render_template, Response, jsonify
from bson import json_util
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin
import psycopg2
import requests
import json
import csv 
import os
import sys
# import spotipy
# import spotipy.util as util
# from spotipy.oauth2 import SpotifyClientCredentials


#----- Import API key ---------------
# from config import username, password, dbname, USERNAME, PASSWORD

DATABASE_URL = os.environ['DATABASE_URL']

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_ORIGINS'] = '*'

# Use flask_pymongo to set up mongo connection


# app.config['MONGO_URI'] = 'mongodb+srv://' + username + ':' + password + '@cluster0.jvrf7.mongodb.net/' + dbname + '?retryWrites=true&w=majority'

# run in debug mode
app.debug = True

mongo = PyMongo(app)
   
# class Songs:
#     def __init__(self,songArray):
#         self.songName = songArray[3]
#         self.performer = songArray[4]
#         self.songID = songArray[5]
#         self.instance = songArray[6]
#         self.weeksonChart = songArray[-1]


def m_insert(name,data):
    topcol = mongo.db.top100
    dataset = {"type": name, "result" : data}
    topcol.insert_one(dataset)
    return

#function that filters vowels
def filterLetters(letter):
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',',']
    return (letter in letters)    

# Database connection setup
t_host = "localhost"
t_port = "5432"
t_dbname = "top100"

@app.route('/', methods=["GET", "POST"])
@app.route("/home")
def root():
    # return render_template('index.html')
    return app.send_static_file("index.html")


# get the top100 song information from mongodb
@app.route("/get_top100", methods=["GET"])
@cross_origin()
def get_geo():

    # access the top 100 collection
    topcol = mongo.db.top100

    myquery = { "type": "top100" }

    #Are the documents there?
    x = topcol.count_documents(myquery)
    data = {}
    if x == 0:
        print("No Top 100 data")

    else:
        topdoc = topcol.find_one(myquery)
        print(topdoc)
        data = json.loads(json_util.dumps(topdoc))

    return jsonify(data)

# call the API to load the top 100 file and store into Mongo DB if not there.
@app.route("/reload_top100", methods=["GET"])
@cross_origin()
def reload_geo():
    # access the top 100 collection
    topcol = mongo.db.top100

    hot100 = os.path.join("data", "HotStuff.csv")

    myquery = { "type": "top100" }

    #Are the documents there?
    x = topcol.count_documents(myquery)

    if x == 0:
        # if col == 0:
        # if the file file is not stored, read the file from the DB

        with open(hot100, mode='r') as file:
            headers = file.readline()

            # parse the headers and clean them up.  Used to create a dictionary 
            headers = headers.lower()
            hdrFiltered = ''
            for letter in headers:
                if filterLetters(letter):
                    hdrFiltered += letter
            hdr_list = str(hdrFiltered).split(',')
            print(hdr_list)

            # reading the CSV file
            csvFile = csv.reader(file)

            # counter = 0
            for lines in csvFile:
                test = zip(hdr_list,lines)
                songDict = dict(test)
                try:
                    topcol.update_one({'songid': songDict['songid']},{'$set':songDict},upsert=True)

                except:
                    print("something happened")
                    break

    return "finished"


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


# call the API to load the top 100 file and store into SQL DB if not there.
@app.route("/reload_top100_sql", methods=["GET"])
@cross_origin()
def reload_top100_sql():
    # access the top 100 collection


    db_conn = psycopg2.connect(DATABASE_URL, sslmode='require')
#    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=USERNAME, password=PASSWORD)
    cursor = db_conn.cursor()

    hot100 = os.path.join("data", "HotStuff.csv")

    with open(hot100, mode='r') as file:
        file.readline()  # skip the header

        # reading the CSV file
        csvFile = csv.reader(file)

        counter = 0
        for lines in csvFile:

            try:
                id = 0
                sql_query = """select id, top_position, weeksonchart from song where songid = %s and instnce = %s """
                # print(sql_query,(lines[sidIn],int(lines[iIn])))
                cursor.execute(sql_query,(lines[sidIn],int(lines[iIn])))

                record = cursor.fetchone()

                if record == None:
                    postgres_insert_query = """ INSERT INTO song (songid, name, performer,top_position,instnce,weeksonchart) VALUES (%s,%s,%s,%s,%s,%s)"""
                    record_to_insert = (lines[sidIn], lines[sIn], lines[pIn],int(lines[ppIn]),int(lines[iIn]),int(lines[wocIn]))
                    cursor.execute(postgres_insert_query, record_to_insert)
                    # db_conn.commit()
                    # need to retrieve the id
                    sql_query = """select id, top_position, weeksonchart from song where songid = %s and instnce = %s """
                    # print(sql_query,(lines[sidIn],int(lines[iIn])))
                                    
                    cursor.execute(sql_query,(lines[sidIn],int(lines[iIn])))
                    record = cursor.fetchone()
                    id = record[0]
                else:
                    updated = False                     # set flag to false
                    id = record[0]
                    top_position = record[1]
                    weeksonchart = record[2]
                    if top_position > int(lines[ppIn]): 
                        top_position = int(lines[ppIn])
                        updated = True
                    if weeksonchart < int(lines[wocIn]): 
                        weeksonchart = int(lines[wocIn])
                        updated = True
                    # print(id,updated,weeksonchart,top_position,lines[ppIn],lines[wocIn])
                    if updated:
                        sql_update_query = """UPDATE song set top_position = %s, weeksonchart = %s where id = %s"""
                        cursor.execute(sql_update_query,(top_position,weeksonchart,id))
                        # db_conn.commit()  # move commit to after everything is updated

                # write to other tables

                sql_query = "select id from weeks where weekinfo = '" + str(lines[wIn]) + "'"
                # print(sql_query,lines[wIn])
                #cursor.execute(sql_query,(str(lines[wIn])))
                cursor.execute(sql_query)
                record = cursor.fetchone()
                if record == None:
                    postgres_insert_query = "INSERT INTO weeks (weekinfo) VALUES ('" + str(lines[wIn]) + "')"
                    cursor.execute(postgres_insert_query)
                    # db_conn.commit()      # move commit to after everything is updated
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
                if record == None:
                    postgres_insert_query = """ INSERT INTO weekly (id, weekid, url,pos,top_pos_wk) VALUES (%s,%s,%s,%s,%s)"""
                    record_to_insert = (id, weekid, lines[uIn],int(lines[wpIn]),int(lines[ppIn]))
                    cursor.execute(postgres_insert_query, record_to_insert)
                    # db_conn.commit()      # move commit to after everything is updated

            except Exception:
                exc_type, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print("error occurred", sys.exc_info()[1])
                cursor.close()
                db_conn.close()
                break

            else:
                db_conn.commit()
                counter += 1
                if counter % 10000 == 0: print("next record",counter)
                # if counter > 200: break

    return "finished"

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/performer",  methods=["GET"])
@app.route("/get_top100_sql/performer/<performer>", methods=["GET"])
@cross_origin()
def get_top100_sql_performer(performer= '*'):

    # access the top 100 collection

    db_conn2 = psycopg2.connect(DATABASE_URL, sslmode='require')
#    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=USERNAME, password=PASSWORD)
    cursor2 = db_conn2.cursor()
    
    try:
        record = []
        if performer != '*':
            performer = check_string(performer)         # escape any single quote characters
            sql_query = "select id, name, top_position, instnce, weeksonchart from song where lower(performer) = lower('" + performer + "')"
        else:
            sql_query = "select distinct name, performer, top_position, weeksonchart from song "
            
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
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
    db_conn2 = psycopg2.connect(DATABASE_URL, sslmode='require')
#    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=USERNAME, password=PASSWORD)
    cursor2 = db_conn2.cursor()

    try:
        record = []
        if song != '*':
            song = check_string(song)
            sql_query = "select name, performer, top_position, weeksonchart from song" 
            sql_query += "  where lower(name) = lower('" + song + "')"
        else:
            sql_query= "select distinct name from song"
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
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
    db_conn2 = psycopg2.connect(DATABASE_URL, sslmode='require')
#    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=USERNAME, password=PASSWORD)
    cursor2 = db_conn2.cursor()

    try:
        song = check_string(song)   # need to add a single quote where necessary for query
        sql_query = "select s.id, name, performer, wk.weekinfo, w.pos, w.top_pos_wk, s.top_position, instnce, weeksonchart from song as s" 
        sql_query += " inner join weekly w on s.id = w.id " 
        sql_query += " inner join weeks wk on w.weekid = wk.id where lower(name) = lower('" + song + "')"
                    
        cursor2.execute(sql_query)
        record = cursor2.fetchall()

    except Exception:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("error occurred", sys.exc_info()[1])
        record = []

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/search/<path:searchInput>",  methods=["GET"])
@cross_origin()
def get_top100_sql_search(searchInput):
    record = []
    if searchInput == '': jsonify(record)
    print("have data: " + searchInput)
    sql_query_where = ''
    result = searchInput.split('/')
    index = 0
    for res in result:
        srchkey=res.split('=')
        lower = ''
        lower2 = ''
        if index <= 1: 
            lower = "lower("
            lower2 = ") "

        if srchkey[1] != 'All': sql_query_where += "and " + lower + srchkey[0] + lower2 + " = " + lower + "'" + check_string(srchkey[1]) + "'" + lower2
        index += 1
    # access top 100 collection
    db_conn2 = psycopg2.connect(DATABASE_URL, sslmode='require')
#    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=USERNAME, password=PASSWORD)
    cursor2 = db_conn2.cursor()

    sql_order = " order by weekinfo desc , name "
    
    try:
        
        sql_query = "select name, performer, s.top_position, weeksonchart, wk.weekinfo, w.pos  from song as s" 
        sql_query += " inner join weekly w on s.id = w.id " 
        sql_query += " inner join weeks wk on w.weekid = wk.id "
        if len(sql_query_where) != 0: sql_query += 'where 1=1 ' + sql_query_where
        sql_query += sql_order
        print(sql_query)  
        cursor2.execute(sql_query)
        record = cursor2.fetchall()


    except Exception:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

# get the songs for a performer from SQL DB
@app.route("/get_top100_sql/weekid/")
@app.route("/get_top100_sql/weekid/<weekid>",  methods=["GET"])
@cross_origin()
def get_top100_sql_week(weekid = ''):
    
    record = []
    # access top 100 collection
    db_conn2 = psycopg2.connect(DATABASE_URL, sslmode='require')
#    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=USERNAME, password=PASSWORD)
    cursor2 = db_conn2.cursor()

    if weekid == '': 
        print("have data: " + weekid)
        sql_query_where = ''
    else:
        print(weekid)
        sql_query_where = ' where weekid = ' + weekid
    try:
        
        sql_query = "select distinct weekid from weeks" + sql_query_where
        cursor2.execute(sql_query)
        record = cursor2.fetchall()

    except Exception:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print("error occurred", sys.exc_info()[1])

    finally:
        cursor2.close()
        db_conn2.close()

    return jsonify(record)

if __name__ == "__main__":
    app.run()
