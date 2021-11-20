var sentPromise = fetch('/sent-messages/' + Date.now());
var recvPromise = fetch('/recv-messages/' + Date.now());


Promise.all([sentPromise, recvPromise]).then((values) => {
    sentResp = values[0];
    recvResp = values[1];

    var sentJsonPromise = sentResp.json();
    var recvJsonPromise = recvResp.json();


    Promise.all([sentJsonPromise, recvJsonPromise]).then((jsonValues) => {
        sentJson = jsonValues[0];
        recvJson = jsonValues[1];
        var throughCount = 0;
        var throughUl = document.getElementById("eb-messages-collapsible");
        throughUl.innerHTML = `<li>
                            <div class="collapsible-header "><i class="material-icons ">info</i>SSNMUN</div>
                            <div class="collapsible-body "><span>Messages sent to EB and from EB to you will be located here.</span>
                            </div>
                            </li>`;
        throughCount = sentMessagesHandler(sentJson, recvJson, throughUl, throughCount);
        throughCount = recvMessagesHandler(sentJson, recvJson, throughUl, throughCount);
        document.getElementById('thru_length').innerHTML = throughCount;

    });
});

function sentMessagesHandler(sentJson, recvJson, throughUl, throughCount) {
    var sentCount = 0;
    var recvMap = new Map();

    recvJson.forEach((message) => {
        recvMap.set(message["message-id"], message);
    });



    var sentUl = document.getElementById("sent-messages-collapsible");
    sentUl.innerHTML = `<li>
                            <div class="collapsible-header"><i class="material-icons">info</i>From SSNMUN</div>
                            <div class="collapsible-body"><span>Click on the compose button and choose delegate or eb to send a
                            message. Substantiative messages are <span style="color: #5aaaed; font-weight: 800;">highlighted
                            in this colour.</span></div>
                            </li>`;
    sentJson.sort(function (a, b) {
        return b['timestamp'] - a['timestamp'];
    });
    sentJson.forEach((message) => {
        if (message['to-eb'] === false) {
            sentCount += 1;

            var li = document.createElement("li");
            var message_header = document.createElement("div");
            message_header.className = "collapsible-header";
            var d = new Date(message['timestamp'] * 1000);
            dateString = ("00" + d.getHours()).slice(-2) + ":" + ("00" + d.getMinutes()).slice(-2);
            if (message['recv-del-id'].slice(2) == 'EB') {
                if (message['substantiative'] === true) {
                    message_header.classList.add("sub-highlight");
                }
                message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>To:&nbsp</b>EB" +
                    '<span class="new badge red" data-badge-caption="">' + dateString + '</span>';
            } else {
                message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>To:&nbsp</b>" +
                    message['recv-del-country'] +
                    '<span class="badge" data-badge-caption="">' + dateString + '</span>';
            }
            li.appendChild(message_header);
            var message_content = document.createElement("div");
            message_content.className = "collapsible-body"

            var prepend = "";
            if (message["parent"] != null) {
                console.log("Message has parent: " + message["parent"]);
                prepend += `<div style="opacity:0.7;">`;
                console.log("Message[Parent]: " + message["parent"]);
                parentMsg = recvMap.get(message["parent"]);
                console.log("Message Parent Obj: " + parentMsg);
                prepend += "Reply to message <b>From:&nbsp</b>" + parentMsg["send-del-country"] + "<br>";
                prepend += parentMsg["message"] + "<br><hr><br></div>";
            }

            message_content.innerHTML = prepend + message['message']
            li.appendChild(message_content);
            sentUl.appendChild(li);
            return;
        }
        throughCount += 1;
        var li = document.createElement("li");
        var message_header = document.createElement("div");
        message_header.className = "collapsible-header";
        var d = new Date(message['timestamp'] * 1000);
        dateString = ("00" + d.getHours()).slice(-2) + ":" + ("00" + d.getMinutes()).slice(-2);
        if (message['recv-del-id'].slice(2) == 'EB') {
            message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>To:&nbsp</b>EB" +
                '<span class="new badge red" data-badge-caption="">' + dateString + '</span>';
        } else {
            message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>To:&nbsp</b>" +
                message['recv-del-country'] +
                '<span class="badge" data-badge-caption="">' + dateString + '</span>';
        }
        li.appendChild(message_header);
        var message_content = document.createElement("div");
        message_content.className = "collapsible-body"
        var prepend = "";
        if (message["parent"] != null) {
            console.log("Message has parent: " + message["parent"]);
            prepend += `<div style="opacity:0.7;">`;
            console.log("Message[Parent]: " + message["parent"]);
            parentMsg = recvMap.get(message["parent"]);
            console.log("Message parent Obj: " + parentMsg);
            prepend += "Reply to message <b>From:&nbsp</b>" + parentMsg["send-del-country"] + "<br>";
            prepend += parentMsg["message"] + "<br><hr><br></div>";
        }

        message_content.innerHTML = prepend + message['message'];
        li.appendChild(message_content);
        throughUl.appendChild(li);
    });
    document.getElementById("sent_length").innerHTML = sentCount;
    return throughCount;
}


function recvMessagesHandler(sentJson, recvJson, throughUl, throughCount) {
    var recvCount = 0;
    var sentMap = new Map();
    recvJson.sort(function (a, b) {
        return b['timestamp'] - a['timestamp'];
    });
    sentJson.forEach((message) => {
        sentMap.set(message["message-id"], message);
    });

    var recvUl = document.getElementById("received-messages-collapsible");
    recvUl.innerHTML = `<li>
    <div class=" collapsible-header"><i class="material-icons ">info</i>SSNMUN</div>
    <div class="collapsible-body"><span>All the messages that you receive from other delegates will be
    located here</span></div>
    </li>`;
    recvJson.forEach((message) => {
        if (message['to-eb'] === false) {
            recvCount += 1;
            var li = document.createElement("li");
            var message_header = document.createElement("div");

            var reply_button = createReplyButton(message);


            message_header.className = "collapsible-header"
            var d = new Date(message['timestamp'] * 1000);
            dateString = ("00" + d.getHours()).slice(-2) + ":" + ("00" + d.getMinutes()).slice(-2);
            if (message['send-del-id'].slice(2) == 'EB') {
                message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>From:&nbsp</b>EB" +
                    '<span class="new badge red" data-badge-caption="">' + dateString + '</span>';
            } else {
                message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>From:&nbsp</b>" +
                    message['send-del-country'] +
                    '<span class="badge" data-badge-caption="">' + dateString + '</span>';
            }
            li.appendChild(message_header);
            var message_content = document.createElement("div");
            message_content.className = "collapsible-body";
            var prepend = "";
            if (message["parent"] != null) {
                console.log("Message has parent: " + message["parent"]);
                prepend += `<div style="opacity:0.7;">`;
                console.log("Message[Parent]: " + message["parent"]);
                parentMsg = sentMap.get(message["parent"]);
                console.log("Parent Message Obj: " + parentMsg);
                prepend += "Reply for message sent <b>To:&nbsp</b>" + parentMsg["recv-del-country"] + "<br>";
                prepend += parentMsg["message"] + "<br><hr><br></div>";
            }

            message_content.innerHTML = prepend + message['message'];
            var reply_br1 = document.createElement("br");
            var reply_br2 = document.createElement("br");

            message_content.appendChild(reply_br1);
            message_content.appendChild(reply_br2);
            message_content.appendChild(reply_button);
            li.appendChild(message_content);
            recvUl.appendChild(li);
            return;
        }
        throughCount += 1;


        var li = document.createElement("li");
        var message_header = document.createElement("div");
        message_header.className = "collapsible-header"
        var reply_button = createReplyButton(message);

        var d = new Date(message['timestamp'] * 1000);
        dateString = ("00" + d.getHours()).slice(-2) + ":" + ("00" + d.getMinutes()).slice(-2);
        if (message['send-del-id'].slice(2) == 'EB') {
            message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>From:&nbsp</b>EB" +
                '<span class="new badge red" data-badge-caption="">' + dateString + '</span>';
        } else {
            message_header.innerHTML = '<i class="material-icons" >mail</i>' + "<b>From:&nbsp</b>" +
                message['send-del-country'] +
                '<span class="badge" data-badge-caption="">' + dateString + '</span>';
        }
        li.appendChild(message_header);
        var message_content = document.createElement("div");
        message_content.className = "collapsible-body"
        var prepend = "";
        if (message["parent"] != null) {
            prepend += `<div style="opacity:0.7;">`;
            console.log("Message[Parent]: " + message["parent"]);
            parentMsg = sentMap.get(message["parent"]);
            prepend += "Reply for message sent <b>To:&nbsp</b>" + parentMsg["recv-del-country"] + "<br>";
            prepend += parentMsg["message"] + "<br><hr><br></div>";
        }

        message_content.innerHTML = prepend + message['message'];
        var reply_br1 = document.createElement("br");
        var reply_br2 = document.createElement("br");

        message_content.appendChild(reply_br1);
        message_content.appendChild(reply_br2);
        message_content.appendChild(reply_button);
        li.appendChild(message_content);
        throughUl.appendChild(li);
    });
    document.getElementById('recv_length').innerHTML = recvCount;
    return throughCount;
}

function createReplyButton(message) {
    var reply_button = document.createElement("button");
    reply_button.setAttribute("id", "reply-button");
    reply_button.message = message;
    reply_button.innerHTML = "Reply";
    reply_button.className += "btn waves-effect waves-light";

    var reply_icon = document.createElement("i");
    reply_icon.className += "material-icons right";
    reply_icon.innerHTML = "send";


    reply_button.appendChild(reply_icon);
    reply_button.addEventListener("click", replyMessage);
    return reply_button;
}


function replyMessage(event) {
    message = event.currentTarget.message;
       
    if (message["send-del-id"].slice(2) === "EB") {
        window.location.href = "/send-eb?parent_id=" + message["message-id"];
    }
    else {
        window.location.href = "/send-delegate?send_country=" +
            message["send-del-country"] + "&send_country_id=" +
            message["send-del-id"] + "&parent_id=" + message["message-id"] + "&to_eb=" + message["to-eb"];
    }
};