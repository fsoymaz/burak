import { loadPage } from "./pageLoader.js";
import { parseJWT } from "./auth.js";

export function password(flag_mail) {
    console.log("flag_mail" + flag_mail)
    let _cookie = document.cookie;
    let flag = 0;

    const emailDiv = document.getElementById('emailDiv');
    const otpInput = document.getElementById('otpInput');
    const newPasswords = document.getElementById('newPasswords');

    if (_cookie) {
        emailDiv.style.display = 'none';
        otpInput.style.display = 'none';
    }
    else if (flag_mail) {
        emailDiv.style.display = 'block';
        otpInput.style.display = 'block';
        newPasswords.style.display = 'block';
        flag = 0;
    }
    else {
        emailDiv.style.display = 'block';
        otpInput.style.display = 'none';
        newPasswords.style.display = 'none';
        flag = 1;
    }

    document.getElementById('resetForm').addEventListener('submit', function (event) {
        event.preventDefault();
        const email = document.getElementById("email").value;
        if (!_cookie && email == "")
            console.log("Error:");

        if (_cookie) {
            const newPassword = document.getElementById("newPassword").value;
            let parse_cookie = parseJWT(_cookie);
            fetch("https://10.11.4.10/api/updateuser/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: parse_cookie.email,
                    password: newPassword,
                    flag: 1,
                }),
            })
                .then(response => {
                    if (response.ok) { loadPage("profile") }
                    else {
                        console.log("Error:");
                    }
                })
        }
        else if (flag == 1) {
            console.log("asdasd" + email);
            fetch("https://10.11.4.10/api/updateuser/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: email,
                    flag: 2
                }),
            })
                .then(response => {
                    if (response.ok) {
                        password(1);
                    } else {
                        console.log("Error:");
                    }
                })
        }
        else {
            const newPassword = document.getElementById("newPassword").value;
            const otp = document.getElementById("otp").value;
            fetch("https://10.11.4.10/api/updateuser/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: email,
                    password: newPassword,
                    otpInput: otp,
                    flag: 0
                }),
            })
                .then(response => {
                    if (response.ok) {
                        loadPage("login")
                    } else {
                        console.log("Error:");
                    }
                })
        }
    });
}