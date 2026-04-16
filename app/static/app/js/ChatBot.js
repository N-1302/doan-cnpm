document.addEventListener("DOMContentLoaded", function () {
  const chatbotToggle = document.getElementById("chatbot-toggle");
  const chatbotBox = document.getElementById("chatbot-box");
  const chatbotClose = document.getElementById("chatbot-close");
  const chatbotSend = document.getElementById("chatbot-send");
  const chatbotText = document.getElementById("chatbot-text");
  const chatbotMessages = document.getElementById("chatbot-messages");

  if (!chatbotToggle || !chatbotBox || !chatbotClose || !chatbotSend || !chatbotText || !chatbotMessages) {
    return;
  }

  function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = type === "user" ? "user-msg" : "bot-msg";

    const span = document.createElement("span");
    span.textContent = text;

    div.appendChild(span);
    chatbotMessages.appendChild(div);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  function getBotReply(message) {
    const msg = message.toLowerCase();

    if (msg.includes("xin chào") || msg.includes("chào") || msg.includes("hello") || msg.includes("hi")) {
      return "Xin chào bạn 🍰 SprintTeam rất vui được hỗ trợ bạn.";
    }

    if (msg.includes("ship") || msg.includes("giao hàng") || msg.includes("phí vận chuyển")) {
      return "Phí vận chuyển hiện tại từ 15.000đ đến 30.000đ tùy giá trị đơn hàng nhé.";
    }

    if (msg.includes("khuyến mãi") || msg.includes("mã giảm giá") || msg.includes("sale")) {
      return "Bạn có thể chọn mã giảm giá ngay ở trang thanh toán để được giảm giá đơn hàng.";
    }

    if (msg.includes("momo")) {
      return "Shop có hỗ trợ thanh toán bằng ví MoMo nhé.";
    }

    if (msg.includes("zalopay")) {
      return "Shop có hỗ trợ thanh toán bằng ví ZaloPay nhé.";
    }

    if (msg.includes("thanh toán")) {
      return "Bạn có thể thanh toán bằng COD, chuyển khoản, MoMo hoặc ZaloPay.";
    }

    if (msg.includes("đặt hàng") || msg.includes("mua hàng")) {
      return "Bạn chọn bánh, thêm vào giỏ hàng rồi vào thanh toán để đặt đơn nhé.";
    }

    if (msg.includes("địa chỉ") || msg.includes("cửa hàng ở đâu")) {
      return "Cửa hàng ở 280 An Dương Vương, Phường Chợ Quán, TP.Hồ Chí Minh.";
    }

    if (msg.includes("giờ mở cửa") || msg.includes("mấy giờ")) {
      return "Shop mở cửa từ 8:00 đến 22:00 hằng ngày nhé.";
    }

    if (msg.includes("liên hệ") || msg.includes("hotline")) {
      return "Bạn có thể liên hệ hotline 0944 630 055 để được hỗ trợ nhanh nhất.";
    }

    if (msg.includes("cảm ơn")) {
      return "SprintTeam cảm ơn bạn rất nhiều 💖";
    }

    return "Mình chưa hiểu rõ câu hỏi lắm 😅 Bạn thử hỏi về giao hàng, thanh toán, khuyến mãi hoặc đặt bánh nhé.";
  }

  function sendMessage() {
    const message = chatbotText.value.trim();
    if (!message) return;

    addMessage(message, "user");
    chatbotText.value = "";

    setTimeout(function () {
      addMessage(getBotReply(message), "bot");
    }, 400);
  }

  chatbotToggle.addEventListener("click", function () {
    chatbotBox.style.display = "flex";

    if (chatbotMessages.children.length === 0) {
      addMessage("Xin chào bạn 🍰 Mình là chatbot hỗ trợ của SprintTeam. Bạn cần mình giúp gì nào?", "bot");
    }
  });

  chatbotClose.addEventListener("click", function () {
  chatbotBox.style.display = "none";
  chatbotMessages.innerHTML = "";
  });

  chatbotSend.addEventListener("click", sendMessage);

  chatbotText.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });
});