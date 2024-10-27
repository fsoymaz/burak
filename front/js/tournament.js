import { parseJWT } from "./auth.js";
let cookie = document.cookie;
const parse_cookie = parseJWT(cookie);
const message = document.getElementById("message");
var pongCanvas = document.getElementById("pongCanvas");
var joinRoomButton = document.getElementById("join-room");
var StartGameButtons = document.getElementById("start-game");
var players;
var next_game_button;

var socket;
var roomName;
const data = {
    name: parse_cookie.username,
    action: "",
    message: ""
};

roomName = ''; // roomName değişkeni doğru şekilde tanımlandı


function gameLoop(e) {
    const canvas = document.getElementById("pongCanvas");
    const context = canvas.getContext("2d");
    const paddleWith = 10;
    const paddleHeight = 100;
    const canvasWidth = 800;
    const canvasHeight = 400;

    let leftPlayerScore = 0;
    let rightPlayerScore = 0;
    let leftPlayer = (canvasHeight - paddleHeight) / 2;
    let rightPlayer = (canvasHeight - paddleHeight) / 2;

    const action = JSON.parse(e.data);
    let ballX = action.BallX;
    let ballY = action.BallY;
    leftPlayerScore = action.leftPlayerScore;
    rightPlayerScore = action.rightPlayerScore;
    leftPlayer = action.leftPlayer;
    rightPlayer = action.rightPlayer;

    const drawRect = (x, y, w, h) => {
        context.fillStyle = "#FFF";
        context.fillRect(x, y, w, h);
    };

    const drawCircle = (x, y, r) => {
        context.fillStyle = "#FFF";
        context.beginPath();
        context.arc(x, y, r, 0, Math.PI * 2);
        context.closePath();
        context.fill();
    };

    const clearCanvas = () => context.clearRect(0, 0, canvasWidth, canvasHeight);

    const updateScore = () => {
        context.font = "30px Arial";
        context.fillStyle = "#FFF";
        context.fillText(leftPlayerScore, canvasWidth / 4, 50);
        context.fillText(rightPlayerScore, (canvasWidth * 3) / 4, 50);
    };

    const draw = () => {
        clearCanvas();
        drawRect(0, leftPlayer, paddleWith, paddleHeight);
        drawRect(canvasWidth - paddleWith, rightPlayer, paddleWith, paddleHeight);
        drawCircle(ballX, ballY, 10);
        updateScore();
    };

    const endGame = () => {
        clearCanvas();
        socket.close();
        fetch("https://10.11.4.10/tournament/end_game/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                roomNumber: roomName,
                username: parse_cookie.username,
            }),
        })
            .then((response) => response.ok ? response.json() : Promise.reject('Request failed'))
            .then((data) => {
                next_game_button = document.getElementById("next_game_button");
                console.log(data);
                pongCanvas.style.display = "none";
                if (data.result === "winner") {
                    message.textContent = "You win!";
                    message.style.color = "green";
                    next_game_button.style.display = "block";
                } else if (data.result === "loser") {
                    next_game_button.style.display = "none";
                    message.textContent = "You lose!";
                    message.style.color = "red";
                } else if (data.result === "f_winner") {
                    next_game_button.style.display = "none";
                    message.textContent = "You win the tournament!";
                    message.style.color = "green";
                }
            })
            .catch((error) => console.error('Error:', error));
    };

    draw();

    if (leftPlayerScore == 5 || rightPlayerScore == 5) endGame();
}

const movePaddles = (direction) => {
    data.action = "move";
    data.message = direction;
    socket.send(JSON.stringify(data));
};

document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") movePaddles(1);
    else if (e.key === "ArrowDown") movePaddles(2);
});


function generateRandomSixDigit() {
    return Math.floor(100000 + Math.random() * 900000);
}
export function setupTournament() {
    var flag = 0;
    pongCanvas = document.getElementById("pongCanvas");
    pongCanvas.style.display = "none";
    next_game_button = document.getElementById("next_game_button");
    roomName = generateRandomSixDigit();

    next_game_button.style.display = "none";

    next_game_button.addEventListener("click", function () {
        message.textContent = "";
        next_game_button.style.display = "none";
        socket = new WebSocket(`wss://10.11.4.10/ws/tournament/${roomName + "f"}/`);
        socket.onopen = function () {
            pongCanvas.style.display = "block";
            socket.send(JSON.stringify(data));
            socket.send(JSON.stringify({ start_game_f: playerName }));
            console.log("WebSocket bağlantısı kuruldu.");
        };
        socket.onmessage = function (event) {
            console.log("Mesaj alındı:", event.data);
            const data = JSON.parse(event.data);
            console.log(data.players);
            if (data.players !== undefined)
                players = data.players
            console.log("dorduncu");
            if (data.BallX !== undefined) {
                var usernames = document.getElementById("username");

                if (parse_cookie.username === players[0])
                    usernames.textContent = players[1];
                if (parse_cookie.username === players[1])
                    usernames.textContent = players[0];
                gameLoop(event);
            }
        };
    });


    document
        .getElementById("create-room")
        .addEventListener("submit", function (event) {
            event.preventDefault();
            const createbutton = document.getElementById("create-room-button");
            message.textContent = roomName;
            message.style.color = "yellow";
            createbutton.style.display = "none";
            message.textContent = roomName;
            joinRoomButton.style.display = "none";
            socket = new WebSocket(`wss://10.11.4.10/ws/tournament/${roomName}/`);

            socket.onopen = function () {
                console.log("WebSocket bağlantısı kuruldu.");
                socket.send(JSON.stringify(data));
                addPlayerToList(playerName);
            };
            socket.onmessage = function (event) {
                const data = JSON.parse(event.data);
                if (data.players !== undefined) {
                    players = data.players;
                    if (data.players.length > 4)
                        return;
                    updatePlayerList(data.players);
                }
                if (data.BallX !== undefined) {
                    var usernames = document.getElementById("username");

                    pongCanvas.style.display = "block";
                    if (parse_cookie.username === players[0])
                        usernames.textContent = players[2];
                    if (parse_cookie.username === players[1])
                        usernames.textContent = players[3];
                    if (parse_cookie.username === players[2])
                        usernames.textContent = players[0];
                    if (parse_cookie.username === players[3])
                        usernames.textContent = players[1];
                    gameLoop(event);
                }
            };


            fetch("https://10.11.4.10/tournament/create_room/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    roomNumber: roomName,
                    username: parse_cookie.username,
                }),
            })
                .then((response) => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error("Network response was not ok.");
                    }
                })
        });
    document
        .getElementById("join-room")
        .addEventListener("submit", function (event) {
            console.log("parse_cookie.username:           ", parse_cookie.username);
            event.preventDefault();
            roomName = document.getElementById("roomName").value;
            socket = new WebSocket(`wss://10.11.4.10/ws/tournament/${roomName}/`);
            const createbutton = document.getElementById("create-room-button");
            joinRoomButton.style.display = "none";
            createbutton.style.display = "none";
            StartGameButtons.style.display = "none";
            socket.onopen = function () {
                console.log("WebSocket bağlantısı kuruldu.");
                socket.send(JSON.stringify(data));
                addPlayerToList(playerName);
            };
            socket.onmessage = function (event) {
                const data = JSON.parse(event.data);
                console.log(data.players);
                if (data.BallX !== undefined) {
                    var usernames = document.getElementById("username");
                    pongCanvas.style.display = "block";
                    if (parse_cookie.username === players[0])
                        usernames.textContent = players[2];
                    if (parse_cookie.username === players[1])
                        usernames.textContent = players[3];
                    if (parse_cookie.username === players[2])
                        usernames.textContent = players[0];
                    if (parse_cookie.username === players[3])
                        usernames.textContent = players[1];
                    gameLoop(event);
                }
                else if (data.players !== undefined) {
                    players = data.players;
                    console.log("player data not undefined : ", players)
                    if (data.players.length > 4)
                        return;
                }
                if (data.players !== undefined)
                    updatePlayerList(data.players);

            };


            fetch("https://10.11.4.10/tournament/join_room/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    roomNumber: roomName,
                    username: parse_cookie.username,
                }),
            })
                .then((response) => {
                    if (response.ok) {
                        return response.json(); // JSON verisini alıyoruz
                    } else {
                        throw new Error("Network response was not ok.");
                    }
                })
            console.log(roomName);
            console.log("Connected to server");

        });

    const playersList = document.getElementById("players-list");
    const startGameButton = document.getElementById("start-game");

    const playerName = parse_cookie.username; // Bu oyuncunun ismini buraya koyun


    function addPlayerToList(player) {
        const li = document.createElement("li");
        li.textContent = player;
        playersList.appendChild(li);
    }

    function updatePlayerList(players) {
        playersList.innerHTML = "";

        players.forEach(player => {
            addPlayerToList(player);
        });

        if (players.length === 4) {
            startGameButton.classList.add("enabled");
            startGameButton.disabled = false;
            // startGameButton.addEventListener("click", startGame);
        }
    }

    document.getElementById("start-game").addEventListener("click", function () {
        console.log("Game started");
        StartGameButtons.style.display = "none";
        console.log("player data not undefined  START GAME: ", players);
        socket.send(JSON.stringify({ start_game: playerName }));
    });

}