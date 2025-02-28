const crypto = require('crypto');

class Crypto {
    constructor() {
        // 使用固定的加密密钥（实际应用中应该更安全地存储）
        this.key = crypto.scryptSync('your-password', 'salt', 32);
        this.algorithm = 'aes-256-cbc';
    }

    encrypt(text) {
        try {
            const iv = crypto.randomBytes(16);
            const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);
            let encrypted = cipher.update(text, 'utf8', 'hex');
            encrypted += cipher.final('hex');
            return iv.toString('hex') + ':' + encrypted;
        } catch (error) {
            console.error('加密失败:', error);
            return null;
        }
    }

    decrypt(text) {
        try {
            const [ivHex, encryptedHex] = text.split(':');
            const iv = Buffer.from(ivHex, 'hex');
            const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
            let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
            decrypted += decipher.final('utf8');
            return decrypted;
        } catch (error) {
            console.error('解密失败:', error);
            return null;
        }
    }
}

module.exports = new Crypto();