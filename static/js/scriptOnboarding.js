/**
 * Created by gebruiker on 13/06/2017.
 */
/* Log in*/

var showLogin = document.querySelector("#showLogin");
var loginForm = document.querySelector("#loginForm");
showLogin.addEventListener("click", function(event){

    loginForm.classList.remove("hidden");
});
