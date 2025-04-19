
const token = "7556108523:AAHEtYdygrQUlWS1Ll_eC-Vo6qx7XIXgdsE";
const chatId = "6852222545";

document.getElementById("productForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const title = document.getElementById("title").value;
  const category = document.getElementById("category").value;
  const prices = document.getElementById("prices").value;
  const description = document.getElementById("description").value;
  const imageFile = document.getElementById("imageInput").files[0];

  const caption = `**${category}**\n\n*${title}*\n\n${prices}\n\n${description}`;

  const formData = new FormData();
  formData.append("chat_id", chatId);
  formData.append("caption", caption);
  formData.append("parse_mode", "Markdown");

  if (imageFile) {
    formData.append("photo", imageFile);
    await fetch(`https://api.telegram.org/bot${token}/sendPhoto`, {
      method: "POST",
      body: formData
    });
  } else {
    formData.append("text", caption);
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: "POST",
      body: formData
    });
  }

  alert("Produit ajouté et envoyé sur Telegram !");
});
