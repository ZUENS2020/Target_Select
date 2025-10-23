# Target Select 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

运行基础版本（最简单）：

```bash
python target_select.py
```

运行高级版本（更多功能）：

```bash
python target_select_advanced.py
```

### 3. 设置GitHub Token（推荐）

为避免API限制，强烈建议设置GitHub Token：

```bash
export GITHUB_TOKEN=your_personal_access_token
```

#### 如何获取GitHub Token：

1. 登录GitHub
2. 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 "Generate new token"
4. 选择 "Generate new token (classic)"
5. 不需要选择任何特殊权限（用于提高公开API限制即可）
6. 复制生成的token并设置到环境变量

## 详细功能说明

### 基础版本 (target_select.py)

适合快速搜索和简单使用。

**功能：**
- 自动搜索包含安全漏洞关键词的项目
- 筛选star数 > 500的项目
- 导出结果为JSON格式

**搜索策略：**
- 搜索包含 "security vulnerability" 的项目
- 搜索包含 "CVE" 的项目
- 搜索包含 "security issue" 的项目
- 搜索包含 "outdated dependencies" 的项目

### 高级版本 (target_select_advanced.py)

提供更多自定义选项和功能。

#### 命令行参数

```bash
# 查看帮助
python target_select_advanced.py --help

# 使用自定义配置文件
python target_select_advanced.py -c myconfig.json

# 按编程语言过滤（例如Python）
python target_select_advanced.py -l Python

# 自定义搜索查询
python target_select_advanced.py -q "SQL injection"

# 按配置中的多种语言分类搜索
python target_select_advanced.py --by-language

# 自定义输出文件名
python target_select_advanced.py -o my_results.json

# 查看API速率限制状态
python target_select_advanced.py --rate-limit

# 自定义最小star数
python target_select_advanced.py --min-stars 1000

# 自定义最大结果数
python target_select_advanced.py --max-results 100
```

#### 使用示例

**示例1：搜索Python项目中的SQL注入漏洞**

```bash
python target_select_advanced.py -l Python -q "SQL injection" --min-stars 500
```

**示例2：按多种语言分类搜索**

```bash
python target_select_advanced.py --by-language -o results_by_lang.json
```

**示例3：搜索特定关键词**

```bash
python target_select_advanced.py -q "XSS vulnerability" --max-results 20
```

**示例4：使用自定义配置**

首先创建配置文件 `my_config.json`：

```json
{
  "min_stars": 1000,
  "max_results": 100,
  "search_keywords": [
    "XSS",
    "CSRF",
    "SQL injection",
    "remote code execution"
  ],
  "languages": ["JavaScript", "PHP", "Java"]
}
```

然后运行：

```bash
python target_select_advanced.py -c my_config.json
```

## 配置文件说明

默认配置文件 `config.json` 的结构：

```json
{
  "github_token": "",           // GitHub token（可选）
  "min_stars": 500,             // 最小star数
  "max_results": 50,            // 最大结果数
  "search_keywords": [          // 搜索关键词列表
    "security vulnerability",
    "CVE",
    "security issue",
    "outdated dependencies"
  ],
  "languages": [                // 支持的编程语言列表
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

### 配置参数说明

- `github_token`: GitHub API token，用于提高API速率限制
- `min_stars`: 最小star数，只返回star数大于此值的项目
- `max_results`: 最大返回结果数
- `search_keywords`: 搜索关键词列表，用于匹配可能存在漏洞的项目
- `languages`: 编程语言列表，用于按语言分类搜索

## 输出格式

### JSON输出文件结构

```json
{
  "generated_at": "2024-01-01T00:00:00.000000",
  "total_projects": 50,
  "min_stars": 500,
  "projects": [
    {
      "name": "project-name",
      "full_name": "owner/project-name",
      "description": "项目描述",
      "url": "https://github.com/owner/project-name",
      "clone_url": "https://github.com/owner/project-name.git",
      "stars": 1234,
      "forks": 567,
      "language": "Python",
      "updated_at": "2024-01-01T00:00:00Z",
      "created_at": "2023-01-01T00:00:00Z",
      "has_issues": true,
      "open_issues": 15,
      "topics": ["security", "vulnerability"]
    }
  ]
}
```

## 编程方式使用

查看 `example_usage.py` 获取更多编程示例：

```python
from target_select import GitHubTargetSelector

# 创建选择器
selector = GitHubTargetSelector(github_token="your_token", min_stars=500)

# 搜索项目
projects = selector.search_vulnerable_projects(language="Python", max_results=20)

# 处理结果
for project in projects:
    print(f"{project['full_name']} - {project['stars']} stars")

# 导出结果
selector.export_results(projects, "my_output.json")
```

## API速率限制

### 未认证请求
- 每小时60个请求（搜索API：每分钟10个）

### 认证请求（使用Token）
- 每小时5000个请求（搜索API：每分钟30个）

### 查看当前限制状态

```bash
python target_select_advanced.py --rate-limit
```

## 常见问题

### Q: 为什么搜索不到结果？

A: 可能的原因：
1. API速率限制 - 建议设置GitHub Token
2. 搜索关键词太具体 - 尝试使用更通用的关键词
3. Star数设置太高 - 尝试降低 `min_stars` 参数

### Q: 如何避免API限制？

A: 
1. 设置 `GITHUB_TOKEN` 环境变量
2. 减少搜索频率
3. 减少 `max_results` 参数值
4. 使用更具体的搜索条件减少查询次数

### Q: 如何搜索特定类型的漏洞？

A: 使用 `-q` 参数指定具体的漏洞类型：

```bash
# SQL注入
python target_select_advanced.py -q "SQL injection"

# XSS
python target_select_advanced.py -q "XSS cross-site scripting"

# RCE
python target_select_advanced.py -q "remote code execution RCE"
```

### Q: 输出的项目真的存在漏洞吗？

A: 工具基于关键词搜索，返回的是**可能**存在漏洞的项目。这些项目可能：
- 曾经有安全问题（已修复）
- 正在修复安全问题
- 是故意包含漏洞的教学项目
- 在讨论安全问题但本身没有漏洞

建议进一步人工审查和验证。

## 安全和法律说明

⚠️ **重要提示**：

1. 此工具**仅用于安全研究和教育目的**
2. 不要用于未经授权的渗透测试或攻击
3. 遵守相关法律法规和GitHub服务条款
4. 尊重项目维护者的劳动成果
5. 如发现漏洞，请负责任地披露

## 高级技巧

### 1. 组合使用多个条件

```bash
python target_select_advanced.py \
  -l JavaScript \
  -q "authentication bypass" \
  --min-stars 1000 \
  --max-results 30 \
  -o auth_bypass_js.json
```

### 2. 批量处理多个语言

创建脚本 `batch_search.sh`：

```bash
#!/bin/bash

languages=("Python" "JavaScript" "Java" "PHP" "Go")

for lang in "${languages[@]}"; do
  echo "Searching $lang projects..."
  python target_select_advanced.py -l "$lang" -o "results_${lang}.json"
  sleep 5  # 避免API限制
done
```

### 3. 过滤和后处理结果

使用Python脚本进一步处理JSON输出：

```python
import json

# 读取结果
with open('vulnerable_targets.json', 'r') as f:
    data = json.load(f)

# 过滤：只保留open_issues > 10的项目
filtered = [p for p in data['projects'] if p['open_issues'] > 10]

# 保存过滤后的结果
data['projects'] = filtered
data['total_projects'] = len(filtered)

with open('filtered_results.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## 贡献和反馈

欢迎提交Issues和Pull Requests来改进这个工具！

## 许可证

MIT License
