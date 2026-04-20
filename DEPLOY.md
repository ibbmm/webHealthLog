# 血压 + 血尿酸健康管理 Web 服务 - 阿里云部署指南

## 项目介绍
轻量级健康数据管理 Web 服务，支持血压和血尿酸数据录入、查询、趋势图表展示。

## 技术栈
- 后端：Python 3 + Flask
- 前端：HTML + CSS + JavaScript + ECharts
- 数据库：SQLite
- 部署：阿里云 ECS/轻量应用服务器

## 项目结构
```
blood/
├── app.py              # Flask 主程序
├── requirements.txt    # Python 依赖
├── DEPLOY.md          # 部署文档
├── templates/          # 模板目录
│   ├── index.html     # 主页面
│   └── login.html     # 登录页面
├── static/            # 静态资源目录
└── health_data.db     # SQLite 数据库（运行后自动生成）
```

## 一、阿里云服务器准备

### 1. 购买服务器
- 推荐：阿里云轻量应用服务器（CentOS 7）
- 配置：1核2G 起步
- 系统镜像：CentOS 7.9

### 2. 开放端口
在阿里云控制台安全组中开放 **5000** 端口（或自定义端口）

## 二、服务器环境配置

### 1. SSH 连接服务器
```bash
ssh root@your-server-ip
```

### 2. 安装 Python 3
```bash
# 安装依赖
yum install -y python3 python3-pip git

# 验证安装
python3 --version
pip3 --version
```

## 三、部署项目

### 1. 上传项目文件
方式一：使用 scp 上传（在本地终端执行）
```bash
scp -r /path/to/blood/* root@your-server-ip:/root/blood/
```

方式二：在服务器上克隆代码（如果使用 git）
```bash
cd /root
git clone <your-repo-url> blood
cd blood
```

### 2. 安装 Python 依赖
```bash
cd /root/blood
pip3 install -r requirements.txt
```

### 3. 测试运行
```bash
python3 app.py
```
访问：http://your-server-ip:5000 测试是否正常

默认登录密码：`123456`

## 四、使用 Gunicorn + Nginx 生产部署（推荐）

### 1. 安装 Gunicorn
```bash
pip3 install gunicorn
```

### 2. 使用 Gunicorn 启动服务
```bash
cd /root/blood
gunicorn -w 4 -b 0.0.0.0:5000 app:app --daemon
```

参数说明：
- `-w 4`：启动 4 个 worker 进程
- `-b 0.0.0.0:5000`：监听所有 IP 的 5000 端口
- `--daemon`：后台运行

### 3. 安装 Nginx
```bash
yum install -y nginx
```

### 4. 配置 Nginx
编辑配置文件：
```bash
vi /etc/nginx/conf.d/health.conf
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或服务器IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 5. 启动 Nginx
```bash
# 测试配置
nginx -t

# 启动 Nginx
systemctl start nginx
systemctl enable nginx  # 开机自启
```

## 五、使用 Systemd 管理服务（可选）

### 1. 创建服务文件
```bash
vi /etc/systemd/system/health.service
```

添加以下内容：
```ini
[Unit]
Description=Health Data Management Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/blood
ExecStart=/usr/bin/python3 /usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. 启动服务
```bash
systemctl daemon-reload
systemctl start health
systemctl enable health  # 开机自启

# 查看状态
systemctl status health
```

## 六、安全配置

### 1. 修改默认密码
编辑 `app.py`，找到并修改：
```python
if password == '123456':  # 修改为你的密码
```

### 2. 修改 Secret Key
编辑 `app.py`，修改：
```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

### 3. 配置防火墙（可选）
```bash
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

## 七、数据备份

### 1. 定期备份数据库
```bash
# 创建备份脚本
vi /root/backup.sh
```

添加内容：
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /root/blood/health_data.db /root/backups/health_data_$DATE.db
find /root/backups/ -name "health_data_*.db" -mtime +30 -delete
```

### 2. 设置定时任务
```bash
mkdir -p /root/backups
chmod +x /root/backup.sh
crontab -e
```

添加：
```
0 2 * * * /root/backup.sh  # 每天凌晨2点备份
```

## 八、常见问题

### 1. 端口被占用
```bash
# 查看端口占用
netstat -tlnp | grep 5000

# 杀死进程
kill -9 <pid>
```

### 2. 权限问题
```bash
chmod -R 755 /root/blood
```

### 3. 查看日志
```bash
# Gunicorn 日志
journalctl -u health -f

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 九、一键启动（开发测试用）

创建启动脚本：
```bash
vi /root/blood/start.sh
```

添加：
```bash
#!/bin/bash
cd /root/blood
pip3 install -r requirements.txt
python3 app.py
```

运行：
```bash
chmod +x /root/blood/start.sh
/root/blood/start.sh
```

---

**部署完成！** 访问 http://your-server-ip 即可使用。
