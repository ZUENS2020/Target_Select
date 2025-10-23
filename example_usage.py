#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例：如何使用Target Select工具
"""

import os
import json
from target_select import GitHubTargetSelector
from target_select_outdated import OutdatedDependencyChecker


def example_basic_search():
    """示例1: 基本搜索"""
    print("="*60)
    print("示例1: 基本搜索")
    print("="*60)
    
    # 创建选择器（可选：传入GitHub token）
    github_token = os.environ.get('GITHUB_TOKEN')
    selector = GitHubTargetSelector(github_token=github_token, min_stars=500)
    
    # 搜索项目
    projects = selector.search_vulnerable_projects(max_results=10)
    
    # 打印结果
    for project in projects:
        print(f"\n项目: {project['full_name']}")
        print(f"  Stars: {project['stars']}")
        print(f"  URL: {project['url']}")
    
    return projects


def example_language_filter():
    """示例2: 按语言过滤"""
    print("\n" + "="*60)
    print("示例2: 按Python语言过滤")
    print("="*60)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    selector = GitHubTargetSelector(github_token=github_token, min_stars=500)
    
    # 搜索Python项目
    projects = selector.search_vulnerable_projects(language="Python", max_results=10)
    
    for project in projects:
        print(f"\n项目: {project['full_name']}")
        print(f"  语言: {project['language']}")
        print(f"  Stars: {project['stars']}")
    
    return projects


def example_export_results():
    """示例3: 导出结果"""
    print("\n" + "="*60)
    print("示例3: 搜索并导出结果")
    print("="*60)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    selector = GitHubTargetSelector(github_token=github_token, min_stars=500)
    
    # 搜索项目
    projects = selector.search_vulnerable_projects(max_results=20)
    
    # 导出到文件
    selector.export_results(projects, "example_output.json")
    print(f"\n已导出 {len(projects)} 个项目")
    
    return projects


def example_check_vulnerabilities():
    """示例4: 检查特定项目的安全问题"""
    print("\n" + "="*60)
    print("示例4: 检查项目安全问题")
    print("="*60)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    selector = GitHubTargetSelector(github_token=github_token, min_stars=500)
    
    # 检查一个已知项目的安全警报
    # 注意：这需要适当的权限
    test_repo = "OWASP/NodeGoat"  # 已知的漏洞测试项目
    
    security_info = selector.check_vulnerabilities(test_repo)
    print(f"\n项目: {test_repo}")
    print(f"安全信息: {json.dumps(security_info, indent=2)}")
    
    return security_info


def example_outdated_dependencies():
    """示例5: 检测过时依赖（新功能）"""
    print("\n" + "="*60)
    print("示例5: 检测过时依赖（新功能）")
    print("="*60)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    
    # 创建过时依赖检测器
    checker = OutdatedDependencyChecker(
        github_token=github_token,
        min_stars=500,
        days_back=60  # 最近2个月
    )
    
    print("注意：此示例需要大量API调用，已注释掉实际执行代码")
    print("取消注释下面的代码以运行:")
    print()
    print("# 获取最近流行的仓库")
    print("# repos = checker.fetch_recent_popular_repos(max_repos=10)")
    print()
    print("# 检查过时依赖")
    print("# for repo in repos:")
    print("#     dep_check = checker.check_outdated_dependencies(repo)")
    print("#     if dep_check['has_outdated']:")
    print("#         print(f\"✓ {repo['full_name']} 可能有过时依赖\")")
    print()
    print("# 导出结果")
    print("# checker.export_results(repos, 'outdated_example.json')")
    
    return []


def main():
    """运行所有示例"""
    print("""
╔══════════════════════════════════════════════════════════╗
║              Target Select 使用示例                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查token
    if not os.environ.get('GITHUB_TOKEN'):
        print("⚠️  提示: 未设置GITHUB_TOKEN，可能会遇到API限制")
        print("   设置方法: export GITHUB_TOKEN=your_token\n")
    
    try:
        # 运行示例（注释掉部分示例以避免API限制）
        # example_basic_search()
        # example_language_filter()
        # example_export_results()
        # example_check_vulnerabilities()
        example_outdated_dependencies()  # 新功能示例
        
        print("\n✅ 示例完成!")
        print("   取消注释上面的示例函数以运行不同的示例")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
