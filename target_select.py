#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Target Select - 自动化漏洞挖掘目标选择工具
自动从GitHub获取可能存在漏洞的项目，筛选star数大于500的项目
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import List, Dict, Optional


class GitHubTargetSelector:
    """GitHub目标项目选择器"""
    
    def __init__(self, github_token: Optional[str] = None, min_stars: int = 500):
        """
        初始化GitHub目标选择器
        
        Args:
            github_token: GitHub API token (可选，但推荐使用以提高API限制)
            min_stars: 最小star数量，默认500
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
        self.min_stars = min_stars
        
    def search_vulnerable_projects(self, 
                                   language: Optional[str] = None,
                                   max_results: int = 100) -> List[Dict]:
        """
        搜索可能存在漏洞的项目
        
        搜索策略：
        1. 寻找有已知安全问题的项目
        2. 寻找依赖过时的项目
        3. 寻找长时间未更新但流行的项目
        
        Args:
            language: 编程语言过滤
            max_results: 最大返回结果数
            
        Returns:
            项目列表
        """
        vulnerable_projects = []
        
        # 搜索策略1: 有security标签或issues的项目
        search_queries = [
            f"security vulnerability stars:>{self.min_stars}",
            f"CVE stars:>{self.min_stars}",
            f"security issue stars:>{self.min_stars}",
            f"outdated dependencies stars:>{self.min_stars}",
        ]
        
        if language:
            search_queries = [f"{q} language:{language}" for q in search_queries]
        
        for query in search_queries:
            try:
                results = self._search_repositories(query, max_results // len(search_queries))
                vulnerable_projects.extend(results)
                time.sleep(2)  # 避免API限制
            except Exception as e:
                print(f"搜索查询 '{query}' 时出错: {e}", file=sys.stderr)
                
        # 去重
        seen = set()
        unique_projects = []
        for project in vulnerable_projects:
            if project['full_name'] not in seen:
                seen.add(project['full_name'])
                unique_projects.append(project)
                
        return unique_projects[:max_results]
    
    def _search_repositories(self, query: str, per_page: int = 30) -> List[Dict]:
        """
        使用GitHub搜索API搜索仓库
        
        Args:
            query: 搜索查询字符串
            per_page: 每页结果数
            
        Returns:
            仓库列表
        """
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(per_page, 100)
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            # 处理API限制
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
                if rate_limit_remaining == '0':
                    reset_time = response.headers.get('X-RateLimit-Reset', 'unknown')
                    print(f"⚠️  API速率限制已达到。重置时间: {reset_time}", file=sys.stderr)
                    print(f"   建议: 设置GITHUB_TOKEN环境变量以提高限制", file=sys.stderr)
                return []
            
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            return [self._format_project_info(item) for item in items]
            
        except requests.exceptions.RequestException as e:
            if "403" not in str(e):
                print(f"API请求失败: {e}", file=sys.stderr)
            return []
    
    def _format_project_info(self, repo_data: Dict) -> Dict:
        """
        格式化项目信息
        
        Args:
            repo_data: GitHub API返回的仓库数据
            
        Returns:
            格式化后的项目信息
        """
        return {
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description", "无描述"),
            "url": repo_data.get("html_url"),
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "language": repo_data.get("language"),
            "updated_at": repo_data.get("updated_at"),
            "has_issues": repo_data.get("has_issues"),
            "open_issues": repo_data.get("open_issues_count"),
        }
    
    def check_vulnerabilities(self, full_name: str) -> Dict:
        """
        检查项目的安全问题
        
        Args:
            full_name: 项目全名 (owner/repo)
            
        Returns:
            安全信息字典
        """
        # 检查是否有security advisories
        url = f"{self.base_url}/repos/{full_name}/vulnerability-alerts"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            # 204表示启用了安全警报，404表示未启用或没有权限
            has_security_alerts = response.status_code == 204
            
            return {
                "has_security_alerts": has_security_alerts,
                "checked_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"检查安全警报时出错: {e}", file=sys.stderr)
            return {"has_security_alerts": False, "error": str(e)}
    
    def export_results(self, projects: List[Dict], filename: str = "vulnerable_targets.json"):
        """
        导出结果到JSON文件
        
        Args:
            projects: 项目列表
            filename: 输出文件名
        """
        output = {
            "generated_at": datetime.now().isoformat(),
            "total_projects": len(projects),
            "min_stars": self.min_stars,
            "projects": projects
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {filename}")


def print_projects(projects: List[Dict]):
    """打印项目列表"""
    print("\n" + "="*80)
    print(f"找到 {len(projects)} 个潜在目标项目")
    print("="*80)
    
    for idx, project in enumerate(projects, 1):
        print(f"\n[{idx}] {project['full_name']}")
        print(f"    ⭐ Stars: {project['stars']} | 🍴 Forks: {project['forks']}")
        print(f"    💻 Language: {project['language'] or 'Unknown'}")
        print(f"    📝 Description: {project['description']}")
        print(f"    🔗 URL: {project['url']}")
        print(f"    📅 Last Updated: {project['updated_at']}")
        print(f"    🐛 Open Issues: {project['open_issues']}")


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          Target Select - 自动化漏洞挖掘目标选择工具              ║
║                                                               ║
║  自动从GitHub获取可能存在漏洞的项目 (stars > 500)               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # 可以从环境变量或配置文件读取token
    import os
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        print("⚠️  警告: 未设置GITHUB_TOKEN环境变量")
        print("   建议设置token以避免API限制: export GITHUB_TOKEN=your_token")
        print("   继续使用匿名访问...\n")
    
    # 创建选择器
    selector = GitHubTargetSelector(github_token=github_token, min_stars=500)
    
    print("🔍 正在搜索潜在的漏洞项目...")
    print("   搜索条件: stars > 500, 包含安全相关关键词\n")
    
    # 搜索项目
    projects = selector.search_vulnerable_projects(max_results=50)
    
    if not projects:
        print("❌ 未找到符合条件的项目")
        return
    
    # 显示结果
    print_projects(projects)
    
    # 导出结果
    output_file = "vulnerable_targets.json"
    selector.export_results(projects, output_file)
    
    print(f"\n✅ 完成! 共找到 {len(projects)} 个潜在目标项目")
    print(f"📄 详细结果已保存到: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}", file=sys.stderr)
        sys.exit(1)
