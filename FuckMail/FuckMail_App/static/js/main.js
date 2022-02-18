//setInterval(getNewMessages, 5000);

$('#basic-addon1').keypress(function (event) {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if (keycode == '13') { }
});

$(document).on("contextmenu", ".list-group-item", function(e){
    var mails_count = document.getElementById("title-mails-count"); // Get mails count from title-mails-count element.
    var title_mail_address = document.getElementById("mail_address");
    if (title_mail_address != null){
        title_mail_address.remove();
    }
    mails_count.innerText = `📨Mails - ${ mails_count.innerText.split("-")[1] - 1 }`; // Change mails count.
    var x = event.clientX, y = event.clientY,
    mail_address = document.elementFromPoint(x, y);
    mail_address.remove();
    var data = new FormData(); // Init new FormData object.
    data.append("mail_address", mail_address.value); // Add mail address in the FormData object.
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

/**
 * This is function redirect on main page (profile).
 */
function redirect_to_main_page() {
    window.location.replace("profile");
};

// All modals

/**
 * This is show modal window for add account.
 * User just may to add one mail account.
 */
function add_account_modal(){
    $("#addAccount").modal("show");
}

/**
 * This is show modal window for add few accounts.
 * User just may to add few accounts.
 */
function add_few_accounts_modal(){
    $("#addFewAccounts").modal("show");
}

/**
 * This is show modal window for delete all accounts.
 * User just may delete all accounts.
 */
function deleteAllAccounts_modal(){
    $("#deleteAllAccounts").modal("show")
}

/**
 * This is read message:
 *  1) Change color if message is not read but user on click.
 *  2) Send request in the views.
 * @param {string} message_id
 */
function read_message(message_id) {
    var elem = document.getElementById(message_id);
    elem.style.color = "#686868";

    var data = new FormData(); // Init new FormData object.
    data.append("message_id", message_id); // Add message id in the FormData object.
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

/**
 * This is function delete mail address:
 *  1) Send request in the views.
 * @param {string} mail_address 
 */
function del_mail(mail_address) {
    $('#delMail').modal('hide');
    document.getElementById("accordionExample").remove();
    document.getElementById("mail-" + mail_address).remove();
    var data = new FormData(); // Init new FormData object.
    data.append("mail_address", mail_address); // Add mail address in the FormData object.
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
                if (data==true){
                    redirect_to_main_page(); // Redirect on the main page.
                }
            }
        );
    });
}

/**
 * This function delete is not found mail address:
 *  1) Send request in views.
 * @param {string} mail_address 
 */
function del_is_not_found_mail(mail_address) {
    $('#delMail').modal('hide');
    var data = new FormData(); // Init new FormData object.
    data.append("mail_address", mail_address); // Add mail address in the FormData object.
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
                    redirect_to_main_page(); // Redirect on the main page.
                }
            }
        );
    });
}

function get_file() {
    var file = document.getElementById("file").files[0];
    console.log(file);
    if (file) {
        var fileNameArray = file.name.split("."); // File name separation for name and extension.
        if (fileNameArray[fileNameArray.length - 1] != "txt") {
            return alert("Формат файла является неправильным!"); // Output message for invalid file extension.
        }
        var fileSize = file.size / 1024 / 1024; // File Size.
        if (fileSize > 50) {
            return alert("Файл превышает размер!"); // The size of file exceeds file quota limit.
        } else {
            $('#addFewAccounts').modal('hide');
            var reader = new FileReader(); // Init new FileReader object.
            reader.readAsText(file, "UTF-8");
            reader.onload = function(e) {
                var data = new FormData(); // Init new FormData object.
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
                                redirect_to_main_page(); // Redirect on the main page.
                            }
                        }
                    );
                });
            }
        }
    }
    else {
        return alert("Файл отсутствует!"); // File is not exists.
    }
}

/**
 * This is function delete all mail addresses from user account.
 */
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
                    redirect_to_main_page(); // Redirect on the main page.
                }
            }
        )
    });
}

/**
 * This is function redirect on help page.
 */
function help_addFileFormat(){
    window.location.href = "help/add_file_format.html";
}

function getNewMessages(){
    var mail_address = document.getElementById("mail_address");
    if (mail_address != null){
        var data = new FormData(); // Init new FormData object.
        data.append("mail_address", mail_address.textContent); // Add mail address in the FormData object.
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
                        // Select accordion element.
                        var ACCORDION = document.querySelector("#accordionExample");

                        // Create elements.
                        var CARD = document.createElement('div');
                        var Element_H5 = document.createElement('h5');
                        var Element_INPUT = document.createElement('input');
                        var Element_DIV = document.createElement("div");
                        var CARD_BODY = document.createElement("div");
                        var BANG = document.createElement("div");
                        var PAYLOAD_DIV = document.createElement("div");

                        // Set values for all new elements.
                        CARD.className = "card";

                        Element_INPUT.id = data["messages"]["message_id"];
                        Element_INPUT.type = "submit";
                        Element_INPUT.className = "list-group-item list-group-item-action shadow p-3 mb-2 bg-white rounded font-weight-bold";
                        Element_INPUT.value = `${data["messages"]["from_user"]} - ${data["messages"]["subject"]}`;
                        Element_INPUT.title = data["messages"]["subject"];
                        Element_INPUT.style = "color: #000000;";
                        Element_INPUT.innerHTML = "This is message";
                        Element_INPUT.setAttribute("data-target", `#collapse${data["messages"]["message_id"]}`);
                        Element_INPUT.setAttribute("data-toggle", "collapse");
                        Element_INPUT.setAttribute("onclick", "read_message(this.id);");
                        Element_INPUT.setAttribute("aria-expanded", "true");
                        Element_INPUT.setAttribute("data-placement", "right");
                        Element_INPUT.setAttribute("aria-controls", `collapse${data["messages"]["message_id"]}`);

                        Element_DIV.id = `collapse${data["messages"]["message_id"]}`
                        Element_DIV.className = "collapse";
                        Element_DIV.setAttribute("aria-labelledby", `heading${data["messages"]["message_id"]}`);
                        Element_DIV.setAttribute("data-parent", "#accordionExample");

                        CARD_BODY.className = "card-body";

                        BANG.className = "bang";
                        BANG.innerHTML = `<small id="emailHelp" class="form-text text-muted">Date: <u>${data["messages"]["date"]} UTC</u></small>&nbsp;<br>`;

                        PAYLOAD_DIV.innerHTML = `${data["messages"]["payload"]}`;

                        // Append elements.
                        Element_H5.append(Element_INPUT);
                        CARD.append(Element_H5);
                        CARD.append(Element_DIV);
                        Element_DIV.append(CARD_BODY);
                        CARD_BODY.append(BANG);
                        CARD_BODY.append(PAYLOAD_DIV);
                        ACCORDION.prepend(CARD);

                        // Set new count messages.
                        var messages_count_number = document.getElementById("messages-count");
                        messages_count_number.innerText = `<i class="bi bi-envelope"></i> Messages - ${ parseInt(messages_count_number.innerText.split("-")[1]) + 1 }`;
                    }
                }
            );
        });
    }
}

function cache_messages_checkbox(){
    fetch("change_checkbox_value/", {
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
                    //redirect_to_main_page(); // Redirect on the main page.
                }
            }
        )
    });
}

/**
 * This is function take cookie from browser.
 * @param {*} name 
 * @returns cookieValue
 */
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