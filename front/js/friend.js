import { parseJWT } from "./auth.js";
import { loadPage } from "./pageLoader.js";

const socket = new WebSocket("wss://10.11.4.10/ws/status/userstatus/");
let chatSocket = null;
let currentRoomName = null;

function getSenderUsername() {
  const jwt = localStorage.getItem("jwt");
  if (!jwt) {
    return null;
  }
  const decoded = parseJWT(jwt);
  return decoded ? decoded.username : null;
}

function getSenderId() {
  const jwt = localStorage.getItem("jwt");
  if (!jwt) {
    return null;
  }
  const decoded = parseJWT(jwt);
  return decoded ? decoded.id : null;
}

async function getUserStatus(username) {
  const url = `https://10.11.4.10/api/user-status/${username}/`;
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (response.ok) {
      const data = await response.json();
      return data.status;
    } else {
      const errorText = await response.text();
      console.error(
        `Failed to fetch user status. Status: ${response.status}. Message: ${errorText}`
      );
      return null;
    }
  } catch (error) {
    console.error("Error fetching user status:", error);
    return null;
  }
}

export function setupFriendPage() {
  document.getElementById("sendRequestButton").addEventListener("click", () => {
    const receiverUsername = document.getElementById("usernameInput").value;
    const senderUsername = getSenderUsername();
    sendFriendRequest(senderUsername, receiverUsername);
    socket.send("1");
  });

  loadFriendsList();
  loadInvitations();
  loadBlockedList();
}

async function loadBlockedList() {
  const username = getSenderUsername();
  const url = `https://10.11.4.10/api/friend-request/blocked-list/?username=${username}`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const blockedUsers = await response.json();
    const blockedList = document.getElementById("BlockedList");
    blockedList.innerHTML = "";

    blockedUsers.forEach((user) => {
      const blockedUsername = user.username;
      const blockedBy = user.blocked_by;

      const item = document.createElement("li");
      item.className =
        "list-group-item d-flex justify-content-between align-items-center";

      const blockedNameSpan = document.createElement("span");
      blockedNameSpan.textContent = blockedUsername;
      item.appendChild(blockedNameSpan);

      if (blockedBy === getSenderId()) {
        const buttonContainer = document.createElement("div");
        const unblockButton = document.createElement("button");
        unblockButton.className = "btn btn-warning btn-sm ml-2";
        unblockButton.textContent = "Unblock";
        unblockButton.addEventListener("click", () =>
          unblockFriend(username, blockedUsername)
        );
        buttonContainer.appendChild(unblockButton);
        item.appendChild(buttonContainer);
      }

      blockedList.appendChild(item);
    });
  } catch (error) {
    console.error("Error fetching blocked list:", error);
  }
}

async function unblockFriend(senderUsername, blockedUsername) {
  const url = `https://10.11.4.10/api/friend-request/unblock/`;
  const data = {
    sender_username: senderUsername,
    receiver_username: blockedUsername,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      socket.send("2");
    } else {
      const errorResponse = await response.json();
      console.error("Error:", errorResponse);
    }
  } catch (error) {
    console.error("Fetch error:", error);
  }
}

async function sendFriendRequest(senderUsername, receiverUsername) {
  const url = "https://10.11.4.10/api/friend-request/send/";
  const data = {
    sender_username: senderUsername,
    username: receiverUsername,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      const jsonResponse = await response.json();
      console.log("Success:", jsonResponse);
    } else {
      const errorResponse = await response.json();
      console.error("Error:", errorResponse);
    }
  } catch (error) {
    console.error("Fetch error:", error);
  }
}

async function loadInvitations() {
  const username = getSenderUsername();
  const url = `https://10.11.4.10/api/friend-request/invitations/?username=${username}`;

  try {
    const response = await fetch(url);
    const invitations = await response.json();
    const invitationsList = document.getElementById("invitationsList");
    invitationsList.innerHTML = "";

    invitations.forEach((invitation) => {
      const item = document.createElement("div");
      item.className = "list-group-item";
      item.textContent = `From: ${invitation.sender__username}`;

      const yesButton = document.createElement("button");
      yesButton.className = "btn btn-success btn-sm ml-2";
      yesButton.textContent = "Yes";
      yesButton.addEventListener("click", () =>
        handleFriendRequest(invitation.sender__username, username, "accept")
      );

      const noButton = document.createElement("button");
      noButton.className = "btn btn-danger btn-sm ml-2";
      noButton.textContent = "No";
      noButton.addEventListener("click", () =>
        handleFriendRequest(invitation.sender__username, username, "decline")
      );

      item.appendChild(yesButton);
      item.appendChild(noButton);
      invitationsList.appendChild(item);
    });
  } catch (error) {
    console.error("Error fetching invitations:", error);
  }
}

async function blockFriend(senderUsername, receiverUsername) {
  const url = "https://10.11.4.10/api/friend-request/blocked/";
  const data = {
    sender_username: senderUsername,
    receiver_username: receiverUsername,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (response.ok) {
      socket.send("2");
      const jsonResponse = await response.json();
      console.log("Success:", jsonResponse);
    } else {
      const errorResponse = await response.json();
      console.error("Error:", errorResponse);
    }
  } catch (error) {
    console.error("Fetch error:", error);
  }
}

socket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.message === 0) loadFriendsList();
  else if (data.message === 1) loadInvitations();
  else {
    loadBlockedList();
    loadFriendsList();
  }
};

async function loadFriendsList() {
  const jwt = localStorage.getItem("jwt");

  if (!jwt) {
    return;
  }
  const username = getSenderUsername();
  const url = `https://10.11.4.10/api/friend-request/friends/?username=${username}`;

  try {
    const response = await fetch(url);
    const friends = await response.json();
    const friendsList = document.getElementById("friendsList");
    if (!friendsList) {
      return;
    }
    friendsList.innerHTML = "";

    for (const friend of friends) {
      const friendUsername =
        friend.receiver__username || friend.sender__username;
      const userStatus = await getUserStatus(friendUsername);
      const item = document.createElement("li");
      item.className =
        "list-group-item d-flex justify-content-between align-items-center";

      item.style.backgroundColor = userStatus ? "#d4edda" : "#f8d7da";

      const friendNameSpan = document.createElement("span");
      friendNameSpan.textContent = friendUsername;
      item.appendChild(friendNameSpan);

      const messageButton = document.createElement("button");
      messageButton.className = "btn btn-primary btn-sm ml-2";
      messageButton.textContent = "Message";
      messageButton.addEventListener("click", () =>
        openChatRoom(username, friendUsername)
      );

      const blockButton = document.createElement("button");
      blockButton.className = "btn btn-danger btn-sm ml-2";
      blockButton.textContent = "Block";
      blockButton.addEventListener("click", () =>
        blockFriend(username, friendUsername)
      );

      const infoButton = document.createElement("button");
      infoButton.className = "btn btn-info btn-sm ml-2";
      infoButton.textContent = "Info";
      infoButton.addEventListener("click", () => openModal(friendUsername));

      const buttonContainer = document.createElement("div");
      buttonContainer.appendChild(messageButton);
      buttonContainer.appendChild(blockButton);
      buttonContainer.appendChild(infoButton);
      item.appendChild(buttonContainer);

      friendsList.appendChild(item);
    }
  } catch (error) {
    console.error("Error fetching friends list:", error);
  }
}

function createModal() {
  const modalHTML = `
    <div class="modal fade" id="infoModal" tabindex="-1" aria-labelledby="infoModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="infoModalLabel">User Statistics</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <h4 id="usernameDisplay">Stats for User</h4>
            <table id="statsTable" class="table">
              <thead>
                <tr>
                  <th>Opponent</th>
                  <th>Winner</th>
                  <th>Loser</th>
                  <th>Host Score</th>
                  <th>Guest Score</th>
                </tr>
              </thead>
              <tbody>
                <!-- Data will be populated here -->
              </tbody>
            </table>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML("beforeend", modalHTML);
}

function openModal(username) {
  if (!document.getElementById("infoModal")) {
    createModal();
  }

  const infoModal = new bootstrap.Modal(document.getElementById("infoModal"));
  infoModal.show();

  grafikPage(username);
}

function grafikPage(username) {
  if (!username) {
    console.error("Username parameter is required.");
    return;
  }

  const url = `https://10.11.4.10/game/user-stats/${username}`;

  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById(
        "usernameDisplay"
      ).textContent = `Stats for ${data.username}`;
      const tableBody = document.querySelector("#statsTable tbody");
      tableBody.innerHTML = "";

      data.recent_games.forEach((game) => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${game.opponent}</td>
          <td>${game.winner}</td>
          <td>${game.loser}</td>
          <td>${game.hostScore}</td>
          <td>${game.guestScore}</td>
        `;

        tableBody.appendChild(row);
      });
    })
    .catch((error) => console.error("Error fetching user stats:", error));
}

async function handleFriendRequest(senderUsername, receiverUsername, action) {
  const url =
    action === "accept"
      ? "https://10.11.4.10/api/friend-request/accept/"
      : "https://10.11.4.10/api/friend-request/decline/";

  const data = {
    sender_username: senderUsername,
    receiver_username: receiverUsername,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      const jsonResponse = await response.json();
      console.log("Success:", jsonResponse);
    
      socket.send("0");
      loadFriendsList();
    } else {
      const errorResponse = await response.json();
      console.error("Error:", errorResponse);
    }
  } catch (error) {
    console.error("Fetch error:", error);
  }
}

function openChatRoom(username1, username2) {
  const sortedUsernames = [username1, username2].sort();
  const newRoomName = `${sortedUsernames[0]}_${sortedUsernames[1]}`;

  if (!currentRoomName || newRoomName !== currentRoomName) {
    currentRoomName = newRoomName;
    loadPage("friend").then(() => {
      setupChatRoom(newRoomName, username1);
    });
  } else {
    console.log("Same room, no need to reload the page.");
  }
}

function setupChatRoom(roomName, userName) {
  console.log("Setting up chat room...");

  document.getElementById(
    "username-display"
  ).innerText = `Chatting as: ${userName}`;

  if (chatSocket) {
    chatSocket.close();
  }

  chatSocket = new WebSocket(`wss://10.11.4.10/ws/chat/${roomName}/`);

  chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.message) {
      addMessageToChat(data.username, data.message, data.username === userName);
    }
  };

  chatSocket.onclose = function (e) {
    console.log("The socket closed unexpectedly");
  };

  function sendMessage() {
    if (chatSocket.readyState === WebSocket.OPEN) {
      const messageInputDom = document.querySelector("#chat-message-input");
      const message = messageInputDom.value.trim();

      if (message) {
        chatSocket.send(
          JSON.stringify({
            message: message,
            username: userName,
            room: roomName,
          })
        );

        messageInputDom.value = "";
      }
    } else {
      alert("WebSocket connection is not open.");
    }
  }

  document.querySelector("#chat-message-submit").onclick = sendMessage;

  document
    .querySelector("#chat-message-input")
    .addEventListener("keypress",
    function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    });
}

function addMessageToChat(username, message, isSent) {
  const chatMessages = document.querySelector("#chat-messages");
  const messageElement = document.createElement("div");
  messageElement.classList.add("message", isSent ? "sent" : "received");

  const usernameElement = document.createElement("div");
  usernameElement.classList.add("message-username");
  usernameElement.textContent = username;

  const messageTextElement = document.createElement("div");
  messageTextElement.classList.add("message-text");
  messageTextElement.textContent = message;

  const timeElement = document.createElement("div");
  timeElement.classList.add("message-time");
  timeElement.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  messageElement.appendChild(usernameElement);
  messageElement.appendChild(messageTextElement);
  messageElement.appendChild(timeElement);

  chatMessages.appendChild(messageElement);
  scrollToBottom();
}

function scrollToBottom() {
  const chatMessages = document.getElementById("chat-messages");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

document.addEventListener("DOMContentLoaded", setupFriendPage);