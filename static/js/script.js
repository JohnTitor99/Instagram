// OPEN DROPDOWNS

// ----- NAVBAR DROPDOWNS-----
// notifications
function showNotificationsFunc() {
    document.getElementById("notificationsDropdownId").classList.remove("hide");
    document.getElementById("notificationsDropdownId").classList.toggle("show");
}

  // creating a post
function postCreateDropdownFunc() {
    document.getElementById("postCreateDropdownId").classList.remove("hide");
    document.getElementById("postCreateDropdownId").classList.toggle("show");

    // show a select from computer btn
    document.getElementById("postCreateSelectBtnId").classList.remove("hide");

    let name = document.getElementById('postCreateImageId');
    
    document.getElementById("postCreateUserLogoId").setAttribute('src', request_user_logo);
    document.getElementById("postCreateUserNameId").textContent = request_user;
}

// user menu dropdown
function userMenuDropdownFunc() {
    document.getElementById("userMenuDropdownId").classList.remove("hide");
    document.getElementById("userMenuDropdownId").classList.toggle("show");
}

// switch account dropdown
function switchAccountDropdownFunc() {
    document.getElementById("switchAccountDropdown").classList.remove("hide");
    document.getElementById("switchAccountDropdown").classList.toggle("show");
}



// ----- POST AND POST COMMENTS OPTIONS -----
// my post options dropdown
function myPostOptionsDropdownFunc(postId, postImage, postText) {
    document.getElementById("myPostOptionsDropdownId").classList.remove("hide");
    document.getElementById("myPostOptionsDropdownId").classList.toggle("show");
    // onclick value to post delete btn
    document.getElementById("postDeleteBtnId").setAttribute('onclick', 'postDeleteDropdownFunc()');
    // onclick value for post edit
    document.getElementById("postEditBtnId").setAttribute('onclick', `postEditDropdownFunc('${ postId }', '${ postImage }', '${ postText }')`);
    // confirm value to post delete confirm btn
    document.getElementById("postDeleteConfirmLinkId").setAttribute('href', '/delete-post/' + postId + '/');
    // link to go_to_post btn
    document.getElementById("myPostGoToPostLinkId").setAttribute('href', '/p/' + postId + '/');
}

// editing a post
function postEditDropdownFunc(postId, postImage, postText) {
    document.getElementById("postEditDropdownId").classList.remove("hide");
    document.getElementById("postEditDropdownId").classList.toggle("show");
    
    document.getElementById("postEditImageId").setAttribute('src', postImage);
    document.getElementById("postEditUserLogoId").setAttribute('src', request_user_logo);
    document.getElementById("postEditUserNameId").textContent = request_user;

    document.getElementsByClassName("post-edit-textarea-class")[0].textContent = ""

    if (postText != 'None') {
        document.getElementsByClassName("post-edit-textarea-class")[0].textContent += postText + " ";
    }
    let change_quotes_hashtags = hashtagsJson.replaceAll("'", '"');
    let array_of_hashtags = JSON.parse(change_quotes_hashtags);
    for (let i = 0; i < array_of_hashtags.length; i++) {
        if (array_of_hashtags[i][postId] != undefined) {
            for (let n = 0; n < array_of_hashtags[i][postId].length; n++) {
                document.getElementsByClassName("post-edit-textarea-class")[0].textContent += "#" + array_of_hashtags[i][postId][n] + " ";
            }
        }
    }
    document.getElementById("postEditPostId").setAttribute('value', postId);

}

// other post options dropdown
function otherPostOptionsDropdownFunc(postId, postUserId) {
    document.getElementById("otherPostOptionsDropdownId").classList.remove("hide");
    document.getElementById("otherPostOptionsDropdownId").classList.toggle("show");
    // set link to go_to_post btn
    document.getElementById("otherPostGoToPostLinkId").setAttribute('href', '/p/' + postId + '/');
    // set value to other post unfollow form hidden input
    document.getElementById("otherPostUnfollowFormInputId").setAttribute('value', postUserId);
}

// post options dropdown in go to post
function goToPostOptionsDropdownFunc(postId) {
    document.getElementById("goToPostOptionsDropdownId").classList.remove("hide");
    document.getElementById("goToPostOptionsDropdownId").classList.toggle("show");
}

// post comments dropdown
function postCommentsDropdownFunc(postId, postImage, postUser, postUserId, postUserLogo, postText) {
    // show dropdown
    document.getElementById("postCommentsDropdownId").classList.remove("hide");
    document.getElementById("postCommentsDropdownId").classList.toggle("show");

    // set post image
    document.getElementById("postCommentsPostImageId").setAttribute('src', postImage);

    // set post comment form
    document.getElementsByName("post-id")[0].value = postId;

    // set hashtags
    let change_quotes_hashtags = hashtagsJson.replaceAll("'", '"');
    let array_of_hashtags = JSON.parse(change_quotes_hashtags);
    for (let i = 0; i < array_of_hashtags.length; i++) {
        if (array_of_hashtags[i][postId] != undefined) {
            for (let n = 0; n < array_of_hashtags[i][postId].length; n++) {
                hashtag = `
                    <a href="/explore/tags/${ array_of_hashtags[i][postId][n] }/">#${ array_of_hashtags[i][postId][n] }</a>`;
                document.getElementById("postCommentsHashtagsBlockId").insertAdjacentHTML('afterbegin', hashtag);
            }
        }
    }

    document.getElementById("postCommentsLikesDropdownId").setAttribute('href', `javascript: usersWhoLikedPostFunc(${ postId })`);
    document.getElementsByClassName("postCommentsTextFieldClass")[0].setAttribute('id', 'addCommentInputId' + postId);
    

    if (document.getElementsByName("comment-id")[0].value == "") {
        document.getElementsByName("comment-id")[0].setAttribute('id', 'commentId' + postId);
    } else {
        document.getElementById("addCommentInputId" + postId).value = "";
    }
    // set username, logos, links
    let postCommentsProfileLinks = document.getElementsByClassName("postCommentsProfileLinkClass");
    let postCommentsUserNames = document.getElementsByClassName("postCommentsUserNameClass");
    let postCommentsUserLogos = document.getElementsByClassName("postCommentsUserLogoClass");

    for (let i = 0; i < postCommentsProfileLinks.length; i++) {
        postCommentsUserNames[i].textContent = postUser;
        postCommentsProfileLinks[i].setAttribute('href', `/${postUser}/`);
        postCommentsUserLogos[i].setAttribute('src', postUserLogo);
    }

    // post text
    if (postText != 'None') {
        document.getElementById("postCommentsPostTextId").innerHTML = "";
        document.getElementById("postCommentsPostTextId").innerHTML += postText;
    }

    // set post options buttons
    if (request_user == postUser) {
        document.getElementById("postCommentsPostOptionsId").setAttribute('onclick', `myPostOptionsDropdownFunc('${ postId }', '${ postImage }', '${ postText }')`);
    } else {
        document.getElementById("postCommentsPostOptionsId").setAttribute('onclick', `otherPostOptionsDropdownFunc(${ postId }, ${ postUserId })`);
    }

    // insert comments
    let change_quotes_comments = comments_json.replaceAll("'", '"');
    let array_of_comments = JSON.parse(change_quotes_comments);

    if (document.getElementById("postCommentsCommentId").innerHTML == "") {
        for (let i = 0; i < array_of_comments.length; i++) {
            let obj = array_of_comments[i]
            // insert comment block
            if (String(obj['fields']['post']) == postId) {
                let commentBlock = `
                <div style="height: 100%; width: 100%;">
                    <a href="/${ obj['adj_dict']['username'] }/">
                        <img src="/${ obj['adj_dict']['logo'] }"/>
                    </a>
                    <p class="post-comment-body-p"><b>${ obj['adj_dict']['username'] }</b> ${ obj['fields']['body'] }</p>

                    <!-- comment created date, reply and options buttons -->
                    <div class="comment-created-replies">
                        <small>${ obj['adj_dict']['created'] }
                            <input type="button" onclick="commentReplyFunc('${ postId }', '${ obj['adj_dict']['username'] }', '${ obj['pk'] }')" value="Reply"/>
                            <input type="button" onclick="commentOptionsFunc('${ obj['pk'] }')" value="•••"/>
                        </small>
                    </div>

                    <!-- comments options dropdown-->
                    <div class="dropdown">
                        <div id="commentOptionsDropdown${ obj['pk'] }" class="dropdown-content hide">
                            <div id="commentOptionsDropdownDarkBackgroundId" class="x1ey2m1c xds687c xixxii4 x17qophe x13vifvy x1h0vfkc"></div>
                            <div class="comment-options-dropdown-content">
                                <!-- delete button is only for my comments -->
                                ${ obj['fields']['user'] == request_user_id ? `<a href="/delete-comment/${ obj['pk'] }/"><b style="color: red;">Delete</b></a><hr></hr>`:''}
                                <a href="javascript:hidePopupFunc()">Cancel</a>
                            </div>
                        </div>
                    </div>

                    <div id="replyBlockId${ obj['pk'] }" class="reply-block"></div>
                </div>`
                document.getElementById("postCommentsCommentId").insertAdjacentHTML('beforeend', commentBlock);

                // insert replies if they are
                if (obj['replies'].length > 0) {
                    let hideShowRepliesBtn = `<input type="button" id="viewHideRepliesBtnId${ obj['pk'] }" onclick="viewHideRepliesFunc(${ obj['pk'] }, ${ obj['replies'].length })"
                    class="view-hide-replies" value="----- View replies (${ obj['replies'].length })"/>
                    `
                    document.getElementById(`replyBlockId${ obj['pk'] }`).insertAdjacentHTML('beforebegin', hideShowRepliesBtn);
                    for (let i = 0; i < obj['replies'].length; i++) {
                        let repliesBlock = `
                        <div>
                            <a href="/${ obj['replies'][i]['username'] }/">
                                <img src="/${ obj['replies'][i]['logo'] }"/>
                            </a>
                            <p class="post-comment-body-p">
                                <b>${ obj['replies'][i]['username'] }</b> @${ obj['replies'][i]['related_username'] } ${ obj['replies'][i]['body'] }
                            </p>

                            <!-- reply created date, reply and options buttons -->
                            <div class="comment-created-replies">
                                <small>${ obj['replies'][i]['created'] }
                                    <input type="button" onclick="commentReplyFunc('${ postId }', '${ obj['replies'][i]['username'] }', '${ obj['pk'] }')" value="Reply"/>
                                    <input type="button" onclick="replyOptionsFunc('${ obj['replies'][i]['pk'] }')" value="•••"/>
                                </small>
                            </div>
                            
                            <!-- REPLY OPTIONS DROPDOWN-->
                            <div class="dropdown">
                                <div id="replyOptionsDropdown${ obj['replies'][i]['pk'] }" class="dropdown-content hide">
                                <div id="replyOptionsDropdownDarkBackgroundId" class="x1ey2m1c xds687c xixxii4 x17qophe x13vifvy x1h0vfkc"></div>
                                    <div class="reply-options-dropdown-content">
                                        ${ obj['replies'][i]['user'] == request_user_id ? `<a href="/delete-reply/${ obj['replies'][i]['pk'] }/"><b style="color: red;">Delete</b></a><hr></hr>`: ''}
                                        <a href="javascript:hidePopupFunc()">Cancel</a>
                                    </div>
                                </div>
                            </div>
                        </div>`
                        let replyBlockHTML = document.getElementById(`replyBlockId${ obj['pk'] }`).innerHTML;
                        document.getElementById(`replyBlockId${ obj['pk'] }`).innerHTML = replyBlockHTML + repliesBlock;
                    }
                }
            }
        }
    }

    // parse json posts_data
    let posts_data_json = JSON.parse(posts_data.replaceAll("'", '"'));

    // post created
    document.getElementById("postCommentsHeaderPostCreatedId").innerHTML = posts_data_json[postId]['created'];

    // setting actions block
    if (document.getElementById("postCommentsPostActionsId").innerHTML == "") {
        // set like and unlike forms
        document.getElementsByClassName("postCommentslikeFormId")[0].setAttribute('id', `likeFormId${ postId }`);
        document.getElementsByClassName("postCommentslikeFormId")[0].setAttribute('action', `/post-action/${ postId }/`);
        document.getElementsByClassName("postCommentsUnlikeFormId")[0].setAttribute('id', `unLikeFormId${ postId }`);
        document.getElementsByClassName("postCommentsUnlikeFormId")[0].setAttribute('action', `/post-action/${ postId }/`);

        document.getElementById("postCommentsLikesCountId").innerHTML = "";
        document.getElementById("postCommentsLikesCountId").innerHTML += posts_data_json[postId]['total_likes'] + " likes";
        
        document.getElementById("postCommentsLikesDropdownId").setAttribute('href', '');
        document.getElementById("postCommentsLikesDropdownId").setAttribute('href', `javascript: usersWhoLikedPostFunc('${ postId }')`);


        document.getElementById("postCommentsCreatedId").innerHTML = "";
        document.getElementById("postCommentsCreatedId").innerHTML += posts_data_json[postId]['created'];

        let likeBtnForPostComments = document.getElementById(`likeLabelId${ postId }`).innerHTML;
        let saveBtnForPostComments = document.getElementById(`saveLabelId${ postId }`).innerHTML;
        let actionsBlock = `
        <div>
            <hr>

            <section class="_aamu _ae3_ _ae40 _ae41 _ae48">
                <!-- like button -->
                <span class="_aamw">
                    <label style="cursor: pointer;" id="postCommentsLikeLabelId${ postId }">
                        ${ likeBtnForPostComments }
                    </label>
                </span>

                <!-- comments button -->
                <span>
                    <label style="cursor: pointer;">
                        <input type="button" class="dropbtn _abl-" onclick="">
                        <svg aria-label="Comment" class="_ab6-" color="#262626" height="24" role="img" viewBox="0 0 24 24" width="24">
                            <path d="M20.656 17.008a9.993 9.993 0 1 0-3.59 3.615L22 22Z" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="2">
                            </path>
                        </svg>
                    </label>
                </span>

                <!-- share button -->
                <span class="_aamy">
                    <label style="cursor: pointer;">
                        <input type="button" class="_abl-" onclick="">
                        <svg aria-label="Share Post" class="_ab6-" color="#262626" fill="#262626" height="24" role="img" viewBox="0 0 24 24" width="24">
                        <line fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="2" x1="22" x2="9.218" y1="3" y2="10.083">
                        </line>
                        <polygon fill="none" points="11.698 20.334 22 3.001 2 3.001 9.218 10.084 11.698 20.334" stroke="currentColor" stroke-linejoin="round" stroke-width="2">
                        </polygon>
                        </svg>
                    </label>
                </span>

                <!-- save button -->
                <span class="_aamz">
                    <label style="cursor: pointer;" id="postCommentsSaveLabelId${ postId }">
                        ${ saveBtnForPostComments }
                    </label>
                </span>
            </section>


        </div>`
        document.getElementById("postCommentsPostActionsId").insertAdjacentHTML('afterbegin', actionsBlock);
    }
}

// comments options
function commentOptionsFunc(commentId) {
    document.getElementById("commentOptionsDropdown" + commentId).classList.remove("hide");
    document.getElementById("commentOptionsDropdown" + commentId).classList.toggle("show");
}

// replys options
function replyOptionsFunc(replyId) {
    document.getElementById("replyOptionsDropdown" + replyId).classList.remove("hide");
    document.getElementById("replyOptionsDropdown" + replyId).classList.toggle("show");
}

// post delete confirm
function postDeleteDropdownFunc() {
    document.getElementById("postDeleteDropdownId").classList.remove("hide");
    document.getElementById("postDeleteDropdownId").classList.toggle("show");
}

// users who liked a post
function usersWhoLikedPostFunc(postId) {
    document.getElementById("usersWhoLikedPostDropdown").classList.remove("hide");
    document.getElementById("usersWhoLikedPostDropdown").classList.toggle("show");

    let change_quotes_likes = likesJson.replaceAll("'", '"');
    let likes_array = JSON.parse(change_quotes_likes);

    for (let i = 0; i < likes_array.length; i++) {
        obj = likes_array[i];

        if (obj['post_id'] == postId) {
            let likeUser = `
            <div style="margin-bottom: 30px;">
                <a href="/profile/${ obj['username'] }/" style="text-decoration: none; color: black;"><img src="/${ obj['logo'] }"/>
                    <p><b>${ obj['username'] }</b></p>
                </a>
            </div>`
            document.getElementById("usersWhoLikesPostDropbdownId").innerHTML += likeUser;
        }
    }
}



// ----- PROFILE DROPDOWNS-----
  // profile settings
function profileSettingsDropdownFunc() {
    document.getElementById("profileSettingsDropdownId").classList.remove("hide");
    document.getElementById("profileSettingsDropdownId").classList.toggle("show");
}

// show list of my followers
function showMyFollowersDropdownFunc() {
    document.getElementById("showMyFollowersDropdownId").classList.remove("hide");
    document.getElementById("showMyFollowersDropdownId").classList.toggle("show");
}

// show list of my following
function showMyFollowingDropdownFunc() {
    document.getElementById("showMyFollowingDropdownId").classList.remove("hide");
    document.getElementById("showMyFollowingDropdownId").classList.toggle("show");
}

// show list of other user followers
function showOtherUserFollowersDropdownFunc() {
    document.getElementById("showOtherUserFollowersDropdownId").classList.remove("hide");
    document.getElementById("showOtherUserFollowersDropdownId").classList.toggle("show");
}

// show list of other user following
function showOtherUserFollowingDropdownFunc() {
    document.getElementById("showOtherFollowingDropdownId").classList.remove("hide");
    document.getElementById("showOtherFollowingDropdownId").classList.toggle("show");
}

// change profile picture
function changeLogoDropdownFunc() {
    document.getElementById("changeLogoDropdownId").classList.remove("hide");
    document.getElementById("changeLogoDropdownId").classList.toggle("show");
}




// ----- DIRECT DROPDOWNS-----
// options of sended or received message
function messsageOptionsFunc(messageId) {
    document.getElementById("messageOptionsDropdown" + messageId).classList.toggle("show");
}
  
  // dropdown confirm for delete a message
function unsendMessageFunc(messageId) {
    document.getElementById("unsendMessageDropdown" + messageId).classList.toggle("show");
}

// dropdown for choose a user for send a message
function sendMessageDropdownFunc() {
    document.getElementById("sendMessageDropdown").classList.remove("hide");
    document.getElementById("sendMessageDropdown").classList.toggle("show");
}





  











// CLOSE DROPDOWNS

// close by click on cancel button
function hidePopupFunc() {
    if (document.getElementById("postCommentsCommentId") != null) {
        document.getElementById("postCommentsCommentId").innerHTML = "";
        document.getElementById("postCommentsPostActionsId").innerHTML = "";
        document.getElementById("usersWhoLikesPostDropbdownId").innerHTML = ""
        document.getElementById("postCommentsHashtagsBlockId").innerHTML = "";
        document.getElementById("postCreateSelectBtnId").classList.toggle("hide");
        document.getElementById("postCreateImagePreviewId").setAttribute('src', '');
        document.getElementById("postCreateTextareaId").value = '';
    }

    // clearing elements in goToPost
    if (document.getElementById("goToPostCommentId") != null) {
        document.getElementById("usersWhoLikesPostDropbdownId").innerHTML = ""
    }

    // document.getElementsByClassName("post-edit-textarea-class")[0].textContent = "";

    var dropdowns = document.getElementsByClassName('dropdown-content');
    var i;
    for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
            openDropdown.classList.remove('show');
            openDropdown.classList.toggle('hide');
        }
    }
}








// REPLIES

// paste a user's comment's name to reply
function commentReplyFunc(postId, userToReply, commentId) {
    document.getElementById("addCommentInputId" + postId).value = `@${userToReply} `;
    document.getElementById("commentId" + postId).value = commentId;
}

// view/hide replies
function viewHideRepliesFunc(comId, repliesLength) {
    // get the css display value of a div
    let x = document.getElementById("replyBlockId" + comId);
    style = window.getComputedStyle(x),
    display = style.getPropertyValue('display');

    if (display === "none") {
      x.style.display = "block";
      document.getElementById("viewHideRepliesBtnId" + comId).value = `----- Hide replies (${repliesLength})`;
    } else {
      x.style.display = "none";
      document.getElementById("viewHideRepliesBtnId" + comId).value = `----- View replies (${repliesLength})`;
    }
}




  

// FORM SUBMITTING

// submit a search user form
function searchDropdownFunc() {
    let searchForm = document.getElementById("searchFormId");
    searchForm.submit();
}

// submit following form
function followingFormFunc(suggestedUserId) {
    let followingForm = document.getElementById("followingFormId" + suggestedUserId);
    followingForm.submit();
}

// submit post edit form
function postEditFormFunc() {
    let postEditForm = document.getElementById("postEditFormId");
    postEditForm.submit();
}

// submit post create form
function postCreateFormFunc() {
    let postCreateForm = document.getElementById("postCreateFormId");
    postCreateForm.submit();
}

// submit follow unfollow following form
function followUnfollowFollowingForm() {
    let followUnfollowFollowingForm = document.getElementById("followUnfollowFollowingFormId");
    followUnfollowFollowingForm.submit();
}

function profileEditForm() {
    let profileEditForm = document.getElementById("profileEditFormId");
    profileEditForm.submit();
}











// HASHTAGS

// add hashtag to post edit
function postEditAddHashtag(hashtag) {
    let value = document.getElementById("postEditTextareaId").value;
    document.getElementById("postEditTextareaId").value = value + "#" + hashtag + " ";
}

// add hashtag in post create dropdown
function postCreateAddHashtag(hashtag) {
    let value = document.getElementById("postCreateTextareaId").value;
    document.getElementById("postCreateTextareaId").value = value + "#" + hashtag + " ";
}











// MAKING SUBMIT BUTTON ON REGISTER PAGE INACTIVE UNTIL USER DOESN'T FILL FORM INPUTS

// submit button and fileds ids
const registerSubmitButton = document.getElementById("register-submit");
const phone = document.getElementById("phone");
const username = document.getElementById("username");
const password = document.getElementById("password");

// labels ids
const phoneLabel = document.getElementById("registerPagePhoneLabelId");
  
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
            phoneLabel.classList.toggle("hide");
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