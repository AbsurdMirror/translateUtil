const { ipcRenderer } = require('electron');

class TranslationWindow {
    constructor() {
        console.log('TranslationWindow 初始化');
        this.initElements();
        this.bindEvents();
        this.handleIncomingText();
    }

    initElements() {
        console.log('初始化元素');
        this.closeBtn = document.getElementById('closeBtn');
        this.pinBtn = document.getElementById('pinBtn');
        this.copyBtn = document.getElementById('copyBtn');
        this.retranslateBtn = document.getElementById('retranslateBtn');
        this.translationContent = document.getElementById('translationContent');
        
        this.isPinned = false;
    }

    bindEvents() {
        this.closeBtn.onclick = () => {
            ipcRenderer.send('window-control', 'close');
        };

        this.pinBtn.onclick = () => {
            this.isPinned = !this.isPinned;
            ipcRenderer.send('pin-translation-window', this.isPinned);
            this.pinBtn.style.color = this.isPinned ? '#3498db' : '';
        };

        this.copyBtn.onclick = () => {
            const translatedText = Array.from(this.translationContent.querySelectorAll('.target'))
                .map(el => el.textContent)
                .join('\n');
            ipcRenderer.invoke('set-clipboard-text', translatedText);
        };

        this.retranslateBtn.onclick = () => {
            this.translate(this.lastText);
        };
    }

    async handleIncomingText() {
        console.log('设置翻译文本监听器');
        ipcRenderer.on('translate-text', async (event, text) => {
            console.log('收到要翻译的文本:', text);
            this.lastText = text;
            await this.translate(text);
        });
    }

    async translate(text) {
        if (!text) {
            console.log('没有要翻译的文本');
            return;
        }
    
        try {
            console.log('开始翻译文本');
            this.translationContent.innerHTML = '<div class="translation-item">正在翻译...</div>';
            
            const result = await ipcRenderer.invoke('translate-text', text);
            if (!result.success) {
                throw new Error(result.message);
            }
    
            // 显示翻译结果
            this.displayTranslation(result);
    
        } catch (error) {
            console.error('翻译失败:', error);
            this.translationContent.innerHTML = `<div class="translation-item error">翻译失败: ${error.message}</div>`;
        }
    }

    displayTranslation(translations) {
        if (translations.paragraphs && translations.paragraphs.length > 0) {
            // 使用 AI 分段显示
            this.displayWithParagraphs(translations);
        } else {
            // 普通显示模式
            this.displayNormal(translations.data);
        }
    }

    displayNormal(translations) {
        this.translationContent.innerHTML = translations.map(item => `
            <div class="translation-item">
                <div class="source">${item.source}</div>
                <div class="target">${item.target}</div>
            </div>
        `).join('');
    }

    displayWithParagraphs(translations) {
        const { data, paragraphs } = translations;
        
        this.translationContent.innerHTML = paragraphs.map(paragraph => {
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
                    <div class="paragraph-header">
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
        this.translationContent.querySelectorAll('.paragraph-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const card = header.closest('.paragraph-card');
                card.classList.toggle('collapsed');
            });
        });
    }
}

// 初始化窗口
document.addEventListener('DOMContentLoaded', () => {
    new TranslationWindow();
});