// Svelte version boot script for eDEX-UI
const electron = require("electron");
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const path = require("path");
const url = require("url");
const fs = require("fs");

app.commandLine.appendSwitch("disable-http-cache");

app.on("ready", () => {
    // Create window with Svelte-specific settings
    let win = new BrowserWindow({
        width: 1280,
        height: 720,
        show: false,
        frame: false,
        backgroundColor: '#000000',
        webPreferences: {
            nodeIntegration: true,
            enableRemoteModule: true,
            contextIsolation: false
        }
    });

    // Load the Svelte version of eDEX-UI
    win.loadURL(url.format({
        pathname: path.join(__dirname, 'ui_svelte.html'),
        protocol: 'file:',
        slashes: true
    }));

    // Create a directory for Svelte build files if it doesn't exist
    const buildDir = path.join(__dirname, 'build');
    if (!fs.existsSync(buildDir)) {
        fs.mkdirSync(buildDir);
    }

    win.webContents.on("did-finish-load", () => {
        win.show();
        win.focus();
    });

    win.webContents.on("devtools-opened", () => {
        win.focus();
    });

    // Open developer tools in development mode
    if (process.argv.includes("--dev")) {
        win.webContents.openDevTools();
    }
});

app.on("window-all-closed", () => {
    app.quit();
}); 