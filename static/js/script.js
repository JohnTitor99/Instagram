/* POPUPS */

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

// Change profile picture
function changeLogoFunc() {
  document.getElementById("changeLogoDropdown").classList.toggle("show");
}

function switchAccountfunc() {
  document.getElementById("switchAccountDropdown").classList.toggle("show");
}

function otherProfileOptionsFunc() {
  document.getElementById("otherProfileOptions").classList.toggle("show");
}


// hide popup
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

// making submit button inactive until user don't fills form inputs
const registerSubmitButton = document.getElementById("register-submit");
const phone = document.getElementById("phone");
const username = document.getElementById("username");
const password = document.getElementById("password");

let phone_check = false
let username_check = false
let password_check = false

phone.addEventListener("keyup", (e) => {
  const value = e.currentTarget.value;
  if (value === "") {
    phone_check = false;
    registerSubmitButton.disabled = true;
  } else {
    phone_check = true;
    if (phone_check == true && username_check == true && password_check == true) {
      registerSubmitButton.disabled = false;
    }
  }
});

username.addEventListener("keyup", (e) => {
  const value = e.currentTarget.value;
  if (value === "") {
    username_check = false;
    registerSubmitButton.disabled = true;
  } else {
    username_check = true;
    if (phone_check == true && username_check == true && password_check == true) {
      registerSubmitButton.disabled = false;
    }
  }
});

password.addEventListener("keyup", (e) => {
  const value = e.currentTarget.value;
  if (value === "") {
    password_check = false;
    registerSubmitButton.disabled = true;
  } else {
    password_check = true;
    if (phone_check == true && username_check == true && password_check == true) {
      registerSubmitButton.disabled = false;
    }
  }
});
