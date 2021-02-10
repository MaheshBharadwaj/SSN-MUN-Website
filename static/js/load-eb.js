function load_sent_messages(location) {
    fetch('/sent-messages/' + Date.now())
        .then(function(response) {
            return response.json()
        })
        .then(function(myJson) {
            var ul = document.getElementById(location);
            myJson.sort(function(a, b) {
                return b['timestamp'] - a['timestamp'];
            });
            myJson.forEach((message) => {
                if (message['send-del-id'].slice(2) !== 'EB') {
                    return;
                }
                // message = JSON.parse(message);
                // console.log("Message is" + message);
                var li = document.createElement("li");
                var message_header = document.createElement("div");
                message_header.className = "collapsible-header"
                var d = new Date(message['timestamp'] * 1000);
                dateString = d.getHours() + ":" + d.getMinutes();
                message_header.innerHTML = '<i class="material-icons" >sent</i>' + "To: " 
                    + message['recv-del-country']
                    + '<span class="badge" data-badge-caption="">' + dateString + '</span>';
                li.appendChild(message_header);
                var message_content = document.createElement("div");
                message_content.className = "collapsible-body"
                message_content.textContent = message['message']
                li.appendChild(message_content);
                ul.appendChild(li);
            });
        });
}


function load_recv_messages(location) {
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
                if (message['recv-del-id'].slice(2) !== 'EB') {
                    return;
                }
                // console.log(message)
                // message = JSON.parse(message);
                // console.log("Message is" + message);
                var li = document.createElement("li");
                var message_header = document.createElement("div");
                message_header.className = "collapsible-header"
                var d = new Date(message['timestamp'] * 1000);
                dateString = d.getHours() + ":" + d.getMinutes();
                message_header.innerHTML = '<i class="material-icons" >mail</i>' + "From: " 
                    + message['send-del-country']
                    + '<span class="badge" data-badge-caption="">' + dateString + '</span>';
                li.appendChild(message_header);
                var message_content = document.createElement("div");
                message_content.className = "collapsible-body"
                message_content.textContent = message['message']
                li.appendChild(message_content);
                ul.appendChild(li);
            });
        });
}

function load_eb_messages(location) {
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
                if (!message['to-eb']) {
                    return;
                }
                // console.log(message)
                // message = JSON.parse(message);
                console.log("Message is" + message);
                var li = document.createElement("li");
                var message_header = document.createElement("div");
                message_header.className = "collapsible-header"
                message_header.innerHTML = '<i class="material-icons" >label_important</i>' +
                    "From: " + message['send-del-country'] + "\nTo: " + message['recv-del-country'];
                li.appendChild(message_header);
                var message_content = document.createElement("div");
                message_content.className = "collapsible-body"
                message_content.textContent = message['message']
                li.appendChild(message_content);
                ul.appendChild(li);
            });
        });
    // load_recv_messages(false, "eb-messages-collapsible");
    // load_sent_messages(false, "eb-messages-collapsible");
}


window.onload = function() {
    console.log("Function fired");
    load_sent_messages("sent-messages-collapsible");
    load_recv_messages("received-messages-collapsible");
    load_eb_messages("thru-messages-collapsible");
    //dom not only ready, but everything is loaded
};