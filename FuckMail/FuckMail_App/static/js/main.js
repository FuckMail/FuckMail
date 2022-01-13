$('#basic-addon1').keypress(function (event) {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13') { }
});

$(document).on("contextmenu", ".list-group-item", function(e){
    var mails_count_number = document.getElementById("title-mails-count");
    mails_count_number.innerText = `📨Mails - ${ mails_count_number.innerText.split("-")[1] - 1 }`;
    var x = event.clientX, y = event.clientY,
    mail_address = document.elementFromPoint(x, y);
    mail_address.remove();
    var data = new FormData();
    data.append("mail_address", mail_address.value);
    fetch("del_mail_from_list/", {
        method: "POST",
        body: data,
        contentType: 'application/json',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken")
        },
    });
    return false;
});

function redirect_to_main_page() {
    window.location.replace("profile");
};

function add_account_modal(){
    $('#myModal').modal('show');
}

function add_few_accounts_modal(){
    $('#addFewAccounts').modal('show');
}

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
};

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
    redirect_to_main_page();
};

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
    redirect_to_main_page();
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
            reader.onload = function(e) {
                var data = new FormData();
                data.append("content", e.target.result);
                fetch("add_few_accounts/", {
                    method: "POST",
                    body: data,
                    contentType: 'application/json',
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken")
                    }
                }).then(function(response){
                    console.log(response.json().then(
                        function(data){
                            if (data == true){
                                redirect_to_main_page();
                            }
                        }
                    ));
                });
            }
        }
    }
    else {
        return alert("Файл отсутствует!");
    }
}

function del_all_accounts(){
    fetch("del_all_accounts/", {
        method: "POST",
        contentType: 'application/json',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken")
        },
    });
    redirect_to_main_page();
}

function help_addFileFormat(){
    window.location.href = "help/add_file_format.html";
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