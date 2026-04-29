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
  const link = document.getElementById("modalSwitchLink");

  if (mode === "login") {
    title.innerText = "Logg inn";
    button.innerText = "Logg inn";
    form.action = "/login";

    // ❌ без username
    username.classList.add("hidden");
    username.removeAttribute("required");

    // ✔ текст
    text.innerText = "Har du ikke konto?";
    link.innerText = "Registrer";

  } else {
    title.innerText = "Registrer";
    button.innerText = "Registrer";
    form.action = "/register";

    // ✔ з username
    username.classList.remove("hidden");
    username.setAttribute("required", true);

    // ✔ текст
    text.innerText = "Har du allerede konto?";
    link.innerText = "Logg inn";
  }

  form.reset();
}
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

  const container = document.getElementById("commentsContainer");
  container.innerHTML = "";

  fetch(`/comments/${post_id}`)
    .then(res => res.json())
    .then(comments => {
      comments.forEach(renderComment);
    });

  document.getElementById("postModal").style.display = "flex";
}

function closePost() {
  document.getElementById("postModal").style.display = "none";
}

// ---------------- LIKE POST ----------------
function likePost(postId) {
  fetch(`/like/${postId}`)
    .then(res => res.json())
    .then(data => {
      const el = document.getElementById(`likes-${postId}`);
      el.innerText = data.count;

      const btn = el.closest(".like-btn");

      btn.classList.toggle("liked", data.liked);
    });
}


// ---------------- LIKE COMMENT ----------------

function likeComment(commentId) {
  fetch(`/like_comment/${commentId}`)
    .then(res => res.json())
    .then(data => {

      if (data.error) {
        openLogin();
        return;
      }

      const el = document.getElementById(`comment-likes-${commentId}`);
      el.innerText = data.count;

      const btn = el.previousSibling;

      btn.classList.toggle("liked", data.liked);
    });
}

// ---------------- REPLY ----------------

function replyTo(commentId) {
  replyToCommentId = commentId;

  const input = document.querySelector("#commentForm input");
  input.placeholder = "Replying...";
  input.focus();
}


// ---------------- RENDER COMMENT ----------------

function renderComment(data) {
  const container = document.getElementById("commentsContainer");

  // root
  const commentDiv = document.createElement("div");
  commentDiv.classList.add("comment");
  commentDiv.id = "comment-" + data.id;

  // text
  const p = document.createElement("p");
  const strong = document.createElement("b");
  strong.innerText = data.username;
  p.appendChild(strong);
  p.appendChild(document.createTextNode(": " + data.content));

  // actions row
  const actions = document.createElement("div");
  actions.classList.add("comment-actions");

  // reply
  const replyBtn = document.createElement("button");
  replyBtn.innerText = "Reply";
  replyBtn.classList.add("reply-btn");
  replyBtn.onclick = () => replyTo(data.id);

  // like
  const likeBtn = document.createElement("button");
  likeBtn.innerText = "Like";
  likeBtn.classList.add("like-btn");
  likeBtn.onclick = () => likeComment(data.id);

  // count
  const likeCount = document.createElement("span");
  likeCount.id = `comment-likes-${data.id}`;
  likeCount.classList.add("like-count");
  likeCount.innerText = data.likes_count ?? 0; // якщо з бекенду не приходить — буде 0

  // зібрати actions
  actions.appendChild(replyBtn);
  actions.appendChild(likeBtn);
  actions.appendChild(likeCount);

  // replies container
  const repliesDiv = document.createElement("div");
  repliesDiv.classList.add("replies");

  // зібрати comment
  commentDiv.appendChild(p);
  commentDiv.appendChild(actions);
  commentDiv.appendChild(repliesDiv);

  // вкладення (reply)
  if (data.parent_id) {
    const parent = document.getElementById("comment-" + data.parent_id);
    if (parent) {
      parent.querySelector(".replies").appendChild(commentDiv);
      return;
    }
  }

  // інакше — в корінь
  container.appendChild(commentDiv);
}

// ---------------- COMMENT SUBMIT ----------------

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

      renderComment(data); // 🔥 замість дублювання

      input.value = "";
      input.placeholder = "Write a comment...";
      replyToCommentId = null;
    });
});

