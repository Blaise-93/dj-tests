
  var wss_protocol = window.location.protocol == "https:" ? "wss://" : "ws://";
  var chatSocket = new WebSocket(
    wss_protocol + window.location.host + "/ws/chat/"
  );
  var messages = [];

  chatSocket.onopen = function (e) {
    document.querySelector("#chat-header").innerHTML =
      "Welcome to Django Chatbot";
  };

  chatSocket.onmessage = function (e) {
    var data = JSON.parse(e.data);
    var message = data["text"];
    messages.push(message);

    var str = '<ul class="space-y-2">';
    messages.forEach(function (msg) {
      str += `<li class="flex ${
        msg.source == "bot" ? "justify-start" : "justify-end"
      }">
      <div class="relative max-w-xl px-4 py-2 rounded-lg shadow-md
        ${
          msg.source == "bot"
            ? "text-gray-700 bg-white border border-gray-200"
            : "bg-blue-600 text-white"
        }">
        <span className="block font-normal">${msg.msg}</span></div></li>`;
    });
    str += "</ul>";
    document.querySelector("#chat-log").innerHTML = str;
  };

  chatSocket.onclose = function (e) {
    alert("Socket closed unexpectedly, please reload the page.");
  };

  document.querySelector("#chat-message-input").focus();
  document.querySelector("#chat-message-input").onkeyup = function (e) {
    if (e.keyCode === 13) {
      // enter, return
      document.querySelector("#chat-message-submit").click();
    }
  };

  document.querySelector("#chat-message-submit").onclick = function (e) {
    var messageInputDom = document.querySelector("#chat-message-input");
    var message = messageInputDom.value;
    chatSocket.send(
      JSON.stringify({
        text: message,
      })
    );

    messageInputDom.value = "";
  };
