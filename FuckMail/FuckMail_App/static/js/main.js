$('#basic-addon1').keypress(function(event){
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if(keycode == '13'){}
});

/*function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

function remove_message(){
    await sleep(2000);
    var elem = document.getElementById("message");
    elem.parentNode.removeChild(elem);
    return false;
};*/

function check_work(){
    alert(true);
    return true;
}