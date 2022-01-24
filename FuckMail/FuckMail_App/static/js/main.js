setInterval(getNewMessages, 5000);

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

// All modals
function add_account_modal(){
    $("#myModal").modal("show");
}

function add_few_accounts_modal(){
    $("#addFewAccounts").modal("show");
}

function deleteAllAccounts_modal(){
    $("#deleteAllAccounts").modal("show")
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
    }).then(function(response){
        response.json().then(
            function(data){
                if (data == true){
                    redirect_to_main_page();
                }
            }
        );
    });
}

function get_file() {
    var file = document.getElementById("file").files[0];
    console.log(file);
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
                    response.json().then(
                        function(data){
                            if (data == true){
                                redirect_to_main_page();
                            }
                        }
                    );
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
    }).then(function(response){
        response.json().then(
            function(data){
                if (data==true){
                    redirect_to_main_page();
                }
            }
        )
    });
}

function help_addFileFormat(){
    window.location.href = "help/add_file_format.html";
}

function getNewMessages(){
    var mail_address = document.getElementById("mail_address");
    if (mail_address != null){
        var data = new FormData();
        data.append("mail_address", mail_address.textContent);
        fetch("get_new_messages/", {
            method: "POST",
            body: data,
            contentType: 'application/json',
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken")
            },
        }).then(function(response){
            response.json().then(
                function(data){
                    if (data["messages"] != ""){
                        var accordion = document.querySelector("#accordionExample");
                        var card = document.createElement('div');
                        card.className = "card";
                        var newMessageElement_H5 = document.createElement('h5');
                        var newMessageElement_INPUT = document.createElement('input');
                        newMessageElement_INPUT.id = data["messages"]["message_id"];
                        newMessageElement_INPUT.type = "submit";
                        newMessageElement_INPUT.className = "list-group-item list-group-item-action shadow p-3 mb-2 bg-white rounded font-weight-bold";
                        newMessageElement_INPUT.value = `${data["messages"]["from_user"]} - ${data["messages"]["subject"]}`;
                        newMessageElement_INPUT.title = data["messages"]["subject"];
                        newMessageElement_INPUT.style = "color: #000000;";
                        newMessageElement_INPUT.innerHTML = "This is message";
                        newMessageElement_INPUT.setAttribute("data-target", `#collapse${data["messages"]["message_id"]}`);
                        newMessageElement_INPUT.setAttribute("data-toggle", "collapse");
                        newMessageElement_INPUT.setAttribute("onclick", "show_message(this.id);");
                        newMessageElement_INPUT.setAttribute("aria-expanded", "true");
                        newMessageElement_INPUT.setAttribute("data-placement", "right");
                        newMessageElement_INPUT.setAttribute("aria-controls", `collapse${data["messages"]["message_id"]}`);

                        var newMsgElement_1 = document.createElement("div");
                        newMsgElement_1.id = `collapse${data["messages"]["message_id"]}`
                        newMsgElement_1.className = "collapse";
                        newMsgElement_1.setAttribute("aria-labelledby", `heading${data["messages"]["message_id"]}`);
                        newMsgElement_1.setAttribute("data-parent", "#accordionExample");

                        var card_body = document.createElement("div");
                        card_body.className = "card-body";

                        var bang = document.createElement("div");
                        bang.className = "bang";
                        bang.innerHTML = `<small id="emailHelp" class="form-text text-muted">Date: <u>${data["messages"]["date"]} UTC</u></small>&nbsp;<br>`;

                        var payload_div = document.createElement("div");
                        payload_div.innerHTML = `${data["messages"]["payload"]}`;

                        newMessageElement_H5.append(newMessageElement_INPUT);
                        card.append(newMessageElement_H5);
                        card.append(newMsgElement_1);
                        newMsgElement_1.append(card_body);
                        card_body.append(bang);
                        card_body.append(payload_div);
                        accordion.prepend(card);

                        var messages_count_number = document.getElementById("messages-count");
                        messages_count_number.innerText = `📤Messages - ${ parseInt(messages_count_number.innerText.split("-")[1]) + 1 }`;
                    }
                }
            );
        });
    }
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