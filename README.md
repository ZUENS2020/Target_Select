# Target_Select

自动化漏洞挖掘目标选择工具 - 自动从GitHub获取可能存在漏洞的项目

## 功能特性

- 🔍 自动搜索GitHub上可能存在漏洞的项目
- ⭐ 筛选star数大于500的热门项目
- 🎯 多种搜索策略：安全问题、CVE、过时依赖等
- 📊 支持按编程语言过滤
- 💾 结果导出为JSON格式
- 🔐 支持GitHub Token以提高API限制

## 安装

### 环境要求

- Python 3.7+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 快速启动（推荐）

使用交互式启动脚本：

```bash
./quick_start.sh
```

或者：

```bash
bash quick_start.sh
```

### 基本使用

```bash
python target_select.py
```

### 使用GitHub Token（推荐）

为了避免API限制，建议设置GitHub Token：

```bash
export GITHUB_TOKEN=your_github_token
python target_select.py
```

### 获取GitHub Token

1. 访问 GitHub Settings > Developer settings > Personal access tokens
2. 生成新的token
3. 不需要特殊权限，仅用于提高API限制

## 输出说明

程序将输出以下信息：

- 项目名称和完整路径
- Star数和Fork数
- 编程语言
- 项目描述
- GitHub URL
- 最后更新时间
- 开放的Issues数量

结果将自动保存到 `vulnerable_targets.json` 文件中。

## 配置文件

可以通过修改 `config.json` 自定义搜索参数：

```json
{
  "github_token": "",
  "min_stars": 500,
  "max_results": 50,
  "search_keywords": [
    "security vulnerability",
    "CVE",
    "security issue",
    "outdated dependencies"
  ],
  "languages": [
    "Python",
    "JavaScript",
    "Java",
    "Go",
    "PHP",
    "Ruby",
    "C",
    "C++"
  ]
}
```

## 搜索策略

工具使用以下策略来识别可能存在漏洞的项目：

1. **安全关键词搜索**：搜索包含"security vulnerability"、"CVE"等关键词的项目
2. **过时依赖**：查找提到过时依赖的项目
3. **安全问题**：搜索有安全相关issues的项目
4. **Star数过滤**：只返回star数大于指定值的流行项目

## 示例输出

```
╔═══════════════════════════════════════════════════════════════╗
║          Target Select - 自动化漏洞挖掘目标选择工具              ║
║                                                               ║
║  自动从GitHub获取可能存在漏洞的项目 (stars > 500)               ║
╚═══════════════════════════════════════════════════════════════╝

🔍 正在搜索潜在的漏洞项目...
   搜索条件: stars > 500, 包含安全相关关键词

================================================================================
找到 50 个潜在目标项目
================================================================================

[1] owner/repository
    ⭐ Stars: 5000 | 🍴 Forks: 1000
    💻 Language: Python
    📝 Description: A vulnerable web application for testing
    🔗 URL: https://github.com/owner/repository
    📅 Last Updated: 2024-01-01T00:00:00Z
    🐛 Open Issues: 25

...
```

## 注意事项

- 此工具仅用于安全研究和教育目的
- 请遵守GitHub API使用条款
- 请遵守相关法律法规，不要进行未经授权的渗透测试
- 建议使用GitHub Token以避免API限制

## 许可证

MIT License

## 贡献

欢迎提交Issues和Pull Requests！