const sentenceProcessor = require('./sentence');

function testSentenceProcessor() {
    console.log('开始测试句子处理功能...\n');

    // 测试用例1：混合语言文本
    console.log('测试用例1: 混合语言文本');
    const text1 = "This is an English sentence. 这是一个中文句子。 This is mixed 中英文 sentence.";
    const result1 = sentenceProcessor.process(text1);
    console.log('处理结果:', result1);
    console.log('\n');

    // 测试用例2：包含特殊字符的文本
    console.log('测试用例2: 特殊字符文本');
    const text2 = "Hello... World! \"测试\" 'Test' —— 破折号";
    const result2 = sentenceProcessor.process(text2);
    console.log('处理结果:', result2);
    console.log('\n');

    // 测试用例3：短句合并
    console.log('测试用例3: 短句合并');
    const text3 = "Hi. OK. Good. This is a longer sentence.";
    const result3 = sentenceProcessor.process(text3, { minLength: 15 });
    console.log('处理结果:', result3);
    console.log('\n');

    // 测试用例4：多行文本
    console.log('测试用例4: 多行文本');
    const text4 = "First line.\n\n\nSecond line.\nThird line.";
    const result4 = sentenceProcessor.process(text4);
    console.log('处理结果:', result4);
}

// 运行测试
testSentenceProcessor();