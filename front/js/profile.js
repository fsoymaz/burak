import { parseJWT } from "./auth.js";
import { password } from "./password.js";
import { loadPage } from "./pageLoader.js";
export function setupProfile() {

  const namebutton = document.getElementById("name-button");

  let _cookie = document.cookie;
  let parse_cookie = parseJWT(_cookie);
  let img = document.querySelector("#profile-image");
  const user_name = document.querySelector("#username-id");
  user_name.textContent = parse_cookie.username;
  const name = document.querySelector("#name-button");
  name.textContent = parse_cookie.name;
  namebutton.textContent = parse_cookie.name;
  if (!parse_cookie.is_uploadpp)
    img.src = "../default/pp.png";
  else
    img.src = "../default/pp2.png";
  let twofa_button = document.getElementById('2fa-button');
  if (parse_cookie.twofactoractive)
    twofa_button.style.backgroundColor = 'green'; // Butonun arka plan rengini kırmızı yap
  else
    twofa_button.style.backgroundColor = 'red'; // Butonun arka plan rengini kırmızı yap

  function changeImage() {
    let _cookie = document.cookie;
    let parse_cookie = parseJWT(_cookie);
    fetch("https://10.11.4.10/api/uploadpp/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: parse_cookie.username,
        is_uploadpp: parse_cookie.is_uploadpp,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        let _cookie = document.cookie;
        let parse_cookie = parseJWT(_cookie);
        if (parse_cookie.is_uploadpp)
          img.src = "../default/pp2.png";
        else
          img.src = "../default/pp.png";

      })
      .catch((error) => console.log("Error:", error));
  }

  function activate2FA() {
    // Here you can add the logic to activate 2FA
    // alert('2FA Activate button clicked');
    _cookie = document.cookie
    parse_cookie = parseJWT(_cookie);
    fetch("https://10.11.4.10/api/2faactive/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: parse_cookie.username,
        twofactoractive: !parse_cookie.twofactoractive,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (parse_cookie.twofactoractive)
          twofa_button.style.backgroundColor = 'red';
        else
          twofa_button.style.backgroundColor = 'green';
      })
      .catch((error) => console.log("Error:", error));
  }

  function changePassword() {
    loadPage("password");
  }

  function makeEditable(field) {
    const buttonId = field === 'username' ? 'username-button' : 'name-button';
    const button = document.getElementById(buttonId);
    const currentValue = button.innerText;

    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentValue;
    input.className = 'input-field';
    input.onkeydown = function (event) {
      if (event.key === 'Enter') {
        saveValue(buttonId, input.value);
        fetch("https://10.11.4.10/api/updateuser/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: parse_cookie.email,
            flag: 3,
            name: input.value,
          }),
        })
          .catch((error) => console.log("Error:", error));
      }
    };
    button.replaceWith(input);
    input.focus();
    name.textContent = parse_cookie.name;
  }

  function saveValue(buttonId, value) {
    const button = document.createElement('button');
    button.className = 'info-button';
    button.id = buttonId;
    button.innerText = value;
    button.onclick = function () {
      makeEditable(buttonId.includes('username') ? 'username' : 'name');
    };

    const input = document.querySelector('.input-field');
    input.replaceWith(button);
  }
  document.getElementById('change-image-button').onclick = changeImage;
  document.getElementById('2fa-button').onclick = activate2FA;
  document.getElementById('change-password-button').onclick = changePassword;
  document.getElementById('name-button').onclick = function () { makeEditable('name'); };
}
