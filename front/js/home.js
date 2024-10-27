import { loadPage } from "./pageLoader.js";
import { parseJWT } from "./auth.js";

/* export function setupHome() {
  // Add any JavaScript needed for the home page
  console.log("Home page setup complete.");
}
 */

export function setupHome() {
  var currentUrl = window.location.href;
  if (currentUrl.includes("code=") && !localStorage.getItem("jwt")) {
    var code = currentUrl.split("code=")[1];
    code = code.split(/[&#]/)[0];
    fetch("https://10.11.4.10/api/login42/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code: code,
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        if (data.token) {
          if (parseJWT(data.token).twofactoractive) {
            loadPage("2fa");
          } else {
            localStorage.setItem("jwt", data.token);
            window.location.href = "https://10.11.4.10/#home"; // Replace with your Google login URL
          }
        } else {
          console.error("JWT not found in response");
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
}
