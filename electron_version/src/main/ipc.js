const { ipcMain, clipboard } = require('electron');
const Translator = require('../core/translator');
const config = require('../utils/config');
const crypto = require('../utils/crypto');

// 创建翻译器实例
let decryptedKey = '';
if (config.get('aiKey')) {
    decryptedKey = crypto.decrypt(config.get('aiKey'));
    console.log('update-translator-config: Decrypted API Key:', config.get('aiKey'), decryptedKey);
}

let translator = new Translator({
    aiProvider: config.get('aiProvider'),
    aiKey: decryptedKey,
    useAI: config.get('useAI')
});

const sentenceProcessor = require('../utils/sentence');

class IPCHandler {
    constructor() {
        this.registerHandlers();
    }

    registerHandlers() {
        // 翻译相关
        ipcMain.handle('translate-text', async (event, text) => {
            // console.log('registerHandlers: Received text for translation:', text);
            try {
                const result = await translator.processTranslation(text);
                return result;
            } catch (error) {
                return {
                    success: false,
                    message: error.message
                };
            }
        });

        // 剪贴板相关
        ipcMain.handle('get-clipboard-text', () => {
            return clipboard.readText();
        });

        ipcMain.handle('set-clipboard-text', (event, text) => {
            clipboard.writeText(text);
            return true;
        });

        // 配置相关
        ipcMain.handle('get-config', (event, key) => {
            return config.get(key);
        });

        ipcMain.handle('set-config', (event, key, value) => {
            return config.set(key, value);
        });

        ipcMain.handle('get-all-config', () => {
            return config.getAll();
        });

        // 句子处理相关
        ipcMain.handle('process-sentences', (event, text, options) => {
            return sentenceProcessor.process(text, options);
        });

        // 窗口控制相关
        ipcMain.on('window-control', (event, command) => {
            const window = event.sender.getOwnerBrowserWindow();
            switch (command) {
                case 'minimize':
                    window.minimize();
                    break;
                case 'maximize':
                    window.isMaximized() ? window.unmaximize() : window.maximize();
                    break;
                case 'close':
                    window.close();
                    break;
            }
        });


        ipcMain.handle('update-translator-config', async (event, newConfig) => {
            console.log('update-translator-config:', newConfig);
            try {
                // 解密 API Key
                let decryptedKey = '';
                if (newConfig.aiKey) {
                    decryptedKey = crypto.decrypt(newConfig.aiKey);
                    console.log('update-translator-config: Decrypted API Key:', newConfig.aiKey, decryptedKey);
                }

                // 更新翻译器配置
                console.log('update-translator-config: Updating translator config...');
                translator = new Translator({
                    useAI: newConfig.useAI,
                    aiProvider: newConfig.aiProvider,
                    aiKey: decryptedKey
                });

                return { success: true };
            } catch (error) {
                console.error('更新翻译器配置失败:', error);
                return { success: false, message: error.message };
            }
        });
    }
}

module.exports = new IPCHandler();