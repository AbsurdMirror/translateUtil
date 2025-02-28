const fs = require('fs');
const path = require('path');

class Config {
    constructor() {
        this.configPath = path.join(__dirname, '../../setting.json');
        this.config = this.loadConfig();
    }

    // 加载配置文件
    loadConfig() {
        try {
            if (fs.existsSync(this.configPath)) {
                const data = fs.readFileSync(this.configPath, 'utf8');
                return JSON.parse(data);
            } else {
                // 默认配置
                const defaultConfig = {
                    useAI: true,
                    aiProvider: "deepseek",
                    windowSettings: {
                        main: {
                            width: 800,
                            height: 600
                        },
                        translation: {
                            width: 400,
                            height: 600
                        },
                        input: {
                            width: 400,
                            height: 300
                        }
                    },
                    shortcuts: {
                        translate: "CommandOrControl+O",
                        input: "CommandOrControl+X"
                    },
                    translation: {
                        targetLang: "zh",
                        sourceLang: "auto"
                    }
                };
                this.saveConfig(defaultConfig);
                return defaultConfig;
            }
        } catch (error) {
            console.error('加载配置文件失败:', error);
            return null;
        }
    }

    // 保存配置
    saveConfig(newConfig = null) {
        try {
            const configToSave = newConfig || this.config;
            fs.writeFileSync(this.configPath, JSON.stringify(configToSave, null, 4));
            this.config = configToSave;
            return true;
        } catch (error) {
            console.error('保存配置文件失败:', error);
            return false;
        }
    }

    // 获取配置项
    get(key) {
        if (!this.config) {
            return null;
        }

        const keys = key.split('.');
        let value = this.config;
        
        for (const k of keys) {
            if (value === null || value === undefined) {
                return null;
            }
            value = value[k];
        }
        
        return value;
    }

    // 设置配置项
    set(key, value) {
        if (!this.config) {
            this.config = {};
        }

        const keys = key.split('.');
        let current = this.config;
        
        for (let i = 0; i < keys.length - 1; i++) {
            const k = keys[i];
            if (!(k in current)) {
                current[k] = {};
            }
            current = current[k];
        }
        
        current[keys[keys.length - 1]] = value;
        return this.saveConfig();
    }

    // 重置配置
    reset() {
        if (fs.existsSync(this.configPath)) {
            fs.unlinkSync(this.configPath);
        }
        this.config = this.loadConfig();
        return true;
    }

    // 获取所有配置
    getAll() {
        return this.config;
    }
}

module.exports = new Config();