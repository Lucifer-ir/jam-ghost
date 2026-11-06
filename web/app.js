const $ = (id) => document.getElementById(id);
const dialog = $("infoDialog");
const content = {
  qr: {
    title: "QR pairing is on the roadmap",
    text: "The next milestone will let one device create a one-time WebRTC offer QR code and the other device scan it to create an answer. The connection details will be exchanged locally between users."
  },
  invite: {
    title: "Invite codes are on the roadmap",
    text: "A compact text invitation will provide an alternative to camera scanning. The invite will carry connection setup data; it will not route or store chat messages."
  },
  start: {
    title: "Peer-to-peer is not active yet",
    text: "JAM GHOST v0.1 is the local interface foundation. WebRTC transport, secure pairing, and peer identity verification are planned for later releases."
  }
};

function showInfo(item) {
  const entry = content[item] || content.start;
  $("dialogTitle").textContent = entry.title;
  $("dialogText").textContent = entry.text;
  dialog.showModal();
}
$("startPairing").addEventListener("click", () => showInfo("start"));
$("openSettings").addEventListener("click", () => $("settings").scrollIntoView({behavior:"smooth"}));
document.querySelectorAll("[data-action]").forEach(button => {
  button.addEventListener("click", () => showInfo(button.dataset.action));
});
$("closeDialog").addEventListener("click", () => dialog.close());
$("dialogOk").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

const HISTORY_KEY = "jam-ghost-history-mode";
const historySelect = $("historyMode");
const saved = localStorage.getItem(HISTORY_KEY);
if (saved === "memory" || saved === "encrypted") historySelect.value = saved;
historySelect.addEventListener("change", () => {
  localStorage.setItem(HISTORY_KEY, historySelect.value);
  $("saveState").textContent = "Preference saved on this device.";
});
