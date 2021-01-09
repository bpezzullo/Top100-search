// from set up global variables used through out the JS functions.


var songkey = [], sox, songselected = [];
var perfkey = [], pex, perfselected = [];
var peakkey = [], pox, peekselected = [];
var yearkey = [], yex, yearselected = [];
var years = [];

// fucntion to generate the text for the drop downs.

function generatetxt(keylist) {

  var text, i;

  // start the dropdown list with All.
  text = "<option>Select Item</option>";
  // loop through array to populate the drop down.
  for (i = 0; i < keylist.length; i++) {
    text += "<option>" + keylist[i] + "</option>";
  }
  return text
}

// Create new Line Chart (blank data)
ctx = document.getElementById('graph-area');
var myLineChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: '',
        datasets: [{
            label: '',
            data: []
        }]
    },
    options: {
        legend: { 
            display: false
        },
        title: {
            display: true,
            text: "Song details"
        }
    } 
});
Chart.defaults.line.spanGaps = false;


  url = local + "/get_top100_sql/song/*"
  d3.json(url).then(function (data) {

    data.forEach(datarow => {
      sox = (datarow[0]);
      if (songkey.indexOf(sox) === -1) {
        songkey.push(sox);
      }
    });

    songkey.sort();
    document.getElementById("songselect").innerHTML = generatetxt(songkey);
  });

  url = local + "/get_top100_sql/performer/*"
  d3.json(url).then(function (data) {

    data.forEach(datarow => {

      pex = (datarow[0]);
      if (perfkey.indexOf(pex) === -1) {
        perfkey.push(pex);
      }
    });

    perfkey.sort();
    document.getElementById("performerselect").innerHTML = generatetxt(perfkey);
  });


  for (var i = 1958; i < 2001; i++) {
    yearkey.push(i)
  };

  document.getElementById("yearselect").innerHTML = generatetxt(yearkey);

  for (var i = 1; i < 101; i++) {
    peakkey.push(i)
  };


  document.getElementById("peakselect").innerHTML = generatetxt(peakkey);


/*------- End of Initialization -----*/


/**  Chart styling functions */
function ncColor(color,op) {
  var color1,color2,color3, temp;

  temp = color % 6
  color1 = temp * 51 ;
  color2 = 255 -  color1;
  color3 = (102 + color1) % 256

  // op: opacity [0,1]
  return `rgba(${color1}, ${color2}, ${color3}, ${op})`
}


function multiGraph(songinfo) {

  var lineData =  [];
  var songList = [];
  var myLineData = {
                    data : [],
                    labels : []
                    };

    var promiseText = [];
    // console.log(songinfo)
    songinfo.forEach(element => {promiseText.push(d3.json(local + "/get_top100_sql/song_details/" + element[0]))});

    // Go gather the information.
    mySongPromises = Promise.all(promiseText);

    // Once all the data has been retrieved kick off the processing below
    mySongPromises.then(function(songdinfo) {
      // console.log(songdinfo);
      songdinfo.forEach(elem => {       // Capture the number of weeks for the song being on the charts and save it for the graph
        // console.log(elem);
        lineData.push(buildJS(elem));
        songList.push(elem[0][1]);
      });

      // console.log(songList);
      //create the template to populate the Chartjs module
      for (var i=0;i < songList.length;i++) {
          myLineChart.data.datasets.push({
            type : 'line',
            label: songList[i],
            data : [],
            borderColor : ncColor(i,0.5),
            backgroundColor:  ncColor(i,0.5),
            fill : false
          });
        };

      //lineData has a dictionary of weekid to the position that the song is on the charts "02022019": 20.
      // We need to decompose that so that it can be graphed with the other songs
      // first find all the weeks needed to be plotted
      lineData.forEach(data2 => {    
        // console.log(data2);
        Object.keys(data2).forEach(key => {if (myLineData.labels.indexOf(key) === -1) {
                                                myLineData.labels.push(key)}
                                              });
          
      });
      // Put the weeks in chronological order.   
      myLineData.labels.sort();

      //Need to remove duplicates, I think

      // Now loop through each week and pull the song and position of the song on the chart
      myLineData.labels.forEach(key => {

        var posTemp
        for (var i=0; i < lineData.length; i++) {
          if (lineData[i][key]) {posTemp=lineData[i][key];}
          else { posTemp = 'NaN'; };
          myLineChart.data.datasets[i].data.push(posTemp);
        }
      
      });

      myLineChart.data.labels = myLineData.labels;
      myLineChart.options.legend.display = true;
      myLineChart.update();

    })

  return 
}


/* create a linegraph for each song from the performer */

function generateMultiGraph(performer) {

  // clear out chart
  while (myLineChart.data.datasets.length > 0) {
    myLineChart.data.datasets.pop()

  }

  url = local + "/get_top100_sql/performer/" + performer;

  // pull the songs associated with the performer
  d3.json(url).then(function(songinfo) {

    // Once we have the songs then gather the song information.  We don't want to start processing until
    // after all the data is back.  Set up the variable promiseText to capture all the calls
  multiGraph(songinfo);
});

  return
}

/* create a linegraph for each song from the performer */

function generatePosGraph(position, year) {

  // clear out chart
  while (myLineChart.data.datasets.length > 0) {
    myLineChart.data.datasets.pop()
  }

  url = local + "/get_top100_sql/search/" + "top_position=" + position + "/chartyear=" + year;
  // pull the songs associated with the performer
  d3.json(url).then(function(songinfo) {

    // Once we have the songs then gather the song information.  We don't want to start processing until
    // after all the data is back.  Set up the variable promiseText to capture all the calls
  multiGraph(songinfo);

});

  return
}

function buildJS(songinfo) {

  var lineData =  {}
    

    songinfo.forEach(element => {
      var key;
      key = 'Year ' + element[11] + ' Wk ' ;
      if (element[10] < 10) {key += '0'}
      key += element[10];
      lineData[key] = element[4];
    });

    // console.log(lineData);
    return lineData

  }

// Function that builds the table with song information.

function generateGraph(song) {

  var lineData =  {}

  // Need to build query to gather information.

  url = local + "/get_top100_sql/song_details/" + song;
  
  d3.json(url).then(function (songinfo) {

    while (myLineChart.data.datasets.length > 0) {
      myLineChart.data.datasets.pop()
    }

    lineData = buildJS(songinfo);

    myLineChart.data.datasets.push({
      type : 'line',
      label: song,
      data : Object.values(lineData),
      borderColor : ncColor(2, 0.5),
      backgroundColor:  ncColor(2,0.5),
      fill : false
    });

    myLineChart.data.labels = Object.keys(lineData)

    // console.log("in Graph", myLineChart.data.labels)

    myLineChart.options.legend.display = true;
    myLineChart.update();

  });
}

// Gather input from user and assess songs to graph

function checkinput() {

  var songselected = document.getElementById("songselect").value;
  var performerselected = document.getElementById("performerselect").value;
  var positionselected = document.getElementById("peakselect").value;
  var yearselected = document.getElementById("yearselect").value;

  // console.log("Button Hit", songselected, performerselected);

  if (songselected != 'Select Item') {
    generateGraph(songselected);
    document.getElementById("performerselect").value = 'Select Item';
    document.getElementById("peakselect").value = 'Select Item';
    document.getElementById("yearselect").value = 'Select Item';
  }
  else {  
    if (performerselected != 'Select Item') {
      generateMultiGraph(performerselected);
      document.getElementById("peakselect").value = 'Select Item';
      document.getElementById("yearselect").value = 'Select Item';
    }
    else {

      if (positionselected != 'Select Item' && yearselected != 'Select Item') {
     generatePosGraph(positionselected,yearselected);
    }

     else{
      alert("Select a song, or a performer, or both a position and year");
     }

    }
  }

}

