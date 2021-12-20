$('#basic-addon1').keypress(function(event){
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if(keycode == '13'){}
});

function show_message(message_id){
    var elem = document.getElementById(message_id);
    elem.style.color = "#686868";

    var data = new FormData();
    data.append("message_id", message_id);
    fetch("read_message/", {
        method: "POST",
        body: data,
        contentType: 'application/json',
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken")
        },
    }).then(console.log(true))
}

function del_mail(mail_address){
    $('#delMail').modal('hide');
    document.getElementById("accordionExample").remove();
    document.getElementById("messages-title").textContent = "Messages is not found";
    document.getElementById("mail-"+mail_address).remove();
    var data = new FormData();
    data.append("mail_address", mail_address);
    fetch("del_mail/", {
        method: "POST",
        body: data,
        contentType: 'application/json',
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken")
        },
    }).then(console.log(true))
    window.location.replace("profile");
}

function del_is_not_found_mail(mail_address){
    $('#delMail').modal('hide');
    var data = new FormData();
    data.append("mail_address", mail_address);
    fetch("del_mail/", {
        method: "POST",
        body: data,
        contentType: 'application/json',
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken")
        },
    }).then(console.log(true))
    window.location.replace("profile");
}

function return_main_page(){
    window.location.replace("profile");
}

function getCookie(name) {
    var cookieValue = null;
    var i = 0;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (i; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
});