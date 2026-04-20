# 🩺 血压 + 血尿酸健康管理 Web 服务

轻量级健康数据管理系统，支持血压和血尿酸数据的录入、查询和趋势可视化。

## ✨ 功能特性

- 🔐 **密码登录**：简单安全的登录保护
- 📝 **数据录入**：血压（收缩压、舒张压、心率）、血尿酸数据录入
- 📋 **历史记录**：按时间段筛选查询历史数据
- 📈 **趋势图表**：使用 ECharts 展示数据变化趋势
- 📱 **响应式设计**：完美适配手机、平板、电脑
- 💾 **SQLite 数据库**：无需额外配置，开箱即用

## 🛠️ 技术栈

- **后端**：Python 3 + Flask
- **前端**：HTML + CSS + JavaScript + ECharts
- **数据库**：SQLite
- **部署**：兼容阿里云 ECS、轻量应用服务器

## 🚀 快速开始

### 本地运行

1. **克隆或下载项目**
```bash
cd blood
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行项目**
```bash
python app.py
```

4. **访问应用**
打开浏览器访问：http://localhost:5000

默认登录密码：`123456`

## 📁 项目结构

```
blood/
├── app.py              # Flask 主程序
├── requirements.txt    # Python 依赖包
├── README.md          # 项目说明
├── DEPLOY.md          # 阿里云部署指南
├── templates/          # 模板目录
│   ├── index.html     # 主页面（数据录入、历史、图表）
│   └── login.html     # 登录页面
├── static/            # 静态资源目录
└── health_data.db     # SQLite 数据库（运行后自动生成）
```

## 🎯 使用说明

### 数据录入
1. 选择录入类型（血压/血尿酸）
2. 填写相关数据和测量时间
3. 点击提交按钮

### 历史记录
1. 切换到「历史记录」标签页
2. 选择数据类型和时间范围
3. 查看详细记录或删除错误数据

### 趋势图表
1. 切换到「趋势图表」标签页
2. 选择数据类型和时间周期
3. 查看数据变化趋势图

## 🔧 配置修改

### 修改登录密码
编辑 [app.py](file:///Users/rongzeng/work/solo/blood/app.py#L55)：
```python
if password == 'your-new-password':  # 修改此处
```

### 修改 Secret Key
编辑 [app.py](file:///Users/rongzeng/work/solo/blood/app.py#L7)：
```python
app.secret_key = 'your-new-secret-key'  # 修改此处
```

## 🌐 部署到阿里云

详细的部署步骤请参考 [DEPLOY.md](file:///Users/rongzeng/work/solo/blood/DEPLOY.md)。

快速部署步骤：
1. 购买阿里云服务器（CentOS 7）
2. 安装 Python 3 和依赖
3. 上传项目文件
4. 使用 Gunicorn + Nginx 部署
5. 配置 Systemd 开机自启

## 📝 注意事项

- 首次运行会自动创建 SQLite 数据库文件
- 建议定期备份 `health_data.db` 数据库文件
- 生产环境请务必修改默认密码和 Secret Key
- 建议使用 HTTPS 协议（可使用 Let's Encrypt 免费证书）

## 🤝 许可证

MIT License

---

**祝您健康！** 💪
