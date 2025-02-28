const builder = require('electron-builder');
const path = require('path');

// 设置缓存路径为项目目录下的 cache 文件夹
process.env.ELECTRON_BUILDER_CACHE = path.join(__dirname, '../electron-builder-cache');

builder.build({
    config: {
        // ... 你的构建配置
    }
})
.then(() => console.log('构建成功'))
.catch((error) => console.error('构建失败:', error));