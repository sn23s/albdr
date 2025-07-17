const { app, BrowserWindow } = require("electron");
const path = require("path");
const express = require("express");
const serveStatic = require("serve-static");
const { spawn } = require("child_process");

// Define the full path to python.exe
const pythonExecutable = 'C:\\Users\\mohammed\\AppData\\Local\\Programs\\Python\\Python313\\python.exe';

// Define the path to the backend main.py relative to the Electron app
const backendPath = path.join(__dirname, 'backend', 'src', 'main.py');

let mainWindow;
let expressApp;
let expressServer;
let backendProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false, // Set to false for security
      contextIsolation: true, // Set to true for security
    },
  });

  const frontendPath = path.join(__dirname, "frontend", "dist");
  const frontendPort = 8080; // منفذ الخادم المحلي للواجهة الأمامية
  const frontendUrl = `http://localhost:${frontendPort}`;
  const backendApiUrl = "http://127.0.0.1:5001"; // عنوان خادم Flask

  expressApp = express( );
  expressApp.use(express.json());

  // Handle API requests directly instead of using proxy
  expressApp.all('/api/*', async (req, res) => {
    try {
      const apiPath = req.path.replace('/api', '');
      const backendUrl = `${backendApiUrl}/api${apiPath}`;
      
      console.log(`Forwarding ${req.method} ${req.path} to ${backendUrl}`);
      
      const fetch = require('node-fetch');
      
      const options = {
        method: req.method,
        headers: {
          'Content-Type': 'application/json'
        }
      };
      
      if (req.method !== 'GET' && req.method !== 'HEAD') {
        options.body = JSON.stringify(req.body);
      }
      
      const response = await fetch(backendUrl, options);
      const data = await response.text();
      
      res.status(response.status);
      
      // Set only safe headers
      res.set('Content-Type', response.headers.get('content-type') || 'application/json');
      
      try {
        const jsonData = JSON.parse(data);
        res.json(jsonData);
      } catch {
        res.send(data);
      }
      
    } catch (error) {
      console.error('API forwarding error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  expressApp.use(serveStatic(frontendPath));

  // Start the backend process
  backendProcess = spawn(pythonExecutable, [backendPath]);

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
  });

  expressServer = expressApp.listen(frontendPort, () => {
    console.log(`Express server for frontend started on port ${frontendPort}`);
    mainWindow.loadURL(frontendUrl);
  }).on("error", (err) => {
    console.error(`Failed to start Express server: ${err.message}`);
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
  if (expressServer) {
    expressServer.close(() => {
      console.log("Express server closed.");
    });
  }
  if (backendProcess) {
    backendProcess.kill();
  }
});
