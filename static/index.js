let mode = "login";

// ---------------- LOGIN / REGISTER ----------------

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

  form.reset();
}

window.addEventListener("click", function (e) {
  const modal = document.getElementById("loginModal");
  if (e.target === modal) {
    modal.style.display = "none";
  }
});

// ---------------- POST POPUP ----------------

let currentPostId = null;
let replyToCommentId = null;

function openPost(title, content, author, date, post_id) {
  currentPostId = post_id;

  document.getElementById("postTitle").innerText = title;
  document.getElementById("postContent").innerText = content;
  document.getElementById("postAuthor").innerText = author;
  document.getElementById("postDate").innerText = date;

  const form = document.getElementById("commentForm");
  if (form) {
    form.action = `/comment/${post_id}`;
  }

  document.getElementById("postModal").style.display = "flex";
}

function closePost() {
  document.getElementById("postModal").style.display = "none";
}

// ---------------- LIKE ----------------

function likePost(postId) {
  fetch(`/like/${postId}`)
    .then(res => res.json())
    .then(data => {
      const el = document.getElementById(`likes-${postId}`);
      el.innerText = data.count;

      const btn = el.closest(".like-btn");

      if (data.liked) {
        btn.classList.add("liked");
      } else {
        btn.classList.remove("liked");
      }
    });
}

// ---------------- REPLY ----------------

function replyTo(commentId) {
  replyToCommentId = commentId;

  const input = document.querySelector("#commentForm input");
  input.placeholder = "Replying...";
  input.focus();
}

// ---------------- COMMENT SUBMIT (ОДИН!!!) ----------------

document.addEventListener("submit", function (e) {

  if (e.target.id !== "commentForm") return;

  e.preventDefault();

  const form = e.target;
  const input = form.querySelector("input");
  const text = input.value.trim();

  if (!text) return;

  const formData = new FormData(form);

  if (replyToCommentId) {
    formData.append("parent_id", replyToCommentId);
  }

  fetch(form.action, {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {

    if (data.error) {
      openLogin();
      return;
    }

    const container = document.getElementById("commentsContainer");

    const commentDiv = document.createElement("div");
    commentDiv.classList.add("comment");
    commentDiv.id = "comment-" + data.id;

    const p = document.createElement("p");

    const strong = document.createElement("b");
    strong.innerText = data.username;

    const textNode = document.createTextNode(": " + data.content);

    p.appendChild(strong);
    p.appendChild(textNode);

    const replyBtn = document.createElement("button");
    replyBtn.innerText = "Reply";
    replyBtn.classList.add("reply-btn");
    replyBtn.onclick = () => replyTo(data.id);

    const repliesDiv = document.createElement("div");
    repliesDiv.classList.add("replies");

    commentDiv.appendChild(p);
    commentDiv.appendChild(replyBtn);
    commentDiv.appendChild(repliesDiv);

    if (data.parent_id) {
      const parent = document.getElementById("comment-" + data.parent_id);

      if (parent) {
        const replies = parent.querySelector(".replies");
        replies.appendChild(commentDiv);
      } else {
        container.appendChild(commentDiv);
      }
    } else {
      container.appendChild(commentDiv);
    }

    input.value = "";
    input.placeholder = "Write a comment...";
    replyToCommentId = null;
  });

});