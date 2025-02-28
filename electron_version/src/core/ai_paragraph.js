const { OpenAI } = require('openai');

class AIParagraphGrouper {
    constructor(config = {}) {
        this.config = {
            model: config.model || 'deepseek',
            apiKey: config.apiKey || '',
            baseURL: config.baseURL || ''
        };
        
        this.client = null;
        this.systemPrompt = `
你是一个专业的文本分析助手，能够高效地将句子组织成段落，并对每个段落进行精准总结。你的任务是：
1. 依次接收句子输入，并记录这些句子。
2. 分析当前句子与之前句子的关联性。如果当前句子与之前的句子在主题或逻辑上存在明显断裂，则认为需要拆分为新的段落。
3. 每个段落尽量限制在3-5句之间。
4. 对每个段落进行内容总结，要简洁、一句话说明。

输出格式：
段落序号: [起始句子序号:结束句子序号] <段落总结>

示例：
1: [1:5] <介绍了段落的主题和背景。>
        `.trim();
    }

    async init() {
        if (this.config.model === 'deepseek') {
            this.client = new OpenAI({
                apiKey: this.config.apiKey,
                baseURL: 'https://api.deepseek.com'
            });
        } else if (this.config.model === 'zhipu') {
            console.log('初始化智谱 AI 客户端...', this.config.apiKey);
            this.client = new OpenAI({
                apiKey: this.config.apiKey,
                baseURL: 'https://open.bigmodel.cn/api/paas/v4/'
            });
        } else {
            throw new Error('不支持的 AI 模型');
        }
    }

    async groupSentences(sentences) {
        if (!this.client) {
            await this.init();
        }

        try {
            // 格式化输入文本
            const numberedSentences = sentences
                .map((sentence, index) => `${index + 1}: ${sentence}`)
                .join('\n');

            // 调用 AI API
            const response = await this.client.chat.completions.create({
                model: this.config.model === 'deepseek' ? 'deepseek-coder' : 'glm-4-airx',
                messages: [
                    { role: 'system', content: this.systemPrompt },
                    { role: 'user', content: numberedSentences }
                ],
                max_tokens: 8192,
                temperature: 0.7
            });

            // 解析 AI 响应
            const result = this.parseAIResponse(response.choices[0].message.content);
            console.log('AI 段落分组结果:', response.choices[0].message.content, result);
            return {
                success: true,
                data: result
            };

        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    parseAIResponse(response) {
        const paragraphs = [];
        const lines = response.split('\n');

        for (const line of lines) {
            console.log('parseAIResponse line:', line);
            const match = line.match(/(\d+):\s*\[(\d+):(\d+)\]\s*<(.+)>/);
            console.log('parseAIResponse match:', match);
            if (match) {
                paragraphs.push({
                    index: parseInt(match[1]),
                    start: parseInt(match[2]),
                    end: parseInt(match[3]),
                    summary: match[4].trim()
                });
            }
        }

        return paragraphs;
    }
}

module.exports = AIParagraphGrouper;