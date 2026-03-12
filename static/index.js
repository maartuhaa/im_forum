function openAuth() {

    document.getElementById("authPopup").style.display = "flex";

    showLogin();
}

function showLogin() {

    document.getElementById("loginForm").classList.remove("hidden");
    document.getElementById("registerForm").classList.add("hidden");

    document.getElementById("authTitle").innerText = "Logg inn";
}

function showRegister() {

    document.getElementById("loginForm").classList.add("hidden");
    document.getElementById("registerForm").classList.remove("hidden");

    document.getElementById("authTitle").innerText = "Registrer";
}

function closeAuth() {

    document.getElementById("authPopup").style.display = "none";
}