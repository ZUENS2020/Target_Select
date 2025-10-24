# Target_Select

自动化漏洞挖掘目标选择工具 - 自动从GitHub获取可能存在漏洞的项目

## 功能特性

- 🔍 直接获取最近2个月内流行项目（不使用搜索API）
- ⭐ 筛选star数大于500的热门项目
- 🔐 自动检测过时依赖（Dependabot、依赖文件分析）
- 📊 支持9种主流编程语言的依赖文件检测
- 💾 结果导出为JSON格式
- 🔧 CodeQL 分析准备和配置生成
- 🎯 支持GitHub Token以提高API限制

## 安装

### 环境要求

- Python 3.7+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 快速启动

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

### 使用GitHub Token（推荐）

为了避免API限制，建议设置GitHub Token：

```bash
export GITHUB_TOKEN=your_github_token
python target_select_outdated.py
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
- 过时依赖检测结果
- CodeQL支持状态

结果将自动保存到 `outdated_dependencies_targets.json` 文件中。

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

## 工作原理

1. **直接获取项目**：不使用搜索API，直接列出所有公开仓库
2. **时间过滤**：只保留最近2个月（60天）内更新的项目
3. **流行度过滤**：只保留 star > 500 的项目
4. **依赖检测**：
   - 检查是否启用 Dependabot 安全警报
   - 检测常见依赖文件（package.json, requirements.txt, pom.xml等）
5. **CodeQL准备**：为支持的语言生成CodeQL分析配置

### 支持的依赖文件类型

- JavaScript/Node.js: `package.json`
- Python: `requirements.txt`, `Pipfile`
- Java: `pom.xml`, `build.gradle`
- Ruby: `Gemfile`
- Go: `go.mod`
- PHP: `composer.json`
- Rust: `Cargo.toml`

## 示例输出

```
╔═══════════════════════════════════════════════════════════════╗
║     Target Select Outdated - 过时依赖项目检测工具              ║
║                                                               ║
║  直接获取最近2个月内 star > 500 的项目                         ║
║  检测过时依赖并准备 CodeQL 分析                                ║
╚═══════════════════════════════════════════════════════════════╝

🔍 正在获取最近 60 天内 star > 500 的项目...
   时间范围: 2024-08-24 至今

================================================================================
找到 15 个可能有过时依赖的项目
================================================================================

[1] owner/repository
    ⭐ Stars: 1234 | 🍴 Forks: 567
    💻 Language: Python
    📝 Description: A project with dependencies
    🔗 URL: https://github.com/owner/repository
    📅 Updated: 2024-10-20T10:30:00Z
    ⚠️  可能有过时依赖:
       - 启用了 Dependabot 警报
       - 依赖文件: requirements.txt (Python)
    🔍 CodeQL: 支持 (python)

...
```

## 详细文档

详细使用指南请查看 [OUTDATED_DEPS_GUIDE.md](OUTDATED_DEPS_GUIDE.md)

## 编程方式使用

```python
from target_select_outdated import OutdatedDependencyChecker

# 创建检测器
checker = OutdatedDependencyChecker(
    github_token="your_token",
    min_stars=500,
    days_back=60
)

# 获取项目
repos = checker.fetch_recent_popular_repos(max_repos=50)

# 检查依赖
for repo in repos:
    dep_check = checker.check_outdated_dependencies(repo)
    if dep_check['has_outdated']:
        print(f"✓ {repo['full_name']} 可能有过时依赖")

# 导出结果
checker.export_results(repos, "output.json")
```

## 注意事项

- 此工具仅用于安全研究和教育目的
- 请遵守GitHub API使用条款
- 请遵守相关法律法规，不要进行未经授权的渗透测试
- 建议使用GitHub Token以避免API限制
- 此工具需要较多API调用，务必使用Token

## 许可证

MIT License

## 贡献

欢迎提交Issues和Pull Requests！