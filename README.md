# 广州理工学院查寝脚本

## 免责声明

本项目基于 [CMJNB/bed_check](https://github.com/CMJNB/bed_check) 修改而来，仅用于个人学习交流。

原仓库作者未提供明确的开源许可证。如果原作者认为本仓库侵犯了其权益，请联系我删除。

## 修改内容

基于原仓库的改进：
- 首次运行自动配置账号密码
- 添加 `login.ini` 配置文件支持
- 优化依赖安装说明（使用清华镜像源）
- 新增详细的依赖安装教程
- 清理隐私信息，添加 `.gitignore` 文件
- 更新和完善文档说明

---

## 介绍

这是一个用于[广州理工学院查寝](https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do)的自动化脚本，可以自动完成查寝任务，支持验证码识别、密码加密、定时执行等功能。

## 功能特点

- ✅ **自动验证码识别**：使用 ddddocr 进行验证码识别和计算
- ✅ **密码加密**：使用 Node.js + RSA 加密密码
- ✅ **多种配置方式**：支持配置文件、命令行参数
- ✅ **定时任务**：支持 Windows 定时任务和 GitHub Actions
- ✅ **错误处理**：完善的错误处理和重试机制
- ✅ **日志记录**：详细的日志输出，便于问题排查

## 环境要求

- Python 3.13+
- Node.js v24.13.0+ （用于密码加密）
- Windows 10+

## 快速开始

### 1. 安装依赖

打开命令行，执行以下命令：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

详细安装教程请查看 [依赖安装教程.txt](./依赖安装教程.txt)

⚠️ **重要**：numpy 必须小于 2.0 版本，否则会导致验证码识别失败。

### 2. 配置账号密码

**首次运行自动配置**

首次运行时，程序会提示你输入学号和密码，并自动保存到 `login.ini` 文件：

```bash
python main.py
```

按提示输入账号密码后，下次运行将自动读取，无需重复输入。

**手动配置**

你也可以手动编辑 `login.ini` 文件：

```ini
[loginInfo]
LOGIN_USERNAME = 你的学号
LOGIN_PASSWORD = 你的密码
[setting]
```

> ⚠️ **注意**：`login.ini` 已在 `.gitignore` 中，不会被提交到 Git 仓库，你的账号密码安全。

### 3. 运行查寝

双击运行 `启动查寝.bat` 文件，或在命令行中执行：

```bash
python main.py
```

### 4. 设置定时任务

右键点击 `设置定时任务.bat`，选择"以管理员身份运行"，即可设置每天自动查寝。

## 使用方法

### 参数说明

```bash
python main.py [选项]
```

- `-e, --env`：从环境变量中获取用户名和密码
- `-c, --config`：读取配置文件获取用户名和密码
- `-u, --username`：命令行输入用户名
- `-p, --password`：命令行输入密码

优先级：`-e` > `-c` > `-u`

### 批处理文件

- **启动查寝.bat**：手动启动查寝程序
- **设置定时任务.bat**：设置 Windows 定时任务（需要管理员权限）
- **删除定时任务.bat**：删除已设置的定时任务

## 使用 GitHub Actions 自动查寝

### 1. Fork 仓库

点击右上角的 Fork 按钮将仓库 fork 到你的账号下。

### 2. 配置 Secrets

在仓库的 `Settings -> Secrets and variables -> Actions` 中添加：

- `LOGIN_USERNAME`：你的学号
- `LOGIN_PASSWORD`：你的密码
- `SETTING_STRING`：JSON 格式的配置文件（可选）

SETTING_STRING 示例：
```json
{
  "SPIDER_MAX_RETRY_TIMES": 3,
  "WECHAT_WARNING_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx",
  "WECHAT_WARNING_PHONE": ["135xxxxx", "189xxxxx"],
  "LOG_LEVEL": "INFO"
}
```

更多配置项请参考 [setting.py](./setting.py)。

### 3. 修改定时时间

编辑 `.github/workflows/定时自动查寝.yml` 文件：

```yaml
schedule:
  - cron: '00 14 * * *'  # UTC时间，对应北京时间22:00
```

### 4. 推送代码

推送到 GitHub 后，Actions 会自动按照设定的时间运行。

## 文件说明

| 文件名 | 说明 |
|--------|------|
| main.py | 主程序文件 |
| login.js | RSA 密码加密脚本 |
| login.ini | 用户配置文件 |
| pillow_compat.py | Pillow 兼容性补丁 |
| env.py | 环境变量处理 |
| setting.py | 全局配置 |
| requirements.txt | Python 依赖包 |
| 启动查寝.bat | 启动脚本 |
| 设置定时任务.bat | 定时任务设置 |
| 删除定时任务.bat | 定时任务删除 |
| tools/ | 工具模块目录 |
| .github/ | GitHub Actions 配置 |
| .gitignore | Git 忽略文件配置 |

## 常见问题

### Q: 验证码识别失败？

A: 最常见原因是 `numpy` 版本不兼容。请确保安装正确版本的 `numpy`（必须小于 2.0.0）：

```bash
pip uninstall numpy -y
pip install "numpy<2.0.0"
pip install ddddocr
```

**原因**：`ddddocr` 依赖旧版本的 `numpy`，numpy 2.0+ 有不兼容的 API 变更。

### Q: 密码加密失败？

A: 确保已安装 Node.js：

```bash
node --version
```

如果没有安装，请访问 https://nodejs.org/ 下载安装。

### Q: 今天不需要考勤登记？

A: 这表示查寝程序运行正常，只是当前时间不在查寝时段，或者今天没有安排查寝。

### Q: 如何修改查寝时间？

A: 编辑 `设置定时任务.bat` 文件中的 `/st 22:00` 为你想要的时间。

### Q: 定时任务设置失败？

A: 需要以管理员身份运行 `设置定时任务.bat`，右键选择"以管理员身份运行"。

## 技术实现

- **爬虫框架**：feapder
- **验证码识别**：ddddocr
- **密码加密**：Node.js + RSA
- **图片处理**：Pillow
- **自动执行**：Windows 任务计划程序 / GitHub Actions

## 注意事项

> ⚠️ **警告**：
>
> 1. 请妥善保管你的账号密码
> 2. 不要在公共场合使用本脚本
> 3. 建议在查寝时间段内运行程序
> 4. 定时任务需要管理员权限
> 5. `login.ini` 包含敏感信息，已在 `.gitignore` 中排除，不会上传到 GitHub
> 6. Fork 到你的仓库后，首次运行需要配置账号密码
> 7. **必须严格按照 `requirements.txt` 安装依赖，特别是 `numpy<2.0.0`**

## 许可证

MIT License

## 免责声明

本脚本仅供学习交流使用，使用者需自行承担使用风险。请遵守学校相关规定，合理使用。
