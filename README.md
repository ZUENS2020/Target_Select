# Target_Select

自动化漏洞挖掘目标选择工具 - 自动从GitHub获取可能存在漏洞的项目

## 功能特性

- 🔍 自动搜索GitHub上可能存在漏洞的项目
- ⭐ 筛选star数大于500的热门项目
- 🎯 多种搜索策略：安全问题、CVE、过时依赖等
- 📊 支持按编程语言过滤
- 💾 结果导出为JSON格式
- 🔐 支持GitHub Token以提高API限制
- 🆕 **直接获取最近2个月内流行项目（不使用搜索API）**
- 🆕 **自动检测过时依赖（Dependabot、依赖文件分析）**
- 🆕 **CodeQL 分析准备和配置生成**

## 安装

### 环境要求

- Python 3.7+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 快速启动（推荐）🆕

**直接运行过时依赖检测**

```bash
# 设置GitHub Token（重要！）
export GITHUB_TOKEN=your_token

# 运行过时依赖检测
python target_select_outdated.py
```

这将自动：
- 获取最近2个月内star > 500的项目
- 检测过时依赖和Dependabot警报
- 生成CodeQL分析配置
- 输出结果到 `outdated_dependencies_targets.json`

### 使用交互式启动脚本（可选）

如果需要使用交互式菜单：

```bash
./quick_start.sh
```

或者：

```bash
bash quick_start.sh
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

## 核心功能：过时依赖检测 🆕

**主要特性 (target_select_outdated.py)**

1. **直接获取**：不使用搜索API，直接列出所有公开仓库
2. **时间过滤**：只保留最近2个月内更新的项目
3. **流行度过滤**：只保留star > 500的项目
4. **依赖检测**：
   - 检查是否启用 Dependabot 安全警报
   - 检测常见依赖文件（package.json, requirements.txt, pom.xml等）
5. **CodeQL准备**：为支持的语言生成CodeQL分析配置

### 其他工具（可选）

如需使用关键词搜索策略，也提供了以下工具：

- **target_select.py**：基础搜索版本
- **target_select_advanced.py**：高级搜索版本

这些工具使用搜索API查找包含"security vulnerability"、"CVE"等关键词的项目。

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

## 新功能详解：过时依赖检测 🆕

### target_select_outdated.py - 专门用于检测过时依赖

这是一个全新的工具模块，专门设计用于：

1. **直接获取项目**（不使用搜索API）
   - 使用 `/repositories` API直接列出公开仓库
   - 避免搜索API的速率限制和结果不完整问题

2. **精确的时间和流行度过滤**
   - 只获取最近2个月（60天）内更新的项目
   - 只保留 star > 500 的流行项目

3. **智能依赖检测**
   - 检查 Dependabot 安全警报状态
   - 识别常见依赖管理文件（package.json, requirements.txt等）
   - 支持9种主流编程语言的依赖文件

4. **CodeQL 分析准备**
   - 自动识别支持CodeQL的语言（Python, Java, JavaScript等）
   - 生成可直接使用的GitHub Actions工作流配置
   - 为安全分析提供即用型配置文件

### 使用示例

```bash
# 基本使用
python target_select_outdated.py

# 使用GitHub Token（强烈推荐）
export GITHUB_TOKEN=your_token
python target_select_outdated.py
```

### 输出示例

```
找到 15 个可能有过时依赖的项目

[1] owner/repository
    ⭐ Stars: 1234 | 🍴 Forks: 567
    💻 Language: Python
    ⚠️  可能有过时依赖:
       - 启用了 Dependabot 警报
       - 依赖文件: requirements.txt (Python)
    🔍 CodeQL: 支持 (python)
```

详细文档请查看 [OUTDATED_DEPS_GUIDE.md](OUTDATED_DEPS_GUIDE.md)

## 注意事项

- 此工具仅用于安全研究和教育目的
- 请遵守GitHub API使用条款
- 请遵守相关法律法规，不要进行未经授权的渗透测试
- 建议使用GitHub Token以避免API限制
- 新的过时依赖检测工具需要更多API调用，务必使用Token

## 许可证

MIT License

## 贡献

欢迎提交Issues和Pull Requests！