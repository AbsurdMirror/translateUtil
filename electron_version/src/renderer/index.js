const { ipcRenderer } = require('electron');
const crypto = require('../utils/crypto');

class TranslatorUI {
    constructor() {
        this.initElements();
        this.bindEvents();
        this.loadConfig();
    }

    // 初始化 DOM 元素引用
    initElements() {
        // 窗口控制
        this.minimizeBtn = document.getElementById('minimizeBtn');
        this.maximizeBtn = document.getElementById('maximizeBtn');
        this.closeBtn = document.getElementById('closeBtn');

        // 文本区域
        this.sourceText = document.getElementById('sourceText');
        this.viewModeBtn = document.getElementById('viewModeBtn');
        this.targetText = document.getElementById('targetText');

        // 控制按钮
        this.pasteBtn = document.getElementById('pasteBtn');
        this.clearSourceBtn = document.getElementById('clearSourceBtn');
        this.copyBtn = document.getElementById('copyBtn');
        this.clearTargetBtn = document.getElementById('clearTargetBtn');
        this.translateBtn = document.getElementById('translateBtn');

        // 设置相关
        this.targetLang = document.getElementById('targetLang');
        this.statusText = document.getElementById('statusText');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.useAI = document.getElementById('useAI');
        this.aiProvider = document.getElementById('aiProvider');
        this.aiKey = document.getElementById('aiKey');

        // 设置面板控制
        this.settingsBtn = document.getElementById('settingsBtn');
        this.closeSettingsBtn = document.getElementById('closeSettingsBtn');
    }

    // 绑定事件
    bindEvents() {
        // 窗口控制
        this.minimizeBtn.onclick = () => ipcRenderer.send('window-control', 'minimize');
        this.maximizeBtn.onclick = () => ipcRenderer.send('window-control', 'maximize');
        this.closeBtn.onclick = () => ipcRenderer.send('window-control', 'close');

        // 翻译功能
        this.translateBtn.onclick = () => this.handleTranslate();
        this.sourceText.onkeydown = (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.handleTranslate();
            }
        };

        // 剪贴板操作
        this.pasteBtn.onclick = async () => {
            const text = await ipcRenderer.invoke('get-clipboard-text');
            this.sourceText.value = text;
        };

        this.copyBtn.onclick = () => {
            const text = this.targetText.innerText;
            ipcRenderer.invoke('set-clipboard-text', text);
            this.updateStatus('已复制到剪贴板');
        };

        // 清空按钮
        this.clearSourceBtn.onclick = () => {
            this.sourceText.value = '';
            this.sourceText.focus();
        };

        this.clearTargetBtn.onclick = () => {
            this.targetText.innerHTML = '';
        };

        // 设置变更
        this.targetLang.onchange = () => this.saveConfig();
        this.useAI.onclick = () => this.saveConfig();
        this.aiProvider.onchange = () => this.saveConfig();
        this.aiKey.onchange = () => this.saveConfig();
        
        // 设置面板控制
        this.settingsBtn.onclick = () => this.toggleSettings(true);
        this.closeSettingsBtn.onclick = () => this.toggleSettings(false);

        // 视图模式切换
        this.viewModeBtn.onclick = () => {
            const currentMode = this.targetText.getAttribute('data-view-mode');
            const newMode = currentMode === 'both' ? 'target-only' : 'both';
            this.targetText.setAttribute('data-view-mode', newMode);
            this.viewModeBtn.textContent = newMode === 'both' ? '仅显示译文' : '显示原文';
        };
    
    }

    // 加载配置
    async loadConfig() {
        const config = await ipcRenderer.invoke('get-all-config');
        if (config) {
            this.targetLang.value = config.translation.targetLang;
            this.useAI.checked = config.useAI;
            this.aiProvider.value = config.aiProvider;
            
            // 解密并显示 API Key
            if (config.aiKey) {
                const decryptedKey = crypto.decrypt(config.aiKey);
                this.aiKey.value = decryptedKey || '';
            }
        }
    }

    // 保存配置
    async saveConfig() {
        console.log('Saving config...');
        const config = {
            translation: {
                targetLang: this.targetLang.value
            },
            useAI: this.useAI.checked,
            aiProvider: this.aiProvider.value
        };

        // 加密保存 API Key
        if (this.aiKey.value) {
            config.aiKey = crypto.encrypt(this.aiKey.value);
        }

        await ipcRenderer.invoke('set-config', 'translation', config.translation);
        await ipcRenderer.invoke('set-config', 'useAI', config.useAI);
        await ipcRenderer.invoke('set-config', 'aiProvider', config.aiProvider);
        await ipcRenderer.invoke('set-config', 'aiKey', config.aiKey);
        
        // 通知主进程更新翻译器配置
        await ipcRenderer.invoke('update-translator-config', config);
    }

    // 处理翻译
    async handleTranslate() {
        const text = this.sourceText.value.trim();
        if (!text) {
            this.updateStatus('请输入要翻译的文本');
            return;
        }

        this.updateStatus('正在翻译...');
        this.translateBtn.disabled = true;

        try {
            // 处理文本
            const processedResult = await ipcRenderer.invoke('process-sentences', text);
            if (!processedResult.success) {
                throw new Error(processedResult.error);
            }

            // 翻译文本
            const result = await ipcRenderer.invoke('translate-text', text);
            if (!result.success) {
                throw new Error(result.message);
            }

            // 显示结果
            this.displayTranslation(result);
            this.updateStatus('翻译完成');

        } catch (error) {
            this.updateStatus(`翻译失败: ${error.message}`);
        } finally {
            this.translateBtn.disabled = false;
        }
    }

    // 显示翻译结果
    displayTranslation(translations) {
        console.log("displayTranslation", translations)
        if (translations.paragraphs && translations.paragraphs.length > 0) {
            // 使用 AI 分段显示
            this.displayWithParagraphs(translations);
        } else {
            // 普通显示模式
            this.displayNormal(translations.data);
        }
    }

    // 普通显示模式
    displayNormal(translations) {
        this.targetText.innerHTML = translations.map(item => `
            <div class="translation-item">
                <div class="source">${item.source}</div>
                <div class="target">${item.target}</div>
            </div>
        `).join('');
    }

    // AI 分段显示模式
    displayWithParagraphs(translations) {
        const { data, paragraphs } = translations;
        
        this.targetText.innerHTML = paragraphs.map(paragraph => {
            const sentenceIndexes = Array.from(
                { length: paragraph.end - paragraph.start + 1 },
                (_, i) => paragraph.start - 1 + i
            );
            
            const sentences = sentenceIndexes.map(index => `
                <li class="sentence-item">
                    <div class="source">${data[index].source}</div>
                    <div class="target">${data[index].target}</div>
                </li>
            `).join('');

            return `
                <div class="paragraph-card">
                    <div class="paragraph-header" onclick="this.parentElement.classList.toggle('collapsed')">
                        <h4 class="paragraph-summary">${paragraph.summary}</h4>
                        <button class="collapse-btn">▼</button>
                    </div>
                    <div class="paragraph-content">
                        <ul class="sentence-list">
                            ${sentences}
                        </ul>
                    </div>
                </div>
            `;
        }).join('');

        // 绑定折叠事件
        this.targetText.querySelectorAll('.paragraph-header').forEach(header => {
            header.addEventListener('click', (e) => {
                if (e.target.classList.contains('collapse-btn')) return;
                const card = header.closest('.paragraph-card');
                card.classList.toggle('collapsed');
            });
        });
    }
    
    // 更新状态显示
    updateStatus(message) {
        this.statusText.textContent = message;
    }

    // 切换设置面板显示状态
    toggleSettings(show) {
        if (show) {
            this.settingsPanel.classList.remove('hidden');
        } else {
            this.settingsPanel.classList.add('hidden');
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new TranslatorUI();
});