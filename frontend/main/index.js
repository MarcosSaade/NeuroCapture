// frontend/main/index.js
const { app, BrowserWindow } = require("electron");
const path = require("path");
const net = require("net");

const isDev = process.env.NODE_ENV === "development";
const VITE_URL = "http://localhost:5173";

function waitForViteReady(url, timeout = 10000) {
  const { hostname, port } = new URL(url);
  return new Promise((resolve, reject) => {
    const start = Date.now();
    (function check() {
      const socket = net.createConnection(port, hostname, () => {
        socket.end();
        resolve();
      });
      socket.on("error", () => {
        if (Date.now() - start > timeout) {
          reject(new Error("Timed out waiting for Vite server"));
        } else {
          setTimeout(check, 100);
        }
      });
    })();
  });
}

async function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    console.log("⚡ Running in development mode. Waiting for Vite at", VITE_URL);
    try {
      await waitForViteReady(VITE_URL);
      console.log("✅ Vite is up! Loading", VITE_URL);
      await mainWindow.loadURL(VITE_URL);
      mainWindow.webContents.openDevTools({ mode: "detach" });
    } catch (err) {
      console.error("❌ Vite server not ready:", err);
      // Show a simple error page if dev build isn’t available
      mainWindow.loadURL("data:text/html,<h1>Vite failed to start</h1><p>Check your terminal.</p>");
    }
  } else {
    const indexPath = path.join(__dirname, "../renderer/dist/index.html");
    console.log("📦 Running in production, loading", indexPath);
    await mainWindow.loadFile(indexPath);
  }
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
