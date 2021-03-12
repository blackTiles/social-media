function signUp(){
    let feed = document.querySelector('#cont-feed');
    let form = document.querySelector('#cont-form');
    let loginPage = document.querySelector('#login');
    let signupPage = document.querySelector('#signup');
    let x = document.querySelector('#mobilenav');
    x.style.display="none";
    loginPage.style.display="none";
    signupPage.style.display="inline-block";
    feed.style.display="none";
    form.style.display="flex"; 
}
function logIn(){
    let feed = document.querySelector('#cont-feed');
    let form = document.querySelector('#cont-form');
    let loginPage = document.querySelector('#login');
    let signupPage = document.querySelector('#signup');
    let x = document.querySelector('#mobilenav');
    x.style.display="none";
    signupPage.style.display="none";
    loginPage.style.display="inline-block";  
    feed.style.display="none";
    form.style.display="flex"; 
}
function next(){
    let prePage = document.querySelector('#partone');
    let nextPage = document.querySelector('#parttwo');
    prePage.style.display="none";
    nextPage.style.display="inline-block";
}
function pre(){
    let prePage = document.querySelector('#partone');
    let nextPage = document.querySelector('#parttwo');
    nextPage.style.display="none";
    prePage.style.display="inline-block";
    prePage.style.paddingBottom="10px";
}
function navMobile(){
    let x = document.querySelector('#mobilenav');
    if(x.style.display="none"){
        x.style.display="block";
    }
    else{
        x.style.display="none";
    }
}
function closeNavMobile(){
    let x = document.querySelector('#mobilenav');
    x.style.display="none";
}
function postReveal(){
    let f = document.querySelector('#blogpost');
    let g = document.querySelector('#button-post');
    if (f.style.display === "block") {
        f.style.display = "none";
        g.innerHTML="Add a New Post";
    } else {
        f.style.display = "block";
        g.innerHTML="Close";
    }
}
function feedRun(){
    let feed = document.querySelector('#cont-feed');
    let form = document.querySelector('#cont-form');
    let x = document.querySelector('#mobilenav');
    x.style.display="none";
    feed.style.display="block";
    form.style.display="none";
}