const { app, BrowserWindow, globalShortcut, ipcMain, clipboard } = require('electron');
const path = require('path');
require('./ipc');

// 保持窗口对象的全局引用，避免被 JavaScript 垃圾回收
let mainWindow = null;
let translationWindow = null;
let inputWindow = null;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createTranslationWindow() {
  translationWindow = new BrowserWindow({
    width: 400,
    height: 500,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    show: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  translationWindow.loadFile(path.join(__dirname, '../renderer/translation.html'));

  translationWindow.on('closed', () => {
    translationWindow = null;
  });

  return translationWindow;
}

// 注册快捷键
function registerShortcuts() {
  // 使用 electron 的全局快捷键
  globalShortcut.register('CommandOrControl+O', async () => {
    // 获取剪贴板内容
    const clipboardText = clipboard.readText();
    console.log('剪贴板内容:', clipboardText);

    // 如果剪贴板有内容
    if (clipboardText && clipboardText.trim()) {
      console.log('准备创建翻译窗口');
      if (!translationWindow) {
        translationWindow = createTranslationWindow();
        console.log('创建新的翻译窗口');
        // 等待窗口加载完成
        translationWindow.webContents.on('did-finish-load', () => {
          console.log('翻译窗口加载完成，发送文本');
          translationWindow.webContents.send('translate-text', clipboardText);
        });
      }

      // 获取鼠标位置
      const screen = require('electron').screen;
      const mousePos = screen.getCursorScreenPoint();
      console.log('鼠标位置:', mousePos);

      translationWindow.setPosition(mousePos.x + 10, mousePos.y + 10);
      translationWindow.show();
    } else {
      console.log('剪贴板没有内容');
    }
  });
  console.log('快捷键注册完成');
}

function createInputWindow() {
  inputWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  inputWindow.loadFile(path.join(__dirname, '../renderer/input.html'));

  inputWindow.on('closed', () => {
    inputWindow = null;
  });
}

// 应用准备就绪时
app.whenReady().then(() => {
  console.log('应用程序准备就绪');
  createMainWindow();
  registerShortcuts();
  console.log('初始化完成');

  // macOS 应用激活时重新创建窗口
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

// 所有窗口关闭时退出应用
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// 注销所有快捷键
app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

// IPC 通信处理
ipcMain.on('update-window-position', (event, { x, y }) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) {
    win.setPosition(x, y);
  }
});

ipcMain.on('close-window', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) {
    win.close();
  }
});