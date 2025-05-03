const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // future IPC methods, e.g.:
  // send: (channel, data) => ipcRenderer.send(channel, data),
  // on: (channel, fn) => ipcRenderer.on(channel, (e, args) => fn(args))
});