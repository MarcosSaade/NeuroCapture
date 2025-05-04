console.log('🔥 ELECTRON MAIN STARTED, NODE_ENV=', process.env.NODE_ENV);

const { app, BrowserWindow } = require('electron');
const path = require('path');

async function createWindow() {
  const isDev = process.env.NODE_ENV === 'development';
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    const devURL = 'http://localhost:5173/'; 
    console.log('⏳ Loading dev URL:', devURL);

    // give the Vite server a moment to start
    await new Promise((resolve) => setTimeout(resolve, 1000));

    mainWindow
      .loadURL(devURL)
      .catch((err) => {
        console.error('❌ Failed to load dev URL:', err);
        mainWindow.loadURL(`data:text/html,
          <h1 style="color:red">Cannot connect to Dev Server</h1>
          <p>Is Vite running on port 5173?</p>`).then(() => console.log('✅ loadURL succeeded'))
          .catch((e) => console.error('❌ loadURL failed:', e));          
      });

    mainWindow.webContents.openDevTools();
  } else {
    const indexPath = path.join(__dirname, '../renderer/dist/index.html');
    console.log('✅ Loading prod file:', indexPath);
    mainWindow.loadFile(indexPath);
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
