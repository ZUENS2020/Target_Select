# 过时依赖检测使用指南

## 概述

`target_select_outdated.py` 是一个专门用于检测过时依赖的工具。与其他版本不同，它**不使用搜索API**，而是直接获取最近2个月内star > 500的项目，然后检测这些项目的依赖状态。

## 主要特性

- ✅ **直接获取**：不使用GitHub搜索API，直接列出公开仓库
- ✅ **时间筛选**：只获取最近2个月（60天）内更新的项目
- ✅ **流行度筛选**：只保留star数 > 500的项目
- ✅ **依赖检测**：自动检测Dependabot警报和依赖文件
- ✅ **CodeQL准备**：为支持的项目生成CodeQL分析配置

## 快速开始

### 基本使用

```bash
python target_select_outdated.py
```

### 使用GitHub Token（强烈推荐）

```bash
export GITHUB_TOKEN=your_personal_access_token
python target_select_outdated.py
```

## 工作原理

### 1. 获取项目阶段

工具使用GitHub的 `/repositories` API端点直接列出所有公开仓库，然后：

- 获取每个仓库的详细信息
- 过滤出star > 500的仓库
- 过滤出最近60天内更新的仓库

**注意**：这种方法比搜索API更可靠，但需要更多API调用。

### 2. 依赖检测阶段

对每个符合条件的项目，工具会：

#### a. 检查Dependabot警报

通过API检查项目是否启用了Dependabot安全警报：

```
GET /repos/{owner}/{repo}/vulnerability-alerts
```

如果返回204，说明启用了安全警报（可能存在已知漏洞）。

#### b. 检测依赖文件

检查项目是否包含常见的依赖管理文件：

| 文件名 | 生态系统 |
|--------|---------|
| package.json | JavaScript/Node.js |
| requirements.txt | Python |
| Pipfile | Python |
| pom.xml | Java/Maven |
| build.gradle | Java/Gradle |
| Gemfile | Ruby |
| go.mod | Go |
| composer.json | PHP |
| Cargo.toml | Rust |

如果找到这些文件，工具会标记项目可能有过时依赖。

### 3. CodeQL准备阶段

对于CodeQL支持的语言（Python, JavaScript, Java, C/C++, C#, Go, Ruby），工具会：

- 检查项目语言是否被CodeQL支持
- 生成GitHub Actions工作流配置文件
- 保存配置到 `/tmp/codeql_analysis/` 目录

生成的工作流文件可以直接用于GitHub Actions进行自动化安全分析。

## 输出说明

### 终端输出

```
╔═══════════════════════════════════════════════════════════════╗
║     Target Select Outdated - 过时依赖项目检测工具              ║
║                                                               ║
║  直接获取最近2个月内 star > 500 的项目                         ║
║  检测过时依赖并准备 CodeQL 分析                                ║
╚═══════════════════════════════════════════════════════════════╝

🔍 正在获取最近 60 天内 star > 500 的项目...
   时间范围: 2024-08-24 至今

  ✓ 找到: owner/repo1 (1234 stars, 更新于 2024-10-20T10:30:00Z)
  ✓ 找到: owner/repo2 (5678 stars, 更新于 2024-10-21T14:20:00Z)
  ...

找到 25 个符合条件的仓库

🔍 正在检查过时依赖...

[1/25] 检查 owner/repo1... ✓ 可能有过时依赖
[2/25] 检查 owner/repo2... - 未检测到明显的依赖问题
...

================================================================================
找到 15 个可能有过时依赖的项目
================================================================================

[1] owner/repo1
    ⭐ Stars: 1234 | 🍴 Forks: 567
    💻 Language: Python
    📝 Description: A sample project with dependencies
    🔗 URL: https://github.com/owner/repo1
    📅 Updated: 2024-10-20T10:30:00Z
    ⚠️  可能有过时依赖:
       - 启用了 Dependabot 警报
       - 依赖文件: requirements.txt (Python), package.json (JavaScript/Node.js)
    🔍 CodeQL: 支持 (python)
...

📄 结果已保存到: outdated_dependencies_targets.json

✅ 完成! 共找到 15 个可能有过时依赖的项目
🔍 其中 12 个项目支持 CodeQL 分析
```

### JSON输出文件

结果保存在 `outdated_dependencies_targets.json`：

```json
{
  "generated_at": "2024-10-23T08:00:00.000000",
  "total_projects": 15,
  "min_stars": 500,
  "days_back": 60,
  "cutoff_date": "2024-08-24T08:00:00.000000",
  "projects": [
    {
      "name": "repo1",
      "full_name": "owner/repo1",
      "description": "项目描述",
      "url": "https://github.com/owner/repo1",
      "clone_url": "https://github.com/owner/repo1.git",
      "stars": 1234,
      "forks": 567,
      "language": "Python",
      "updated_at": "2024-10-20T10:30:00Z",
      "created_at": "2023-01-01T00:00:00Z",
      "has_issues": true,
      "open_issues": 15,
      "topics": ["security", "web"],
      "default_branch": "main",
      "dependency_check": {
        "has_outdated": true,
        "dependabot_alerts": true,
        "dependency_files": [
          "requirements.txt (Python)",
          "package.json (JavaScript/Node.js)"
        ],
        "checked_at": "2024-10-23T08:00:00.000000"
      },
      "codeql_prep": {
        "supported": true,
        "language": "python",
        "codeql_language": "python",
        "config_file": "/tmp/codeql_analysis/repo1_codeql.yml",
        "clone_url": "https://github.com/owner/repo1.git",
        "instructions": "可以使用 CodeQL 分析此项目。配置文件已生成: /tmp/codeql_analysis/repo1_codeql.yml"
      }
    }
  ]
}
```

## CodeQL配置文件

对于支持CodeQL的项目，工具会生成GitHub Actions工作流配置文件。示例：

```yaml
name: CodeQL Analysis for owner/repo1

on:
  workflow_dispatch:

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    
    permissions:
      actions: read
      contents: read
      security-events: write
    
    strategy:
      fail-fast: false
      matrix:
        language: [ 'python' ]
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      with:
        repository: owner/repo1
    
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}
    
    - name: Autobuild
      uses: github/codeql-action/autobuild@v2
    
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
```

### 使用CodeQL配置

1. 找到生成的配置文件（在 `/tmp/codeql_analysis/` 目录下）
2. 复制到你的GitHub仓库的 `.github/workflows/` 目录
3. 提交并推送
4. 在GitHub Actions中手动触发工作流

## 与其他版本的对比

| 特性 | target_select.py | target_select_advanced.py | target_select_outdated.py |
|------|------------------|---------------------------|---------------------------|
| 使用搜索API | ✅ | ✅ | ❌ |
| 关键词搜索 | ✅ | ✅ | ❌ |
| 直接获取仓库 | ❌ | ❌ | ✅ |
| 时间过滤 | ❌ | ❌ | ✅ (最近2个月) |
| Dependabot检测 | ❌ | ❌ | ✅ |
| 依赖文件检测 | ❌ | ❌ | ✅ |
| CodeQL配置生成 | ❌ | ❌ | ✅ |
| 语言分类 | ❌ | ✅ | ❌ |
| 自定义查询 | ❌ | ✅ | ❌ |

## API速率限制

### 未认证请求
- 每小时60个请求

### 认证请求（使用Token）
- 每小时5000个请求

**建议**：由于此工具需要大量API调用（每个仓库至少2-3次），强烈建议使用GitHub Token。

## 常见问题

### Q: 为什么不使用搜索API？

A: 搜索API有以下限制：
- 每分钟最多30次搜索请求（即使有Token）
- 结果可能不完整或不准确
- 无法精确控制时间范围

直接获取方式虽然需要更多API调用，但：
- 结果更准确和完整
- 可以精确控制筛选条件
- 不受搜索API的特殊限制

### Q: 为什么只获取最近2个月的项目？

A: 
- 最近更新的项目更可能正在活跃开发
- 减少API调用次数
- 重点关注活跃且流行的项目

你可以通过修改代码调整这个时间范围（修改`days_back`参数）。

### Q: 如何判断项目真的有过时依赖？

A: 工具使用两种方法：
1. **Dependabot警报**：如果启用，说明GitHub已检测到安全问题
2. **依赖文件存在**：说明项目使用包管理器，可能有依赖

建议手动验证并使用专门的依赖检查工具（如 `npm audit`, `pip-audit`, `snyk`等）。

### Q: CodeQL支持哪些语言？

A: 目前支持：
- Python
- JavaScript/TypeScript
- Java
- C/C++
- C#
- Go
- Ruby

### Q: 获取过程很慢怎么办？

A: 
1. 确保设置了`GITHUB_TOKEN`
2. 减少`max_repos`参数（修改代码中的值）
3. 优化网络连接
4. 使用缓存（可以修改代码添加缓存机制）

## 最佳实践

1. **设置Token**：始终使用GitHub Token以避免API限制
2. **分批处理**：不要一次获取太多项目
3. **定期运行**：可以设置cron作业定期运行此工具
4. **验证结果**：自动检测只是第一步，需要人工验证
5. **负责任披露**：如果发现真实漏洞，请负责任地披露

## 进阶使用

### 自定义时间范围

修改代码中的`days_back`参数：

```python
checker = OutdatedDependencyChecker(
    github_token=github_token,
    min_stars=500,
    days_back=30  # 改为30天
)
```

### 自定义star数阈值

```python
checker = OutdatedDependencyChecker(
    github_token=github_token,
    min_stars=1000,  # 改为1000
    days_back=60
)
```

### 导出到自定义文件

```python
checker.export_results(projects, "my_custom_output.json")
```

## 安全和法律说明

⚠️ **重要提示**：

1. 此工具**仅用于安全研究和教育目的**
2. 不要用于未经授权的渗透测试或攻击
3. 遵守相关法律法规和GitHub服务条款
4. 尊重项目维护者的劳动成果
5. 如发现漏洞，请负责任地披露

## 许可证

MIT License
