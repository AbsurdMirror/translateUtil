const natural = require('natural');

class SentenceProcessor {
    constructor() {
        this.tokenizer = new natural.SentenceTokenizer();
    }

    // 分割句子
    splitSentences(text) {
        // 预处理文本
        const processedText = this.preProcessText(text);
        return this.tokenizer.tokenize(processedText);
    }

    // 文本预处理
    preProcessText(text) {
        if (!text) return '';

        return text
            // 统一换行符
            .replace(/\r\n/g, '\n')
            // 处理多个连续换行
            .replace(/\n{3,}/g, '\n\n')
            // 处理特殊标点符号
            .replace(/…/g, '...')
            .replace(/[""]/g, '"')
            .replace(/['']/g, "'")
            // 处理破折号
            .replace(/—/g, '-')
            // 处理省略号
            .replace(/\.{3,}/g, '...')
            // 处理多余的空格
            .replace(/\s+/g, ' ');
    }

    // 合并短句
    mergeSentences(sentences, minLength = 10) {
        const result = [];
        let currentSentence = '';

        for (const sentence of sentences) {
            if (currentSentence && (currentSentence.length + sentence.length) <= minLength) {
                currentSentence += ' ' + sentence;
            } else {
                if (currentSentence) {
                    result.push(currentSentence.trim());
                }
                currentSentence = sentence;
            }
        }

        if (currentSentence) {
            result.push(currentSentence.trim());
        }

        return result;
    }

    // 检测句子语言类型
    detectLanguage(sentence) {
        // 简单的语言检测规则
        const chineseRegex = /[\u4e00-\u9fa5]/;
        const englishRegex = /[a-zA-Z]/;
        
        const hasChineseChars = chineseRegex.test(sentence);
        const hasEnglishChars = englishRegex.test(sentence);

        if (hasChineseChars && !hasEnglishChars) return 'zh';
        if (!hasChineseChars && hasEnglishChars) return 'en';
        if (hasChineseChars && hasEnglishChars) return 'mixed';
        return 'unknown';
    }

    // 格式化段落
    formatParagraph(sentences) {
        return sentences.map(sentence => ({
            text: sentence.trim(),
            length: sentence.length,
            language: this.detectLanguage(sentence)
        }));
    }

    // 主处理函数
    process(text, options = {}) {
        const {
            minLength = 10,
            format = true
        } = options;

        try {
            // 分割句子
            const sentences = this.splitSentences(text);
            
            // 合并短句
            const mergedSentences = this.mergeSentences(sentences, minLength);
            
            // 返回结果
            return {
                success: true,
                original: text,
                sentences: format ? this.formatParagraph(mergedSentences) : mergedSentences,
                count: mergedSentences.length
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                original: text
            };
        }
    }
}

module.exports = new SentenceProcessor();