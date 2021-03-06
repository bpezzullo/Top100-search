// from set up global variables used through out the JS functions.


var songkey = [], sox, songselected = [];
var perfkey = [], pex, perfselected = [];
var yearkey = [], yex, yearselected = [];
var peakkey = [], pox, peekselected = [];
var itemselected = [];


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


// create the drop downlists
function generateDropDowns(data) {

  // loop through the data to find the information needed for the drop down lists for city
  // state, country and shape

  // console.log(data)
  data.forEach(datarow => {
    // get the value of the different song names and push them into an array

    sox = (datarow[0]);
    if (songkey.indexOf(sox) === -1) {
      songkey.push(sox);
    }

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

  for (var i = 1; i < 101; i++) {
    peakkey.push(i)
  };


  document.getElementById("peakselect").innerHTML = generatetxt(peakkey);
  perfkey.sort();
  document.getElementById("performerselect").innerHTML = generatetxt(perfkey);
  songkey.sort();
  document.getElementById("songselect").innerHTML = generatetxt(songkey);

  document.getElementById("yearselect").innerHTML = generatetxt(yearkey);

}

var first = false
// Function that builds the table with song information.

function generateTable(performer = 'All', song = 'All', year = 'All', peakpos = 'All') {

  if (song == 'All' && performer == 'All' && year == 'All' && peakpos == 'All') {
    // Need to build query to gather information and the dropdown menus
    url = local + "/get_top100_sql/search/*";
    first = true
  }
  else {
    // Need to build query to gather information.

    songParms = "name=" + song + "/performer=" + performer + "/chartyear=" + year + "/top_position=" + peakpos
    url = local + "/get_top100_sql/search/" + songParms;
  }
  
  populateTable(url);

}

function populateTable(url) {
  d3.json(url).then(function(data) {
    console.log(data);
    console.log(first);
    if (first == true) {generateDropDowns(data);}
    var x = 0;
    for (let element of data) {
      if (x >= 200) { break; }
      x += 1;
      let row = table.insertRow();

      for (i = 0; i < element.length; i++) {
        // console.log(element[i])
        let cell = row.insertCell();
        if (i > 1) {
          cell.setAttribute('style','text-align:center')
        }
        let text = document.createTextNode(element[i]);
        cell.appendChild(text);
      };
    };
  });
}


// Function that will clear out the table from the previous filter
function clearTable(table, table_size) {

  for (var i = 0; i < table_size - 1; i++) {
    table.deleteRow(0);

  }
}
//
// Function call with includ of keyname and output of items selected
// What items were selected by the user?  This function returns those items in an array.
//
function itemsselected(keyname) {
  // clear out the array
  itemselected = [];
  for (var i = 0; i < keyname.options.length; i++) {
    if (keyname.options[i].selected == true) {
      itemselected.push(keyname.options[i].text);
    }
  }
  return itemselected
}
//
//
// Start of main area that sets up the html to start adding the table elements.
// Set table to start after tbody since the header is there already.
//
//

var table = document.querySelector("tbody");

// generate the table the first time the page is loaded.
generateTable();


// filter table based on the input from the user.  Datetime and country are single elements.
// City, state, and shape are multi select and the input is provided in an array where.
// the field option is set to true if it was selected.  This routine is called when the users has
// hit the filter button.
function checkinput() {

  var performerselected = document.getElementById("performerselect").value;
  var songselected = document.getElementById("songselect").value;
  var yearselected = document.getElementById("yearselect").value;
  var peakselected = document.getElementById("peakselect").value;

  var table_size = document.getElementById("song-table").rows.length;
  // console.log("Button Hit", performerselected, songselected, yearselected, peakselected, table_size)

  // clear the table and then check for the right date range.
  clearTable(table, table_size);
 
  generateTable(performerselected, songselected, yearselected, peakselected);

}
function partialInput() {
 
    var partial = document.getElementById("partial").value;
    var table_size = document.getElementById("song-table").rows.length;

    first = false;
    var url = local + '/get_top100_sql/partialsearch/' + partial;

    // clear the table and then check for the right date range.
    clearTable(table, table_size);

    populateTable(url);
  
  }


