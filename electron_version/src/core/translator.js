const axios = require('axios');
const natural = require('natural');
const fs = require('fs');
const path = require('path');
const AIParagraphGrouper = require('./ai_paragraph');

class Translator {
    constructor(config) {
        this.tokenizer = new natural.SentenceTokenizer();
        
        // 从配置中获取 token
        this.token = config.translationToken;
        
        // 初始化 AI 分段器
        console.log('apiKey', config.aiKey);
        this.paragraphGrouper = new AIParagraphGrouper({
            model: config.aiProvider,
            apiKey: config.aiKey,
        });

        this.useAI = config.useAI;
        console.log('this.useAI', this.useAI);
    }
    
    // 分割句子
    splitSentences(text) {
        // 替换换行符为空格
        const noNewlines = text.replace(/[\r\n]+/g, ' ');
        return this.tokenizer.tokenize(noNewlines);
    }
    
    // 调用彩云小译 API
    async translate(sentences) {
        if (!this.token) {
            throw new Error('请在设置中配置彩云小译 Token');
        }
        
        try {
            const response = await axios.post(
                'http://api.interpreter.caiyunai.com/v1/translator',
                {
                    source: sentences,
                    trans_type: 'auto2zh',
                    request_id: 'demo',
                    detect: true,
                },
                {
                    headers: {
                        'content-type': 'application/json',
                        'x-authorization': `token ${this.token}`,
                    }
                }
            );
    
            if (response.status !== 200) {
                throw new Error(`翻译请求失败: ${response.status}`);
            }
    
            return response.data.target;
        } catch (error) {
            console.error('翻译出错:', error);
            throw error;
        }
    }
    
    // 主要翻译处理函数
    async processTranslation(text) {
        try {
            // 分割句子
            const sentences = this.splitSentences(text);
            if (sentences.length === 0) {
                return { success: false, message: '没有检测到有效文本' };
            }
    
            // 翻译句子
            const translatedText = await this.translate(sentences);
    
            // 组合原文和译文
            const result = sentences.map((source, index) => ({
                source,
                target: translatedText[index]
            }));
    
            // 如果启用了 AI 分段
            console.log('this.useAI', this.useAI);
            if (this.useAI) {
                const groupResult = await this.paragraphGrouper.groupSentences(sentences);
                if (groupResult.success) {
                    return {
                        success: true,
                        data: result,
                        paragraphs: groupResult.data,
                        originalText: text,
                        sentences: sentences,
                        translations: translatedText
                    };
                }
                else {
                    console.error('AI 分段失败:', groupResult.error);
                }
            }
    
            return {
                success: true,
                data: result,
                originalText: text,
                sentences: sentences,
                translations: translatedText
            };
    
        } catch (error) {
            return {
                success: false,
                message: error.message,
                error: error
            };
        }
    }
}
// 修改导出方式
module.exports = Translator;