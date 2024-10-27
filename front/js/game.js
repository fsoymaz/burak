import { parseJWT } from "./auth.js";
import { loadPage } from "./pageLoader.js";

var join_Room;
var create_Room;
var message;
let _cookie;
let parse_cookie;

// join_Room.style.display = 'block';
// create_Room.style.display = 'block';

function gameLoop(roomName, isHost, isPlayerA) {
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

  var ballX;
  var ballY;

  const ws = new WebSocket(`wss://10.11.4.10/ws/game/${roomName}/`);

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

  const movePaddle = (direction) => {
    if (isPlayerA) {
      if (direction === 1) {
        ws.send("2");
      } else {
        ws.send("1");
      }
    } else {
      if (direction === 1) {
        ws.send("4");
      } else {
        ws.send("3");
      }
    }
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
    ws.close(); // WebSocket bağlantısını kapat
    fetch("https://10.11.4.10/game/end_game/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        roomNumber: roomName,
        username: parse_cookie.username,
        playerScore: leftPlayerScore,
        opponentScore: rightPlayerScore,
      }),
    })
      .then((response) => {
        if (response.ok) {
          return response.json(); // JSON verisini alıyoruz
        } else {
          throw new Error("Network response was not ok.");
        }
      })
      .then((data) => {
        const canva = document.getElementById("gameCanvas");
        canva.style.display = "none";

        const retrybutton = document.getElementById("retry-id");
        retrybutton.style.display = "block";

        const winner = document.getElementById("winner");
        if (data[0] === parse_cookie.username) {
          winner.textContent = "You win!";
          winner.style.color = "green";
          console.log("You win!");
        } else {
          console.log("You lose!");
          winner.textContent = "You lose!";
          winner.style.color = "red";
        }
      })
      .catch(() => console.log("Error: Could not end the game."));
  };

  ws.onopen = () => {
    ws.send(0);
  };

  ws.onmessage = (e) => {
    message.style.display = "none";
    const action = JSON.parse(e.data);
    ballX = action.BallX;
    ballY = action.BallY;
    leftPlayerScore = action.leftPlayerScore;
    rightPlayerScore = action.rightPlayerScore;
    leftPlayer = action.leftPlayer;
    rightPlayer = action.rightPlayer;
    draw();
    if (leftPlayerScore == 5 || rightPlayerScore == 5) endGame();
  };

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") movePaddle(1);
    else if (e.key === "ArrowDown") movePaddle(2);
  });
}

function generateRandomSixDigit() {
  return Math.floor(100000 + Math.random() * 900000);
}

export function setupGame() {
  _cookie = document.cookie;
  parse_cookie = parseJWT(_cookie);
  join_Room = document.getElementById("join-room");
  create_Room = document.getElementById("create-room");
  message = document.getElementById("message");
  const retrybutton = document.getElementById("retry-id");
  retrybutton.style.display = "none";

  document
    .getElementById("create-room")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      const roomName = generateRandomSixDigit();
      join_Room.style.display = "none";
      create_Room.style.display = "none";
      message.textContent = roomName;
      message.style.color = "yellow";
      console.log("Connected to server");
      console.log(parse_cookie.username);

      fetch("https://10.11.4.10/game/create_room/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username_host: parse_cookie.username,
          roomNumber: roomName,
        }),
      }).then((response) => {
        if (response.ok) {
          console.log("Room created, waiting for guest...");
          gameLoop(roomName, true, true);
        } else {
          console.log("Error: Room creation failed.");
        }
      });
    });

  document
    .getElementById("join-room")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      const roomName = document.getElementById("roomName").value;
      join_Room.style.display = "none";
      create_Room.style.display = "none";
      console.log(roomName);
      console.log("Connected to server");
      fetch("https://10.11.4.10/game/join_room/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username_guest: parse_cookie.username,
          roomNumber: roomName,
        }),
      }).then((response) => {
          console.log("Joined the game, notifying host...");
          gameLoop(roomName, false, false);
      });
    });

  document
    .getElementById("retry-id")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      loadPage("game");
    });
}
