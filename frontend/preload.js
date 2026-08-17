// ============================================================================================
//                                      PRELOAD SCRIPT
// - Runs in an isolated context with access to both Node APIs and the renderer's window.
// - Exposes a safe, limited API to the renderer (window.electronAPI) instead of
//   giving it direct access to ipcRenderer or Node internals.
// ============================================================================================
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    closeApp: () => ipcRenderer.send('window-all-closed'),
    minimizeApp: () => ipcRenderer.send('minimize-window'),
    ajustApp: () => ipcRenderer.send('ajust-window'),
});