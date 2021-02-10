function load_sent_messages(EBCheck, location, chitCount = 0) {
    var i = chitCount;
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
                i += 1;
                // console.log(message)
                // message = JSON.parse(message);
                // console.log("Message is" + message);
                var li = document.createElement("li");
                var message_header = document.createElement("div");
                message_header.className = "collapsible-header";
                var d = new Date(message['timestamp'] * 1000);
                dateString = d.getHours() + ":" + d.getMinutes();
                if (message['recv-del-id'].slice(2) == 'EB') {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "To: EB" 
                        + '<span class="new badge red" data-badge-caption="">' + dateString + '</span>';
                } else {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "To: " 
                    + message['recv-del-country']
                    + '<span class="badge" data-badge-caption="">' + dateString + '</span>';
                }
                li.appendChild(message_header);
                var message_content = document.createElement("div");
                message_content.className = "collapsible-body"
                message_content.textContent = message['message']
                li.appendChild(message_content);
                ul.appendChild(li);
            });
            // console.log(i);
            if (EBCheck !== false) {
                document.getElementById('sent_length').innerHTML = i;
            }             
        });
    return(i);
}


function load_recv_messages(EBCheck, location) {
    fetch('/recv-messages/' + Date.now())
        .then(function(response) {
            return response.json()
        })
        .then(function(myJson) {
            // console.log("the data is: " + myJson);
            var ul = document.getElementById(location);
            var i = 0;
            myJson.sort(function(a, b) {
                return b['timestamp'] - a['timestamp'];
            });
            myJson.forEach((message) => {
                if (message['to-eb'] === EBCheck) {
                    return;
                }
                i += 1;
                // console.log(message)
                // message = JSON.parse(message);
                // console.log("Message is" + message);
                var li = document.createElement("li");
                var message_header = document.createElement("div");
                message_header.className = "collapsible-header"
                var d = new Date(message['timestamp'] * 1000);
                dateString = d.getHours() + ":" + d.getMinutes();
                if (message['send-del-id'].slice(2) == 'EB') {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "From: EB" 
                        + '<span class="new badge red" data-badge-caption="">' + dateString + '</span>';
                } else {
                    message_header.innerHTML = '<i class="material-icons" >mail</i>' + "From: " 
                    + message['send-del-country']
                    + '<span class="badge" data-badge-caption="">' + dateString + '</span>';
                }
                li.appendChild(message_header);
                var message_content = document.createElement("div");
                message_content.className = "collapsible-body"
                message_content.textContent = message['message']
                li.appendChild(message_content);
                ul.appendChild(li);
            });
            if (EBCheck !== false) {
                document.getElementById('recv_length').innerHTML = i;
            } else {
                document.getElementById('thru_length').innerHTML = i;
            }
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
    let x = load_sent_messages(false, "eb-messages-collapsible");
    console.log("hello" + x);
    load_recv_messages(false, "eb-messages-collapsible", x);
}


window.onload = function() {
    console.log("Function fired");
    load_sent_messages(true, "sent-messages-collapsible");
    load_recv_messages(true, "received-messages-collapsible");
    load_eb_messages();
    //dom not only ready, but everything is loaded
};