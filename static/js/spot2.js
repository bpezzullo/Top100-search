// from set up global variables used through out the JS functions.


var songkey = [], sox, songselected = [];
var perfkey = [], pex, perfselected = [];
var weekkey = [], wex, weekselected = [];
var peakkey = [], pox, peekselected = [];

var itemsPlaylist;

if (typeof itemsPlaylist === 'undefined') {itemsPlaylist = []}

var itemselected = [];
var saved_url;


var table = document.querySelector("tbody");

// function to generate the text for the drop downs.

function generatetxt(keylist) {

  var text, i;

  // start the dropdown list with All.
  text = "<option value = 'All' >All</option>"

  // loop through array to populate the drop down.
  for (i = 0; i < keylist.length; i++) {
    text += "<option>" + keylist[i] + "</option>";
  }
  return text
}


// create the drop downlists
function generateDropDowns() {
  // loop through the data to find the information needed for the drop down lists for the 
  // song names, performers, top positions and weekid

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

  weekurl = local + "/get_top100_sql/weekid/*"
  d3.json(weekurl).then(function (data) {

    data.forEach(datarow => {
      wox = (datarow[1]);
      if (weekkey.indexOf(wox) === -1) {
        weekkey.push(wox);
      }
    });

    document.getElementById("weekselect").innerHTML = generatetxt(weekkey);
  });

  for (var i = 1; i < 101; i++) {
    peakkey.push(i)
  };


  document.getElementById("peakselect").innerHTML = generatetxt(peakkey);


}


// Function that builds the table with song information.

function generateTable(table, performer = 'All', song = 'All', week = 'All', peakpos = 'All', startloc = 0) {
  var urlData = ''
  if (week != 'All') {
    urlData = 'week='+ week
  }
  else {
    urlData = 'performer=' + performer + '/name=' + song + '/top_position=' + peakpos + '/start=' + startloc
  }

  url = local + "/get_top100_sql/select/" + urlData;


  d3.json(url).then(function(data) {
    // console.log(data);
    var x = 0;
    for (let element of data) {
      x += 1;
      let row = table.insertRow();
      for (i = 0; i < element.length; i++) {
        // console.log(element[i])
        let cell = row.insertCell();
        if (i > 1) {
          cell.setAttribute('style','text-align:center')
        }
        if (i == element.length - 1) {
          // console.log(element[i]);
          if (element[i] != null) {
            // let text = document.createElement('<input id="' + element[i] + '" type="checkbox"></input>');
            let check = document.createElement("input");
            check.setAttribute('type','checkbox');
            check.setAttribute('id',element[i]);
            check.setAttribute('value', element[0]);
            cell.appendChild(check);}
          else {
            let text = document.createTextNode("n/a");
            cell.appendChild(text);
          }
        }
        else {
          let text = document.createTextNode(element[i]);
          cell.appendChild(text);}
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
//
// Start of main area that sets up the html to start adding the table elements.
// generate the table the first time the page is loaded.

generateDropDowns();


// This routine is called when the users has
// hit the save button.
function nowCheck() {
  // Get all the child elements inside the container.
  var cont = document.getElementById('song-table').children;
  let saved = false
  // console.log(cont);
  for (var i = 0; i < cont.length; i++) {
      // Check if the element is a checkbox.
      // console.log(cont[i]);
      if (cont[i].tagName == 'TBODY') {

          for (var x = 0; x < cont[i].childElementCount; x++) {
            if (cont[i].children[x].children[5].children[0] == undefined) {continue}
            if (cont[i].children[x].children[5].children[0].checked && cont[i].children[x].children[5].children[0].id != 'null') {
              itemsPlaylist.push({'id':cont[i].children[x].children[5].children[0].id, 'name':cont[i].children[x].children[5].children[0].value});
              saved = true
          }
        }
      }
      else {
        // select all the songs on the page.  For now I know the second entry is the body tag
        if (cont[i].children[0].children[5].children[0].checked) {
          for (var x = 0; x < cont[1].childElementCount; x++) {
            if (cont[1].children[x].children[5].children[0] == undefined) {continue}
              if (cont[1].children[x].children[5].children[0].id != 'null') {
               itemsPlaylist.push({'id':cont[1].children[x].children[5].children[0].id, 'name':cont[1].children[x].children[5].children[0].value});
               saved=true
              }
          }
          break;
        }
      }

  }
  if (!saved) { alert("You need to select some songs by using the check boxes.");}

}
// Search was selected
function checkinput() {

  var performerselected = document.getElementById("performerselect").value;
  var songselected = document.getElementById("songselect").value;
  var weekselected = document.getElementById("weekselect").value;
  var peakselected = document.getElementById("peakselect").value;

  var table_size = document.getElementById("song-table").rows.length;
  // console.log("Button Hit", performerselected, songselected, yearselected, peakselected, table_size)

  // clear the table and then check for the right date range.
  clearTable(table, table_size);
 
  generateTable(table, 
                performer = performerselected, 
                song = songselected, 
                week = weekselected, 
                peak = peakselected,
                startloc = 0);

}
function nowClear() {
  // clear out the array
  itemsPlaylist = [];
  var cont = document.getElementById('song-table').children;
  console.log(cont);
  for (var i = 0; i < cont.length; i++) {
      // Check if the element is a checkbox.
      console.log(cont[i]);
      for (var x = 0; x < cont[i].childElementCount; x++) {
        if (cont[i].children[x].children[5].children[0] == undefined) {continue}
        cont[i].children[x].children[5].children[0].checked = false
      }
  }
}
function nowView() {
  // Display the array
  if (itemsPlaylist.length  != 0)  {

      url = local + '/view'
      fetch(url,{
        headers: {
          'Content-Type': 'application/json'
        },
        method: 'POST',

        body:JSON.stringify(itemsPlaylist)
    
    }).then(function(data) {
      console.log(data);
      location.replace(data.url);
    })
  //   fetch(url).then(function(response) {

  //   location.replace(local + '/view.html');
  // })

    }
  else {
      alert("You need to select some songs by using the check boxes.");
    }
}

function nowNext() {
  // next 100
  alert("This function coming in next version.");
}

function nowPrev() {
  // next 100
  alert("This function coming in next version.");
}


