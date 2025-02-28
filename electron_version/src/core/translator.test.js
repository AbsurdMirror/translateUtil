const Translator = require('./translator');
const fs = require('fs');
const path = require('path');

async function testTranslator() {
    console.log('开始测试翻译功能...\n');

    // 读取配置
    const config = {
        useAI: true,
        aiProvider: 'zhipu',
        aiKey: ''
    };

    // 读取 AI API Key
    try {
        const tokenPath = path.join(__dirname, '../../../tokens_keys/zhipu.token');
        config.aiKey = fs.readFileSync(tokenPath, 'utf8').trim();
    } catch (error) {
        console.error('无法读取 AI API Key:', error);
        return;
    }

    // 创建翻译器实例
    const translator = new Translator(config);

    // 测试用例1：普通英文句子
    try {
        console.log('测试用例1: 普通英文句子');
        const text = "The sun was setting behind the mountains. The sky was painted in beautiful shades of orange and pink. Birds were returning to their nests.";
        
        console.log('输入文本:', text);
        const result = await translator.processTranslation(text);
        console.log('翻译结果:', JSON.stringify(result, null, 2));
        console.log('测试用例1完成\n');
    } catch (error) {
        console.error('测试用例1失败:', error);
    }

    // 测试用例2：包含换行符的文本
    try {
        console.log('测试用例2: 包含换行符的文本');
        const text = `First line of text.
Second line with different content.
Third line about something else.`;
        
        console.log('输入文本:', text);
        const result = await translator.processTranslation(text);
        console.log('翻译结果:', JSON.stringify(result, null, 2));
        console.log('测试用例2完成\n');
    } catch (error) {
        console.error('测试用例2失败:', error);
    }

    // 测试用例3：中英混合文本
    try {
        console.log('测试用例3: 中英混合文本');
        const text = "AI is changing our lives. 这是一个重要的转变。Technology keeps evolving. 我们需要适应这些变化。";
        
        console.log('输入文本:', text);
        const result = await translator.processTranslation(text);
        console.log('翻译结果:', JSON.stringify(result, null, 2));
        console.log('测试用例3完成\n');
    } catch (error) {
        console.error('测试用例3失败:', error);
    }

    // 测试用例4：空文本
    try {
        console.log('测试用例4: 空文本');
        const text = "";
        
        console.log('输入文本: [空]');
        const result = await translator.processTranslation(text);
        console.log('翻译结果:', JSON.stringify(result, null, 2));
        console.log('测试用例4完成\n');
    } catch (error) {
        console.error('测试用例4失败:', error);
    }
}

// 运行测试
testTranslator().then(() => {
    console.log('所有测试完成');
}).catch(error => {
    console.error('测试过程中出错:', error);
});