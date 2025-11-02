document.addEventListener("DOMContentLoaded", function () {
  const chatRoom = document.querySelector(".chat-room");
  const inputText = document.getElementById("inputText");
  const sendButton = document.querySelector(".button-send");

  
  chatRoom.style.overflowY = "auto";
  chatRoom.style.scrollBehavior = "smooth";

  
  function addMessage(text, side) {
    const messageWrapper = document.createElement("div");
    messageWrapper.classList.add("message", side === "right" ? "message-right" : "message-left");

   
    const avatarWrapper = document.createElement("div");
    avatarWrapper.classList.add("avatar-wrapper", "avatar-small");
    const avatarImg = document.createElement("img");
    avatarImg.src =
      side === "right"
        ? "/static/medical/user.jpeg"
        : "/static/medical/doctor.jpeg";
    avatarWrapper.appendChild(avatarImg);

    
    const bubbleDiv = document.createElement("div");
    bubbleDiv.classList.add("bubble");
    bubbleDiv.textContent = text;

    
    if (side === "right") {
      messageWrapper.appendChild(bubbleDiv);
      messageWrapper.appendChild(avatarWrapper);
    } else {
      messageWrapper.appendChild(avatarWrapper);
      messageWrapper.appendChild(bubbleDiv);
    }

    chatRoom.appendChild(messageWrapper);
    chatRoom.scrollTop = chatRoom.scrollHeight;
  }

  function sendMessage() {
    const message = inputText.value.trim();
    if (!message) return;

    addMessage(message, "right");
    inputText.value = "";

    
    const typingDiv = document.createElement("div");
    typingDiv.classList.add("message", "message-left");
    typingDiv.innerHTML = `
      <div class="avatar-wrapper avatar-small">
        <img src="/static/medical/doctor.jpeg" alt="Bot Avatar" />
      </div>
      <div class="bubble">Typing...</div>
    `;
    chatRoom.appendChild(typingDiv);
    chatRoom.scrollTop = chatRoom.scrollHeight;

    fetch("/get", {
      method: "POST",
      body: new URLSearchParams({ msg: message }),
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    })
      .then((res) => res.text())
      .then((data) => {
        typingDiv.remove();
        addMessage(data, "left");
      })
      .catch((err) => {
        typingDiv.remove();
        addMessage("⚠️ Sorry, I couldn't process your request.", "left");
        console.error(err);
      });
  }

  sendButton.addEventListener("click", sendMessage);
  inputText.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });
});
