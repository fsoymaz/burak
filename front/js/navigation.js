import { loadPage } from "./pageLoader.js";
import { logout } from "./auth.js";

const defaultLinks = ["register", "login", "profile", "friend", "tournament"];

const specialLinks = {
  "game-link": function () {
    if (localStorage.getItem("jwt")) {
      loadPage("game");
    } else {
      alert("Please log in to access the game.");
      loadPage("login");
    }
  },
  "logout-link": function () {
    console.log("Logging out...");
    logout();
  },
};

export function setupNavLinks() {
  defaultLinks.forEach((link) => {
    const element = document.getElementById(`${link}-link`);
    if (element) {
      element.addEventListener("click", function (event) {
        event.preventDefault();
        loadPage(link);
      });
    }
  });

  Object.entries(specialLinks).forEach(([id, action]) => {
    document.getElementById(id)?.addEventListener("click", (event) => {
      event.preventDefault();
      action();
    });
  });
}

/*
Object.entries() metodu, bir nesnenin kendi enumerable özelliklerini,
 anahtar-değer çiftlerini içeren bir diziye dönüştürür. Bu metodu kullanarak,
 nesnenin her bir özelliğine kolayca erişebilir ve bu özellikleri üzerinde döngü oluşturabilirsiniz.

 ? işareti, JavaScript'te optional chaining (isteğe bağlı zincirleme) operatörü olarak bilinir.
*/

