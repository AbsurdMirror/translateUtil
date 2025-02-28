const AIParagraphGrouper = require('./ai_paragraph');
const fs = require('fs');
const path = require('path');

async function testAIParagraphGrouper() {
    console.log('开始测试 AI 段落分组功能...\n');

    // 读取 API Key
    let apiKey;
    try {
        const tokenPath = path.join(__dirname, '../../../tokens_keys/zhipu.token');
        apiKey = fs.readFileSync(tokenPath, 'utf8').trim();
    } catch (error) {
        console.error('无法读取 API Key:', error);
        return;
    }

    // 创建分组器实例
    const grouper = new AIParagraphGrouper({
        model: 'zhipu',
        apiKey: apiKey
    });

    // 测试用例1：简单的英文段落
    try {
        console.log('测试用例1: 简单的英文段落');
        const sentences = [
            "The sun was setting behind the mountains.",
            "The sky was painted in beautiful shades of orange and pink.",
            "Birds were returning to their nests.",
            "In the city below, lights began to flicker on.",
            "Traffic was starting to thin out as people headed home.",
            "The night life was about to begin.",
            "Restaurants were preparing for dinner service.",
            "Street vendors were setting up their stalls."
        ];

        console.log('输入句子:', sentences);
        const result = await grouper.groupSentences(sentences);
        console.log('分组结果:', JSON.stringify(result, null, 2));
        console.log('测试用例1完成\n');
    } catch (error) {
        console.error('测试用例1失败:', error);
    }

    // 测试用例2：混合中英文段落
    try {
        console.log('测试用例2: 混合中英文段落');
        const sentences = [
            "人工智能正在改变我们的生活。",
            "It is becoming increasingly prevalent in our daily routines.",
            "从智能手机到智能家居，AI无处不在。",
            "Many people are concerned about its impact.",
            "但技术发展是不可阻挡的。",
            "We must learn to adapt to these changes.",
            "教育系统需要相应调整。",
            "未来的工作方式也会发生变化。"
        ];

        console.log('输入句子:', sentences);
        const result = await grouper.groupSentences(sentences);
        console.log('分组结果:', JSON.stringify(result, null, 2));
        console.log('测试用例2完成\n');
    } catch (error) {
        console.error('测试用例2失败:', error);
    }
}

// 运行测试
testAIParagraphGrouper().then(() => {
    console.log('测试完成');
}).catch(error => {
    console.error('测试过程中出错:', error);
});