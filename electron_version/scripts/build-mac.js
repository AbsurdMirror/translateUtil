const builder = require('electron-builder');
const path = require('path');

process.env.CSC_IDENTITY_AUTO_DISCOVERY = false;

// 设置缓存路径
process.env.ELECTRON_BUILDER_CACHE = path.join(__dirname, '../electron-builder-cache');

// Mac 构建配置
const buildConfig = {
    appId: 'com.translator.app',
    productName: '文本翻译工具',
    mac: {
        category: 'public.app-category.utilities',
        target: ['dmg', 'zip'],
        icon: 'build/icon.icns',
        darkModeSupport: true
    },
    dmg: {
        title: '文本翻译工具',
        icon: 'build/icon.icns',
        contents: [
            { x: 130, y: 220 },
            { x: 410, y: 220, type: 'link', path: '/Applications' }
        ]
    },
    files: [
        "src/**/*",
        "package.json"
    ],
    directories: {
        output: "dist-mac"
    },
    // 移除了不支持的配置项
    artifactBuildStarted: (handler) => {
        if (handler.httpExecutor) {
            handler.httpExecutor.maxAttempts = 5;
            handler.httpExecutor.retryDelay = 3000;
        }
    }
};

// 执行构建
async function buildMac() {
    try {
        console.log('开始构建 Mac 版本...');
        await builder.build({
            targets: builder.Platform.MAC.createTarget(),
            config: buildConfig
        });
        console.log('Mac 版本构建成功');
    } catch (error) {
        console.error('构建失败:', error);
        process.exit(1);
    }
}

buildMac();