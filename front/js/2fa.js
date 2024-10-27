import { loadPage } from "./pageLoader.js";
import { parseJWT } from "./auth.js";

export function verifyCode() {
  document
    .getElementById("verifyButton")
    .addEventListener("click", function () {
      const userCode = document.getElementById("userCode").value;
      const message = document.getElementById("message");
      let _cookie = document.cookie;
      const parse_cookie = parseJWT(_cookie);
      fetch("https://10.11.4.10/api/2fa/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: parse_cookie.username,
          userCode: userCode,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.token) {
            message.textContent = "Verification successful!";
            message.style.color = "green";
            localStorage.setItem("jwt", data.token);
            loadPage("home");
          } else {
            message.textContent = "Invalid code. Please try again.";
            message.style.color = "red";
          }
        })
        .catch((error) => {
          console.error("There was a problem with the fetch operation:", error);
          message.textContent = "Service Error";
          message.style.color = "red";
        });
    });
}
