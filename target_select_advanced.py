#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Target Select Advanced - 高级版自动化漏洞挖掘目标选择工具
支持配置文件、多语言、自定义搜索策略
"""

import requests
import json
import time
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class GitHubTargetSelector:
    """GitHub目标项目选择器（高级版）"""
    
    def __init__(self, config: Dict):
        """
        初始化GitHub目标选择器
        
        Args:
            config: 配置字典
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        github_token = config.get('github_token') or config.get('GITHUB_TOKEN')
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
            
        self.min_stars = config.get('min_stars', 500)
        self.max_results = config.get('max_results', 50)
        self.search_keywords = config.get('search_keywords', [
            "security vulnerability",
            "CVE",
            "security issue"
        ])
        self.languages = config.get('languages', [])
        
    def search_vulnerable_projects(self, 
                                   language: Optional[str] = None,
                                   custom_query: Optional[str] = None) -> List[Dict]:
        """
        搜索可能存在漏洞的项目
        
        Args:
            language: 编程语言过滤
            custom_query: 自定义搜索查询
            
        Returns:
            项目列表
        """
        vulnerable_projects = []
        
        if custom_query:
            # 使用自定义查询
            search_queries = [f"{custom_query} stars:>{self.min_stars}"]
        else:
            # 使用配置的关键词
            search_queries = [f"{keyword} stars:>{self.min_stars}" 
                            for keyword in self.search_keywords]
        
        if language:
            search_queries = [f"{q} language:{language}" for q in search_queries]
        
        results_per_query = max(1, self.max_results // len(search_queries))
        
        for idx, query in enumerate(search_queries):
            try:
                print(f"  [{idx+1}/{len(search_queries)}] 搜索: {query[:50]}...", end=' ')
                results = self._search_repositories(query, results_per_query)
                print(f"找到 {len(results)} 个项目")
                vulnerable_projects.extend(results)
                time.sleep(2)  # 避免API限制
            except Exception as e:
                print(f"✗ 错误: {e}")
                
        # 去重
        seen = set()
        unique_projects = []
        for project in vulnerable_projects:
            if project['full_name'] not in seen:
                seen.add(project['full_name'])
                unique_projects.append(project)
                
        return unique_projects[:self.max_results]
    
    def search_by_language(self) -> Dict[str, List[Dict]]:
        """
        按语言分类搜索
        
        Returns:
            按语言分类的项目字典
        """
        results_by_language = {}
        
        for language in self.languages:
            print(f"\n🔍 搜索 {language} 项目...")
            projects = self.search_vulnerable_projects(language=language)
            if projects:
                results_by_language[language] = projects
                print(f"   找到 {len(projects)} 个 {language} 项目")
            else:
                print(f"   未找到 {language} 项目")
                
        return results_by_language
    
    def _search_repositories(self, query: str, per_page: int = 30) -> List[Dict]:
        """使用GitHub搜索API搜索仓库"""
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(per_page, 100)
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 403:
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                if rate_limit_remaining == '0':
                    reset_time = response.headers.get('X-RateLimit-Reset', 'unknown')
                    print(f"\n⚠️  API速率限制。重置时间: {reset_time}")
                    print("   建议: 设置GITHUB_TOKEN以提高限制")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            return [self._format_project_info(item) for item in items]
            
        except requests.exceptions.RequestException as e:
            if "403" not in str(e):
                print(f"错误: {e}")
            return []
    
    def _format_project_info(self, repo_data: Dict) -> Dict:
        """格式化项目信息"""
        return {
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description", "无描述"),
            "url": repo_data.get("html_url"),
            "clone_url": repo_data.get("clone_url"),
            "stars": repo_data.get("stargazers_count"),
            "forks": repo_data.get("forks_count"),
            "language": repo_data.get("language"),
            "updated_at": repo_data.get("updated_at"),
            "created_at": repo_data.get("created_at"),
            "has_issues": repo_data.get("has_issues"),
            "open_issues": repo_data.get("open_issues_count"),
            "topics": repo_data.get("topics", []),
        }
    
    def get_rate_limit(self) -> Dict:
        """获取API速率限制信息"""
        url = f"{self.base_url}/rate_limit"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def export_results(self, projects: List[Dict], filename: str = "vulnerable_targets.json"):
        """导出结果到JSON文件"""
        output = {
            "generated_at": datetime.now().isoformat(),
            "total_projects": len(projects),
            "min_stars": self.min_stars,
            "projects": projects
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 结果已保存到: {filename}")
    
    def export_by_language(self, projects_by_lang: Dict[str, List[Dict]], 
                          filename: str = "vulnerable_targets_by_language.json"):
        """导出按语言分类的结果"""
        output = {
            "generated_at": datetime.now().isoformat(),
            "min_stars": self.min_stars,
            "languages": projects_by_lang,
            "summary": {lang: len(projects) for lang, projects in projects_by_lang.items()}
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 分类结果已保存到: {filename}")


def load_config(config_file: str = "config.json") -> Dict:
    """加载配置文件"""
    config_path = Path(config_file)
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✓ 已加载配置文件: {config_file}")
    else:
        config = {}
        print(f"⚠️  配置文件不存在: {config_file}，使用默认配置")
    
    # 从环境变量读取token（优先级高于配置文件）
    import os
    env_token = os.environ.get('GITHUB_TOKEN')
    if env_token:
        config['GITHUB_TOKEN'] = env_token
    
    return config


def print_projects(projects: List[Dict]):
    """打印项目列表"""
    print("\n" + "="*80)
    print(f"找到 {len(projects)} 个潜在目标项目")
    print("="*80)
    
    for idx, project in enumerate(projects, 1):
        print(f"\n[{idx}] {project['full_name']}")
        print(f"    ⭐ Stars: {project['stars']} | 🍴 Forks: {project['forks']}")
        print(f"    💻 Language: {project['language'] or 'Unknown'}")
        print(f"    📝 Description: {project['description'][:100]}{'...' if len(project['description']) > 100 else ''}")
        print(f"    🔗 URL: {project['url']}")
        print(f"    📅 Updated: {project['updated_at']}")
        if project['open_issues'] > 0:
            print(f"    🐛 Open Issues: {project['open_issues']}")


def print_banner():
    """打印横幅"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║      Target Select Advanced - 高级漏洞挖掘目标选择工具          ║
║                                                               ║
║  自动从GitHub获取可能存在漏洞的项目 (stars > 500)               ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='自动化漏洞挖掘目标选择工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                          # 使用默认配置搜索
  %(prog)s -l Python                # 搜索Python项目
  %(prog)s -q "SQL injection"       # 自定义搜索查询
  %(prog)s --by-language            # 按语言分类搜索
  %(prog)s -c myconfig.json         # 使用自定义配置文件
  %(prog)s --rate-limit             # 查看API限制状态
        """
    )
    
    parser.add_argument('-c', '--config', default='config.json',
                       help='配置文件路径 (默认: config.json)')
    parser.add_argument('-l', '--language',
                       help='按编程语言过滤')
    parser.add_argument('-q', '--query',
                       help='自定义搜索查询')
    parser.add_argument('--by-language', action='store_true',
                       help='按配置中的语言列表分类搜索')
    parser.add_argument('-o', '--output', default='vulnerable_targets.json',
                       help='输出文件名 (默认: vulnerable_targets.json)')
    parser.add_argument('--rate-limit', action='store_true',
                       help='显示API速率限制信息')
    parser.add_argument('--min-stars', type=int,
                       help='最小star数（覆盖配置文件）')
    parser.add_argument('--max-results', type=int,
                       help='最大结果数（覆盖配置文件）')
    
    args = parser.parse_args()
    
    print_banner()
    
    # 加载配置
    config = load_config(args.config)
    
    # 命令行参数覆盖配置
    if args.min_stars:
        config['min_stars'] = args.min_stars
    if args.max_results:
        config['max_results'] = args.max_results
    
    # 创建选择器
    selector = GitHubTargetSelector(config)
    
    # 检查API限制
    if args.rate_limit:
        print("\n🔍 检查API速率限制...")
        rate_limit = selector.get_rate_limit()
        if 'error' not in rate_limit:
            core = rate_limit.get('resources', {}).get('core', {})
            search = rate_limit.get('resources', {}).get('search', {})
            print(f"\n核心API:")
            print(f"  剩余: {core.get('remaining')}/{core.get('limit')}")
            print(f"\n搜索API:")
            print(f"  剩余: {search.get('remaining')}/{search.get('limit')}")
        else:
            print(f"错误: {rate_limit['error']}")
        return
    
    # 执行搜索
    if args.by_language:
        print("\n🔍 按语言分类搜索潜在漏洞项目...")
        projects_by_lang = selector.search_by_language()
        
        # 显示结果
        for language, projects in projects_by_lang.items():
            if projects:
                print(f"\n{'='*80}")
                print(f"语言: {language}")
                print(f"{'='*80}")
                print_projects(projects)
        
        # 导出结果
        if projects_by_lang:
            output_file = args.output.replace('.json', '_by_language.json')
            selector.export_by_language(projects_by_lang, output_file)
            total = sum(len(p) for p in projects_by_lang.values())
            print(f"\n✅ 完成! 共找到 {total} 个项目，覆盖 {len(projects_by_lang)} 种语言")
    else:
        print("\n🔍 搜索潜在漏洞项目...")
        print(f"   条件: stars > {selector.min_stars}")
        if args.language:
            print(f"   语言: {args.language}")
        if args.query:
            print(f"   查询: {args.query}")
        print()
        
        projects = selector.search_vulnerable_projects(
            language=args.language,
            custom_query=args.query
        )
        
        if not projects:
            print("\n❌ 未找到符合条件的项目")
            print("   提示: 尝试设置GITHUB_TOKEN环境变量以避免API限制")
            return
        
        # 显示结果
        print_projects(projects)
        
        # 导出结果
        selector.export_results(projects, args.output)
        print(f"\n✅ 完成! 共找到 {len(projects)} 个潜在目标项目")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
