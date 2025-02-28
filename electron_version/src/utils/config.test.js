const config = require('./config');

function testConfig() {
    console.log('开始测试配置功能...\n');

    // 测试获取配置
    console.log('测试用例1: 获取配置');
    console.log('完整配置:', config.getAll());
    console.log('AI设置:', config.get('useAI'));
    console.log('窗口设置:', config.get('windowSettings.main'));
    console.log('\n');

    // 测试修改配置
    console.log('测试用例2: 修改配置');
    config.set('translation.targetLang', 'en');
    console.log('修改后的翻译目标语言:', config.get('translation.targetLang'));
    console.log('\n');

    // 测试新增配置项
    console.log('测试用例3: 新增配置项');
    config.set('newSetting.test', 'value');
    console.log('新增的配置项:', config.get('newSetting.test'));
    console.log('\n');

    // 测试重置配置
    console.log('测试用例4: 重置配置');
    config.reset();
    console.log('重置后的配置:', config.getAll());
}

// 运行测试
testConfig();