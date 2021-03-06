var itemsPlaylist;
var loginStatus = false;

if (typeof itemsPlaylist === 'undefined') {itemsPlaylist = []}

var table = document.querySelector("tbody");
var cont = document.getElementById('song-table').children;


// Function that will clear out the table from the previous filter
function clearTable(table, table_size) {

  for (var i = 0; i < table_size - 1; i++) {
    table.deleteRow(0);

  }
}
function rebuildList() {
  console.log(cont);
  // clear out the array
  if (cont[1].tagName == 'TBODY') {
    // is the table body empty?
    if (cont[1].childElementCount == 0) {
      alert("No songs left in your playlist.  Please select some.");
      window.location.href='/spot2';
    }
    else {
        // Create a list of items in table
        for (var x = 0; x < cont[1].childElementCount; x++) {
            itemsPlaylist.push({'id':cont[1].children[x].children[1].children[0].id, 'name':cont[1].children[x].children[1].children[0].name})
        }
     } 
    }
  }


// After deleting one or more songs, we need to rebiuld the table body with the songs left in
// the Playlist
function rebuildTable(table) {
  var table_size = document.getElementById("song-table").rows.length;
  clearTable(table,table_size);
  var x = 0;
  for (let element of itemsPlaylist) {
    x += 1;
    let row = table.insertRow();
    let cell = row.insertCell();
    let text = document.createTextNode(element.name) 
    cell.appendChild(text);
    cell = row.insertCell();
    //center the checkbox
    cell.setAttribute('style','text-align:center');

    let check = document.createElement("input");
    check.setAttribute('type','checkbox');
    check.setAttribute('id',element.id);
    check.setAttribute('name', element.name)
    cell.appendChild(check);
  }

}
// Delete the songs that have been identified
function nowDelete() {
  itemsPlaylist = []
  // Clear check if the element is checked in the table body which is offset 1
  for (var x = 0; x < cont[1].childElementCount; x++) {
    if (cont[1].children[x].children[1].children[0].checked != true) {
      itemsPlaylist.push({'id':cont[1].children[x].children[1].children[0].id, 'name':cont[1].children[x].children[1].children[0].name})
    }
  }
  rebuildTable(table);
}

// Reverse the songs that have been identified
function nowRev() {
  itemsPlaylist.reverse();
  rebuildTable(table);
}

//Submit the playlist to spotify.  Ran into an issue as I am not sure I can do this for other users......
function nowLogin() {
  let url = local + '/login'

  d3.json(url).then(function(response) {
    console.log(response)
    if (response.slice(0,10) != "Authorized") {
      location.replace(response)
      };
  })
  .catch(function(error) {console.log('error');
                          console.error(error);
  alert("Error something happened.  Try again");
});
console.log(loginStatus);
loginStatus = true;

}
//Submit the playlist to spotify.  Ran into an issue as I am not sure I can do this for other users......
function nowSubmit() {
 // Calls the functions to submit the list to spotify as a playlist
 var loginStatus = document.getElementById("filter-btn3").value;

 if (loginStatus == 1) {

  var spotifyPlaylist = document.getElementById("playlist").value;

  if (spotifyPlaylist == '' ) {spotifyPlaylist = 'Top100 Billboard PlayList'}

  // Check if there are any items to submit
  if (itemsPlaylist.length  != 0)  {
    var spotifyIds = itemsPlaylist.map(function(item) {
      return item.id;
    });
    let url = local + '/submit/' + spotifyPlaylist
    d3.json(url,{
      headers: {
        'Content-Type': 'application/json'
      },
      redirect: 'follow',
      method: 'POST',

      body:JSON.stringify(spotifyIds)
    }).then(function(response) { 
        console.log(response);
        alert('Playlist created.  Create another or listen on your spotify app and enjoy');
        location.replace(local + '/spot2');
        })
        .catch(function(error) {console.error(error);
        alert("Playlist submit failed.");
        })
        .finally(function(data) { console.log("Redirect", data) });

      // else {
      //   alert("Playlist saved --- enjoy the music");
      //   location.replace(local + '/spot.html?code='+ data);
      // }
    }
  else {
      alert("You need to select some songs by using the check boxes.");
    }
  }
  else {
      
    alert("Log into Spotify first!");
  }
}

  // Rebuild the list.  Need to figure out a better way
rebuildList();


