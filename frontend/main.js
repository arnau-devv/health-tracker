const { app, BrowserWindow, Menu, ipcMain} = require('electron');
const path = require('path');
const { spawn } = require('child_process');


// ----------- Main window -----------
let mainWindow
function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 750,
        minWidth: 750,
        minHeight: 700,
        // backgroundColor: '#00000000',  // Transparent
        // vibrancy: 'dark',              // MacOS
        // backgroundMaterial: 'acrylic',  // Windows 11+
        frame: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    })

    Menu.setApplicationMenu(null)
    mainWindow.loadFile('src/index.html')
    mainWindow.webContents.openDevTools()
}


// ----------- BACKEND STARTING -----------
const backendDir = path.join(__dirname, '..', 'backend');
const pythonExecutable = path.join(backendDir, 'venv', 'Scripts', 'python.exe');

function startPythonBackend() {
    pythonProcess = spawn(pythonExecutable, ['-u', 'main.py'], { cwd: backendDir });
    pythonProcess.stdout.on('data', (data) => console.log(`Python: ${data}`));
    pythonProcess.stderr.on('data', (data) => console.error(`Python error: ${data}`));
    pythonProcess.on('close', (code) => console.log(`Proceso Python cerrado con código ${code}`));
}


// =============================================================================
//  APP STARTUP
// =============================================================================
app.whenReady().then(() => {
    startPythonBackend();
    createMainWindow();
})


// =============================================================================
// MAIN WINDOW BUTTONS
// =============================================================================

//  ---- APP CLOSING
ipcMain.on('window-all-closed', () => {
    if (pythonProcess) pythonProcess.kill();
    app.quit();
})

//  ---- WINDOW MINIMIZE
ipcMain.on('minimize-window', () => {
    const win = BrowserWindow.getFocusedWindow();
    if (win) win.minimize();
})

//  ---- WINDOW JUSTING
ipcMain.on('ajust-window', () => {
    const win = BrowserWindow.getFocusedWindow();
    if (win) {
        if (win.isMaximized()) win.unmaximize();
        else win.maximize();
    }
});
