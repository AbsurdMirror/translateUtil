const { app } = require('electron');
const path = require('path');
const fs = require('fs');

class Config {
    constructor() {
        // 使用用户数据目录
        this.userDataPath = app.getPath('userData');
        this.configPath = path.join(this.userDataPath, 'settings.json');
        
        // 确保配置目录存在
        if (!fs.existsSync(this.userDataPath)) {
            fs.mkdirSync(this.userDataPath, { recursive: true });
        }
        
        // 如果配置文件不存在，创建默认配置
        if (!fs.existsSync(this.configPath)) {
            this.config = this.getDefaultConfig();
            this.save();
        } else {
            this.load();
        }
    }

    getDefaultConfig() {
        return {
            translationToken: "",
            useAI: false,
            aiProvider: "zhipu",
            aiKey: "",
            windowSettings: {
                main: { width: 800, height: 600 },
                translation: { width: 400, height: 600 },
                input: { width: 400, height: 300 }
            },
            shortcuts: {
                translate: "CommandOrControl+O",
                input: "CommandOrControl+X"
            },
            translation: {
                targetLang: "zh"
            }
        };
    }

    load() {
        try {
            const data = fs.readFileSync(this.configPath, 'utf8');
            this.config = JSON.parse(data);
        } catch (error) {
            console.error('加载配置失败:', error);
            this.config = this.getDefaultConfig();
        }
    }

    save() {
        try {
            fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 4));
        } catch (error) {
            console.error('保存配置失败:', error);
        }
    }

    get(key) {
        return key ? this.config[key] : this.config;
    }

    set(key, value) {
        this.config[key] = value;
        this.save();
        return true;
    }

    getAll() {
        return this.config;
    }
}

module.exports = new Config();