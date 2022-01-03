$('#basic-addon1').keypress(function (event) {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13') { }
});

function show_message(message_id) {
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
    });
}

function del_mail(mail_address) {
    $('#delMail').modal('hide');
    document.getElementById("accordionExample").remove();
    document.getElementById("messages-title").textContent = "Messages is not found";
    document.getElementById("mail-" + mail_address).remove();
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
    });
    window.location.replace("profile");
}

function del_is_not_found_mail(mail_address) {
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
    });
    window.location.replace("profile");
}

function return_main_page() {
    window.location.replace("profile");
}

function get_file() {
    var file = document.getElementById("file-browser").files[0];
    if (file) {
        var fileNameArray = file.name.split(".");
        if (fileNameArray[fileNameArray.length - 1] != "txt") {
            return alert("Формат файла является неправильным!");
        }
        var fileSize = file.size / 1024 / 1024;
        if (fileSize > 50) {
            return alert("Файл превышает размер!");
        } else {
            $('#addFewAccounts').modal('hide');
            var reader = new FileReader();
            reader.readAsText(file, "UTF-8");
            var result = null;
            reader.onload = function(e) {
                var data = new FormData();
                data.append("content", e.target.result);
                fetch("add_few_accounts", {
                    method: "POST",
                    body: data,
                    contentType: 'application/json',
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                });
                /*var toastTrigger = document.getElementById('liveToastBtn');
                var toastLiveExample = document.getElementById('liveToast');
                if (toastTrigger) {
                        var toast = new bootstrap.Toast(toastLiveExample)
                        toast.show()
                }*/
            }
            //window.location.replace("profile");
        }
    }
    else {
        return alert("Файл отсутствует!");
    }
}

function del_all_accounts(){
    fetch("del_all_accounts", {
        method: "POST",
        contentType: 'application/json',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken")
        },
    });
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