import { loadPage } from "./pageLoader.js";

function getSenderEmail() {
  const jwt = localStorage.getItem("jwt");
  const decoded = parseJWT(jwt, 1);
  return decoded.email;
}

function showToast(message, type) {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;

  // Alt çizgiyi ekleyin
  const underline = document.createElement("div");
  underline.className = "underline";
  toast.appendChild(underline);

  // Toast'u body'e ekle
  document.body.appendChild(toast);

  // Kısa bir gecikmeyle görünür hale getir
  setTimeout(() => {
    toast.classList.add("show");
  }, 100);

  // Alt çizgi animasyonu bittikten sonra toast'u gizle ve DOM'dan kaldır
  underline.addEventListener("animationend", () => {
    toast.style.animation = "fadeOut 0.5s ease-in-out forwards";
    toast.addEventListener("animationend", () => toast.remove());
  });
}

export function setupLoginForm() {
  const password = document.getElementById("forget-password");
  password.addEventListener("click", function (event) {
    event.preventDefault();
    loadPage("password");
  });

  const register = document.getElementById("register");
  register.addEventListener("click", function (event) {
    event.preventDefault();
    loadPage("register");
  });

  document
    .getElementById("loginForm")
    .addEventListener("submit", function (event) {
      event.preventDefault();

      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      fetch("https://10.11.4.10/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.token) {
            if (parseJWT(data.token).twofactoractive) {
              loadPage("2fa");
              const socket = new WebSocket(
                "wss://10.11.4.10/ws/status/userstatus/"
              );
              socket.onopen = () => {
                socket.send("0");
              };

              showToast("Two-factor authentication required.", "success");
            } else {
              loadPage("home");
              const socket = new WebSocket(
                "wss://10.11.4.10/ws/status/userstatus/"
              );
              socket.onopen = () => {
                socket.send("0");
              };

              localStorage.setItem("jwt", data.token);
              showToast("Login successful!", "success");
            }
          } else {
            console.error("JWT not found in response");
            showToast(
              "Login failed: Please check your email and password and try again.",
              "error"
            );
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          showToast("Login error. Please try again.", "error");
        });
    });

  const login42Link = document.getElementById("login42-link");
  login42Link.addEventListener("click", function (event) {
    event.preventDefault();
    window.location.href =
      "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-466f8ff9df025fc510352c0b2b970477cd8618f031b1e7e196e8f573b492ae53&redirect_uri=https%3A%2F%2F10.11.4.10&response_type=code";
  });
}

export function setupRegisterForm() {
  document
    .getElementById("registerForm")
    .addEventListener("submit", function (event) {
      event.preventDefault();

      const username = document.getElementById("username").value;
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      fetch("https://10.11.4.10/api/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Register failed");
          }
          return response.json();
        })
        .then((data) => {
          loadPage("login");
          showToast("Registration successful!", "success");
        })
        .catch((error) => {
          console.error("Registration error:", error);
          showToast("Registration failed. Please try again.", "error");
        });
    });
}

export function logout() {
  const email = getSenderEmail();
  fetch("https://10.11.4.10/api/logout/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email: email }), // E-posta adresini JSON formatında gönderiyoruz
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Logout failed");
      }
      localStorage.removeItem("jwt");
      localStorage.removeItem("jwt42");
      loadPage("login"); // Kullanıcıyı giriş sayfasına yönlendirin
      const socket = new WebSocket("wss://10.11.4.10/ws/status/userstatus/");
      socket.onopen = () => {
        socket.send("0");
        socket.close();
      };
      showToast("Logout successful!", "success");
    })
    .catch((error) => {
      console.error("Error:", error);
      showToast("Logout failed. Please try again.", "error");
    });
}

function base64UrlDecode(base64Url) {
  if (!base64Url) {
    console.error("Base64 URL is null or undefined.");
    return "";
  }
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  try {
    return atob(base64);
  } catch (e) {
    console.error("Error decoding base64:", e);
    return "";
  }
}

export function parseJWT(token, flag) {
  if (!token) {
    return {};
  }
  const parts = token.split(".");
  if (parts.length !== 3) {
    console.error("Invalid JWT token format.");
    return {};
  }

  const payload = parts[1];
  const decodedPayload = base64UrlDecode(payload);
  if (!decodedPayload) {
    console.error("Error decoding JWT payload.");
    return {};
  }

  const jsonPayload = decodeURIComponent(
    decodedPayload
      .split("")
      .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  );

  let parsedPayload;
  try {
    parsedPayload = JSON.parse(jsonPayload);
  } catch (e) {
    console.error("Error parsing JSON payload:", e);
    return {};
  }

  console.log("Parsed JWT Payload:", parsedPayload);

  // Token süresini kontrol edin
 // Token'ı kontrol eden ve çıkış yapan kod
//if (flag !== 1) {
//	const currentTime = Math.floor(Date.now() / 1000);
//	if (parsedPayload.exp && parsedPayload.exp < currentTime) {
//	  console.log("Token expired.");
//	  logout(); // Token süresi dolmuşsa çıkış yap
//	  showToast("Session expired. Please log in again.", "error");
//	}
//  }
  

  return parsedPayload;
}
