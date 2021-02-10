function load_sent_messages(EBCheck, location) {
    fetch('/sent-messages/' + Date.now())
        .then(function(response) {
            return response.json()
        })
        .then(function(myJson) {
            console.log("the data is: " + myJson);
            var ul = document.getElementById(location);
            myJson.sort(function(a, b) {
                return b['timestamp'] - a['timestamp'];
            });
            myJson.forEach((message) => {
                if (message['to-eb'] === EBCheck) {
                    return;
                }
                // console.log(message)
                // message = JSON.parse(message);
                // console.log("Message is" + message);
                var li = document.createElement("li");
                var message_header = document.createElement("div");
                message_header.className = "collapsible-header"
                if (message['recv-del-id'].slice(2) == 'EB') {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "To: EB" + '<span class="new badge red" data-badge-caption="">EB</span>';
                } else {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "To: " + message['recv-del-country'];
                }
                li.appendChild(message_header);
                var message_content = document.createElement("div");
                message_content.className = "collapsible-body"
                message_content.textContent = message['message']
                li.appendChild(message_content);
                ul.appendChild(li);
            });
        });
}


function load_recv_messages(EBCheck, location) {
    fetch('/recv-messages/' + Date.now())
        .then(function(response) {
            return response.json()
        })
        .then(function(myJson) {
            // console.log("the data is: " + myJson);
            var ul = document.getElementById(location);
            myJson.sort(function(a, b) {
                return b['timestamp'] - a['timestamp'];
            });
            myJson.forEach((message) => {
                if (message['to-eb'] === EBCheck) {
                    return;
                }
                // console.log(message)
                // message = JSON.parse(message);
                // console.log("Message is" + message);
                var li = document.createElement("li");
                var message_header = document.createElement("div");
                message_header.className = "collapsible-header"

                if (message['send-del-id'].slice(2) == 'EB') {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "From: EB" + '<span class="new badge red" data-badge-caption="">EB</span>';
                } else {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "From: " + message['send-del-country'];
                }
                li.appendChild(message_header);
                var message_content = document.createElement("div");
                message_content.className = "collapsible-body"
                message_content.textContent = message['message']
                li.appendChild(message_content);
                ul.appendChild(li);
            });
        });
}

function load_eb_messages() {
    // fetch('/eb-messages')
    //     .then(function(response) {
    //         return response.json()
    //     })
    //     .then(function(myJson) {
    //         // console.log("the data is: " + myJson);
    //         var ul = document.getElementById("sent-messages-collapsible");
    //         myJson.forEach((message) => {
    //             // console.log(message)
    //             // message = JSON.parse(message);
    //             console.log("Message is" + message);
    //             var li = document.createElement("li");
    //             var message_header = document.createElement("div");
    //             message_header.className = "collapsible-header"
    //             message_header.innerHTML = '<i class="material-icons" >label_important</i>' + "From: " + message['send-del-country'];
    //             li.appendChild(message_header);
    //             var message_content = document.createElement("div");
    //             message_content.className = "collapsible-body"
    //             message_content.textContent = message['message']
    //             li.appendChild(message_content);
    //             ul.appendChild(li);
    //         });
    //     });
    load_recv_messages(false, "eb-messages-collapsible");
    load_sent_messages(false, "eb-messages-collapsible");
}


window.onload = function() {
    console.log("Function fired");
    load_sent_messages(true, "sent-messages-collapsible");
    load_recv_messages(true, "received-messages-collapsible");
    load_eb_messages();
    //dom not only ready, but everything is loaded
};