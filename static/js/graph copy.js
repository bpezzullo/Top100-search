// from set up global variables used through out the JS functions.


var songkey = [], sox, songselected = [];
var perfkey = [], pex, perfselected = [];
var years = [];

var local = ''
local = 'http://127.0.0.1:5000'

// fucntion to generate the text for the drop downs.

function generatetxt(keylist) {

  var text, i;

  // start the dropdown list with All.
  text = "<option>All</option>";
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

var myLineData = {labels: [],
                  data: []};

url = local + "/get_top100_sql/song/*";

d3.json(url, function (data) {
  console.log(data);

  // loop through the data to find the information needed for the drop down lists for city
  // state, country and shape


  data.forEach(datarow => {

    sox = (datarow[0]);
    if (songkey.indexOf(sox) === -1) {
      songkey.push(sox);
    }

    pex = (datarow[1]);
    if (perfkey.indexOf(pex) === -1) {
      perfkey.push(pex);
    }

  });

  songkey.sort();
  document.getElementById("songselect").innerHTML = generatetxt(songkey);
  perfkey.sort();
  document.getElementById("performerselect").innerHTML = generatetxt(perfkey);

});

/*------- End of Initialization -----*/


/**  Chart styling functions */
function ncColor(op) {
  // op: opacity [0,1]
  return `rgba(21, 67, 96, ${op})`
}

/**  Chart styling functions */
function ncColor2(color) {
  // color: color of the line
  color = color * 25 + 25
  return `rgb(21, 67, ${color})`
}

function multiGraph(performer) {

  url = local + "/get_top100_sql/performer/" + performer;

  
  d3.json(url, function (songinfo) {

    // loop through the songs for the performer.
    songinfo.forEach(element => {

      // for each song get the details
      url = local + "/get_top100_sql/song_details/" + element[1];

      d3.json(url, function (songdinfo) {
        console.log(songdinfo);
        
        // build up the chart data
        buildJS(songdinfo);
      });
    
    });

  });
}

/* create a linegraph for each song from the performer */

function generateMultiGraph(performer) {

  // clear out chart
  while (myLineChart.data.datasets.length > 0) {
    myLineChart.data.datasets.pop()
    console.log("pop")
    
  }
  
  years = [];

  multiGraph(performer);

  console.log("in Multi Graph", myLineChart.data.datasets);

  myLineChart.data.labels = years;

  myLineChart.options.legend.display = true;
  myLineChart.update();
}

function buildJS(songinfo) {

    var values = [];
    

    songinfo.forEach(element => {
      values.push(element[4]);
      years.push(element[3])
    });

    console.log("in Build", years);

    // myLineChart.data.labels = years;
    myLineChart.data.datasets.push({
        type : 'line',
        label: songinfo[0][1],
        data : values,
        borderColor : ncColor2(myLineChart.data.datasets.length),
        backgroundColor:  ncColor(0.5),
        fill : false
    })

    console.log("in Build", myLineChart.data.datasets)

  }

// Function that builds the table with song information.

function generateGraph(song) {

  // Need to build query to gather information.


  url = local + "/get_top100_sql/song_details/" + song;
  
  d3.json(url, function (songinfo) {

    while (myLineChart.data.datasets.length > 0) {
      myLineChart.data.datasets.pop()
    }

    years = [];
  
    buildJS(songinfo);

    myLineChart.data.labels = years;

    console.log("in Graph", myLineChart.data.datasets)

    myLineChart.options.legend.display = true;
    myLineChart.update();

  });
}

// var songslct = document.getElementById("songselect")
// // var songslct = d3.select(".songselect")
// songslct.select(".songselect").on("change", function() {
//   var songselected = document.getElementById("songselect").value;
//   generateGraph(songselected);
// }

//

function checkinput() {

  var songselected = document.getElementById("songselect").value;
  var performerselected = document.getElementById("performerselect").value;

  console.log("Button Hit", songselected, performerselected);

  if (songselected != 'All') {
    generateGraph(songselected);
  }
  else {
    generateMultiGraph(performerselected);
  }

}

