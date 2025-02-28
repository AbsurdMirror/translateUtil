const Translator = require('./core/translator');
const config = require('./utils/config');
const sentenceProcessor = require('./utils/sentence');
const readline = require('readline');

// 创建翻译器实例
const translator = new Translator({
    aiProvider: config.get('aiProvider'),
    aiKey: config.get('aiKey'),
    useAI: config.get('useAI'),
    translationToken: config.get('translationToken'),
});

class TranslatorCLI {
    constructor() {
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    // 显示主菜单
    showMenu() {
        console.log('\n=== 翻译工具命令行版 ===');
        console.log('1. 输入文本翻译');
        console.log('2. 查看当前配置');
        console.log('3. 修改配置');
        console.log('4. 退出');
        console.log('=====================\n');

        this.rl.question('请选择操作 (1-4): ', (answer) => {
            switch (answer.trim()) {
                case '1':
                    this.translateText();
                    break;
                case '2':
                    this.showConfig();
                    break;
                case '3':
                    this.modifyConfig();
                    break;
                case '4':
                    this.exit();
                    break;
                default:
                    console.log('无效的选择，请重试');
                    this.showMenu();
            }
        });
    }

    // 翻译文本
    async translateText() {
        this.rl.question('\n请输入要翻译的文本 (输入 "q" 返回主菜单):\n', async (text) => {
            if (text.toLowerCase() === 'q') {
                this.showMenu();
                return;
            }

            try {
                // 使用 sentence 处理文本
                const processedResult = sentenceProcessor.process(text);
                if (!processedResult.success) {
                    throw new Error(processedResult.error);
                }

                // 翻译处理后的文本
                const translationResult = await translator.processTranslation(text);
                if (!translationResult.success) {
                    throw new Error(translationResult.message);
                }

                // 显示结果
                console.log('\n=== 翻译结果 ===');
                translationResult.data.forEach((item, index) => {
                    console.log(`\n原文 ${index + 1}: ${item.source}`);
                    console.log(`译文 ${index + 1}: ${item.target}`);
                });
                console.log('\n================\n');

            } catch (error) {
                console.error('翻译出错:', error.message);
            }

            this.showMenu();
        });
    }

    // 显示当前配置
    showConfig() {
        console.log('\n=== 当前配置 ===');
        console.log(JSON.stringify(config.getAll(), null, 2));
        console.log('===============\n');
        this.showMenu();
    }

    // 修改配置
    modifyConfig() {
        console.log('\n=== 修改配置 ===');
        console.log('1. 修改目标语言');
        console.log('2. 修改AI设置');
        console.log('3. 返回主菜单');

        this.rl.question('请选择要修改的选项 (1-3): ', (answer) => {
            switch (answer.trim()) {
                case '1':
                    this.rl.question('请输入目标语言 (zh/en): ', (lang) => {
                        config.set('translation.targetLang', lang);
                        console.log('设置已更新');
                        this.showMenu();
                    });
                    break;
                case '2':
                    this.rl.question('是否启用AI (true/false): ', (useAI) => {
                        config.set('useAI', useAI === 'true');
                        console.log('设置已更新');
                        this.showMenu();
                    });
                    break;
                case '3':
                    this.showMenu();
                    break;
                default:
                    console.log('无效的选择，请重试');
                    this.modifyConfig();
            }
        });
    }

    // 退出程序
    exit() {
        console.log('\n感谢使用，再见！');
        this.rl.close();
        process.exit(0);
    }

    // 启动CLI
    start() {
        console.log('正在初始化翻译工具...');
        this.showMenu();
    }
}

// 启动CLI
const cli = new TranslatorCLI();
cli.start();