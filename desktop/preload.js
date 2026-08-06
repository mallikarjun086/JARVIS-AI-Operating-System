const { contextBridge, ipcRenderer } = require('electron');

// Expose safe, isolated desktop IPC bridge to renderer process
contextBridge.exposeInMainWorld('jarvisDesktop', {
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
});
