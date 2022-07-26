/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */

// Owner's posts options
function postOptionsFunc(postId) {
  document.getElementById("postOptionsDropdown" + postId).classList.toggle("show");
}

 //Other posts options
function postOptionsFunc2(postId) {
  document.getElementById("postOptionsDropdown2" + postId).classList.toggle("show");
}

// User menu
function userMenuFunc() {
  document.getElementById("userMenuDropdown").classList.toggle("show");
}

// Creating a post
function postCreateFunc() {
  document.getElementById("postCreateDropdown").classList.toggle("show");
}

// Deleting a post
function postDeleteFunc(postId) {
  document.getElementById("postDeleteDropdown" + postId).classList.toggle("show");
}

// Editing a post
function postEditFunc(postId) {
  document.getElementById("postEditDropdown" + postId).classList.toggle("show");
}

// Post comments
function postCommentsFunc(postId) {
  document.getElementById("postCommentsDropdown" + postId).classList.toggle("show");
}

// Users who liked a post
function usersWhoLikedPostFunc(postId) {
  document.getElementById("usersWhoLikedPostDropdown" + postId).classList.toggle("show");
}

// Owner's comments options
function commentOptionsFunc(commentId) {
  document.getElementById("commentOptionsDropdown" + commentId).classList.toggle("show");
}

// Other commnets options
function commentOptionsFunc2(commentId) {
  document.getElementById("commentOptionsDropdown2" + commentId).classList.toggle("show");
}

// Profile settings
function profileSettings() {
  document.getElementById("profileSettingsDropdown").classList.toggle("show");
}


function hidePopupFunc() {
  var dropdowns = document.getElementsByClassName('dropdown-content');
  var i;
  for (i = 0; i < dropdowns.length; i++) {
    var openDropdown = dropdowns[i];
    if (openDropdown.classList.contains('show')) {
      openDropdown.classList.remove('show');
    }
  }
}


/* Close the dropdown menu if the user clicks outside of it */
window.onclick = function(event) {
  if (!event.target.matches('.dropbtn')) {
    const isInside = event.target.closest('.dropdown-content')

    const dropdowns = document.getElementsByClassName('dropdown-content');
    for (let i = 0; i < dropdowns.length; i++) {
      let openDropdown = dropdowns[i];
      if (openDropdown.classList.contains('show') && !isInside) {
        openDropdown.classList.remove('show');
      }
    }
  }
}
