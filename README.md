!Top 100 music search (top100-search.herokuapp.com)

Small application with the top songs from 1958 to 2000.  Looking to include up to 2018 if interests.  The song results of the top 100 songs for each week are store in a postgresSQL database.  I used FLask to drive the application and provide a few APIs that can be used to pull the data from the database.  The application allows a user to pick a set of songs based on filter settings from the database and display information on it.  What was the top position it made, how many weeks on the chart.  In addition, there is the ability to graph a song or set of songs based on what the user is interested in.  Check it out at https://top100-search.herokuapp.com .  Let me know if there is anything you would like to see added.  I am working on a page to interact with Spotify to show the different characteristics of a song.  Long term would be to allow the user to create a Spotify playlist and then transfer the set of songs over to an IOS app to play them.

APIs:

~/get_top100_sql/performer
  Returns all the performers in the database - performer
~/get_top100_sql/performer/<performer>
  Returns songs associated with the performer provided (currently needs to be an exact match) - name, performer, top_position, chartyear, weeksonchart
  
~/get_top100_sql/song
 Returns all the songs - name, s.performer, top_position, chartyear, weeksonchart
~/get_top100_sql/song/<song>
  Returns high level informtion on the song based on song name (currently needs to be an exact match) - name, performer, top_position, weeksonchart
  
  
~/get_top100_sql/song_details/<song>
  Returns detailed informtion on the song based on song name (currently needs to be an exact match) - name, performer, weekinfo(week in chart), pos (position in charts on that week), top_pos_wk (the highest position in the charts at that week), top_position (Top position all together), chartyear (year the song hit the charts), instnce (if there were multiple times hitting the charts), weeksonchart (weeks on the charts at this week), week number, year
  
~/get_top100_sql/search/
  returns the high level informatin for all the songs - name, performer, top_position, chartyear, weeksonchart
~/get_top100_sql/search/<path:searchInput>
  searchInput is a string composed of keywords (performer(char), song(char), top_position (int 1:100), chartyear (int 1958:2000)) with each keywordtuple separated by a backward slash '/'.  example ~/get_top100_sql/search/name=<name>/performer=<performer>
  returns the high level informatin for songs matching the criteria - name, performer, top_position, chartyear, weeksonchart


~/get_top100_sql/search_details/<path:searchInput>
  searchInput is a string composed of keywords (performer(char), song(char), top_position (int 1:100), chartyear (int 1958:2000)) with each keywordtuple separated by a backward slash '/'.  example ~/get_top100_sql/search/name=<name>/performer=<performer>
  returns detailed information on the songs matching the criteria - name, performer, top_position, weeksonchart, weekinfo, pos,  weekdate

~/get_top100_sql/weekid/
~/get_top100_sql/weekid/<weekid>
  TBD
