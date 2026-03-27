let mode = "login";

function openLogin() {
  mode = "login";
  updateModal();
  document.getElementById("loginModal").style.display = "flex";
}

function openRegister() {
  mode = "register";
  updateModal();
  document.getElementById("loginModal").style.display = "flex";
}

function closeLogin() {
  document.getElementById("loginModal").style.display = "none";
}

function switchMode(e) {
  e.preventDefault();
  mode = mode === "login" ? "register" : "login";
  updateModal();
}

function updateModal() {
  const title = document.getElementById("modalTitle");
  const form = document.getElementById("modalForm");
  const button = document.getElementById("modalButton");
  const username = document.getElementById("usernameField");
  const text = document.getElementById("modalSwitchText");

  if (mode === "login") {
    title.innerText = "Logg inn";
    button.innerText = "Logg inn";
    form.action = "/login";

    username.classList.add("hidden");
    username.removeAttribute("required");

    text.innerText = "Har du ikke konto?";
  } else {
    title.innerText = "Registrer";
    button.innerText = "Registrer";
    form.action = "/register";

    username.classList.remove("hidden");
    username.setAttribute("required", true);

    text.innerText = "Har du allerede konto?";
  }

  // 🔥 очищає всі поля (фікс бага)
  form.reset();
}

window.addEventListener("click", function (e) {
  const modal = document.getElementById("loginModal");
  if (e.target === modal) {
    modal.style.display = "none";
  }
});


function openPost(title, content, author, date) {

  document.getElementById("postTitle").innerText = title;
  document.getElementById("postContent").innerText = content;
  document.getElementById("postAuthor").innerText = author;
  document.getElementById("postDate").innerText = date;

  document.getElementById("postModal").style.display = "flex";
}

function closePost() {
  document.getElementById("postModal").style.display = "none";
}