#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Target Select Outdated - 查找有过时依赖的项目
直接获取最近2个月内star多于500的项目，并检测过时依赖
"""

import requests
import json
import time
import sys
import os
import subprocess
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class OutdatedDependencyChecker:
    """过时依赖检测器"""
    
    def __init__(self, github_token: Optional[str] = None, min_stars: int = 500, days_back: int = 60):
        """
        初始化过时依赖检测器
        
        Args:
            github_token: GitHub API token
            min_stars: 最小star数量，默认500
            days_back: 追溯天数，默认60天（2个月）
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
        self.min_stars = min_stars
        self.days_back = days_back
        self.cutoff_date = datetime.now() - timedelta(days=days_back)
        
    def fetch_recent_popular_repos(self, max_repos: int = 100) -> List[Dict]:
        """
        直接获取最近流行的仓库（不使用搜索API）
        
        通过列出所有公开仓库，并按照stars和更新时间过滤
        
        Args:
            max_repos: 最大仓库数量
            
        Returns:
            仓库列表
        """
        print(f"🔍 正在获取最近 {self.days_back} 天内 star > {self.min_stars} 的项目...")
        print(f"   时间范围: {self.cutoff_date.date()} 至今\n")
        
        repos = []
        since_id = 0
        page = 0
        max_pages = 50  # 限制最大页数
        total_checked = 0  # 总共检查的仓库数
        
        while len(repos) < max_repos and page < max_pages:
            try:
                url = f"{self.base_url}/repositories"
                params = {
                    "since": since_id,
                    "per_page": 100
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                
                if response.status_code == 403:
                    self._handle_rate_limit(response)
                    break
                
                response.raise_for_status()
                batch = response.json()
                
                if not batch:
                    break
                
                print(f"📦 正在检查第 {page + 1} 批仓库 (共 {len(batch)} 个)...")
                
                # 获取每个仓库的详细信息
                for idx, repo in enumerate(batch, 1):
                    since_id = repo['id']
                    total_checked += 1
                    
                    # 显示实时进度
                    print(f"   [{idx}/{len(batch)}] 检查 {repo.get('full_name', 'unknown')}... ", end='', flush=True)
                    
                    # 预过滤：只获取可能符合条件的仓库详情
                    if repo.get('stargazers_count', 0) >= self.min_stars:
                        detailed_repo = self._get_repo_details(repo['full_name'])
                        if detailed_repo and self._is_recent_and_popular(detailed_repo):
                            repos.append(detailed_repo)
                            print(f"✓ 找到匹配! ({detailed_repo['stars']} ⭐, 更新于 {detailed_repo['updated_at'][:10]})")
                            
                            if len(repos) >= max_repos:
                                print(f"\n🎯 已达到目标数量 ({max_repos} 个项目)")
                                break
                        else:
                            print("- (不符合时间或star条件)")
                    else:
                        print(f"- (仅 {repo.get('stargazers_count', 0)} ⭐)")
                
                # 显示当前批次进度摘要
                print(f"   📊 进度: 已检查 {total_checked} 个仓库，找到 {len(repos)} 个符合条件的项目\n")
                
                page += 1
                time.sleep(1)  # 避免API限制
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  获取仓库列表时出错: {e}", file=sys.stderr)
                break
        
        print(f"\n✅ 完成扫描! 总共检查了 {total_checked} 个仓库，找到 {len(repos)} 个符合条件的仓库")
        return repos
    
    def _get_repo_details(self, full_name: str) -> Optional[Dict]:
        """
        获取仓库详细信息
        
        Args:
            full_name: 仓库全名 (owner/repo)
            
        Returns:
            仓库详细信息
        """
        try:
            url = f"{self.base_url}/repos/{full_name}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 403:
                self._handle_rate_limit(response)
                return None
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            repo_data = response.json()
            
            return self._format_project_info(repo_data)
            
        except Exception as e:
            # 静默处理错误，继续处理其他仓库
            return None
    
    def _is_recent_and_popular(self, repo: Dict) -> bool:
        """
        检查仓库是否最近更新且流行
        
        Args:
            repo: 仓库信息
            
        Returns:
            是否符合条件
        """
        if repo['stars'] < self.min_stars:
            return False
        
        # 检查更新时间
        updated_at = datetime.fromisoformat(repo['updated_at'].replace('Z', '+00:00'))
        if updated_at.replace(tzinfo=None) < self.cutoff_date:
            return False
        
        return True
    
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
            "default_branch": repo_data.get("default_branch", "main"),
        }
    
    def check_outdated_dependencies(self, repo: Dict) -> Dict:
        """
        检查项目是否有过时的依赖
        
        检查策略:
        1. 检查是否有 Dependabot 警报
        2. 检查依赖文件（package.json, requirements.txt, pom.xml等）
        
        Args:
            repo: 仓库信息
            
        Returns:
            依赖检查结果
        """
        result = {
            "has_outdated": False,
            "dependabot_alerts": False,
            "dependency_files": [],
            "checked_at": datetime.now().isoformat()
        }
        
        full_name = repo['full_name']
        
        # 检查 Dependabot 警报（需要特定权限）
        try:
            url = f"{self.base_url}/repos/{full_name}/vulnerability-alerts"
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 204:
                result['dependabot_alerts'] = True
                result['has_outdated'] = True
        except:
            pass
        
        # 检查常见的依赖文件
        dependency_files = self._check_dependency_files(repo)
        if dependency_files:
            result['dependency_files'] = dependency_files
            result['has_outdated'] = True  # 假设有依赖文件就可能有过时依赖
        
        return result
    
    def _check_dependency_files(self, repo: Dict) -> List[str]:
        """
        检查仓库中是否存在常见的依赖文件
        
        Args:
            repo: 仓库信息
            
        Returns:
            找到的依赖文件列表
        """
        full_name = repo['full_name']
        found_files = []
        
        # 常见的依赖文件
        dependency_file_patterns = {
            'package.json': 'JavaScript/Node.js',
            'requirements.txt': 'Python',
            'Pipfile': 'Python',
            'pom.xml': 'Java/Maven',
            'build.gradle': 'Java/Gradle',
            'Gemfile': 'Ruby',
            'go.mod': 'Go',
            'composer.json': 'PHP',
            'Cargo.toml': 'Rust',
        }
        
        for filename, lang in dependency_file_patterns.items():
            if self._file_exists(full_name, filename):
                found_files.append(f"{filename} ({lang})")
        
        return found_files
    
    def _file_exists(self, full_name: str, filename: str) -> bool:
        """
        检查文件是否存在于仓库中
        
        Args:
            full_name: 仓库全名
            filename: 文件名
            
        Returns:
            文件是否存在
        """
        try:
            url = f"{self.base_url}/repos/{full_name}/contents/{filename}"
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def prepare_codeql_analysis(self, repo: Dict, output_dir: str = "/tmp/codeql_analysis") -> Dict:
        """
        准备 CodeQL 分析
        
        为项目生成 CodeQL 配置
        
        Args:
            repo: 仓库信息
            output_dir: 输出目录
            
        Returns:
            分析配置信息
        """
        full_name = repo['full_name']
        language = repo.get('language', 'unknown').lower()
        
        # CodeQL 支持的语言
        codeql_languages = {
            'javascript': 'javascript',
            'typescript': 'javascript',
            'python': 'python',
            'java': 'java',
            'c': 'cpp',
            'c++': 'cpp',
            'cpp': 'cpp',
            'c#': 'csharp',
            'csharp': 'csharp',
            'go': 'go',
            'ruby': 'ruby',
        }
        
        codeql_lang = codeql_languages.get(language)
        
        if not codeql_lang:
            return {
                "supported": False,
                "language": language,
                "reason": "Language not supported by CodeQL"
            }
        
        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成 CodeQL 工作流配置
        workflow_config = self._generate_codeql_workflow(repo, codeql_lang)
        config_file = Path(output_dir) / f"{repo['name']}_codeql.yml"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(workflow_config)
        
        return {
            "supported": True,
            "language": language,
            "codeql_language": codeql_lang,
            "config_file": str(config_file),
            "clone_url": repo['clone_url'],
            "instructions": f"可以使用 CodeQL 分析此项目。配置文件已生成: {config_file}"
        }
    
    def _generate_codeql_workflow(self, repo: Dict, codeql_lang: str) -> str:
        """
        生成 CodeQL 工作流配置
        
        Args:
            repo: 仓库信息
            codeql_lang: CodeQL 语言
            
        Returns:
            工作流配置内容
        """
        workflow = f"""name: CodeQL Analysis for {repo['full_name']}

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
        language: [ '{codeql_lang}' ]
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      with:
        repository: {repo['full_name']}
    
    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{{{ matrix.language }}}}
    
    - name: Autobuild
      uses: github/codeql-action/autobuild@v2
    
    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
"""
        return workflow
    
    def _handle_rate_limit(self, response):
        """处理 API 速率限制"""
        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
        if rate_limit_remaining == '0':
            reset_time = response.headers.get('X-RateLimit-Reset', 'unknown')
            print(f"⚠️  API速率限制已达到。重置时间: {reset_time}", file=sys.stderr)
            print(f"   建议: 设置GITHUB_TOKEN环境变量以提高限制", file=sys.stderr)
    
    def export_results(self, projects: List[Dict], filename: str = "outdated_dependencies_targets.json"):
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
            "days_back": self.days_back,
            "cutoff_date": self.cutoff_date.isoformat(),
            "projects": projects
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 结果已保存到: {filename}")


def print_projects(projects: List[Dict]):
    """打印项目列表"""
    print("\n" + "="*80)
    print(f"找到 {len(projects)} 个可能有过时依赖的项目")
    print("="*80)
    
    for idx, project in enumerate(projects, 1):
        print(f"\n[{idx}] {project['full_name']}")
        print(f"    ⭐ Stars: {project['stars']} | 🍴 Forks: {project['forks']}")
        print(f"    💻 Language: {project['language'] or 'Unknown'}")
        print(f"    📝 Description: {project['description'][:100]}{'...' if len(project['description']) > 100 else ''}")
        print(f"    🔗 URL: {project['url']}")
        print(f"    📅 Updated: {project['updated_at']}")
        
        # 显示依赖检查结果
        if 'dependency_check' in project:
            dep = project['dependency_check']
            if dep.get('has_outdated'):
                print(f"    ⚠️  可能有过时依赖:")
                if dep.get('dependabot_alerts'):
                    print(f"       - 启用了 Dependabot 警报")
                if dep.get('dependency_files'):
                    print(f"       - 依赖文件: {', '.join(dep['dependency_files'])}")
        
        # 显示 CodeQL 准备结果
        if 'codeql_prep' in project:
            codeql = project['codeql_prep']
            if codeql.get('supported'):
                print(f"    🔍 CodeQL: 支持 ({codeql['codeql_language']})")
            else:
                print(f"    🔍 CodeQL: 不支持 ({codeql.get('reason', 'unknown')})")


def main():
    """主函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     Target Select Outdated - 过时依赖项目检测工具              ║
║                                                               ║
║  直接获取最近2个月内 star > 500 的项目                         ║
║  检测过时依赖并准备 CodeQL 分析                                ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # 获取 GitHub token
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        print("⚠️  警告: 未设置GITHUB_TOKEN环境变量")
        print("   建议设置token以避免API限制: export GITHUB_TOKEN=your_token")
        print("   继续使用匿名访问...\n")
    
    # 创建检测器
    checker = OutdatedDependencyChecker(
        github_token=github_token,
        min_stars=500,
        days_back=60  # 2个月
    )
    
    # 获取最近流行的仓库
    repos = checker.fetch_recent_popular_repos(max_repos=50)
    
    if not repos:
        print("❌ 未找到符合条件的项目")
        print("   提示: 可能需要设置 GITHUB_TOKEN 以避免 API 限制")
        return
    
    # 检查每个项目的过时依赖
    print("\n🔍 正在检查过时依赖...\n")
    projects_with_checks = []
    
    for idx, repo in enumerate(repos, 1):
        print(f"[{idx}/{len(repos)}] 检查 {repo['full_name']}...", end=' ')
        
        # 检查过时依赖
        dep_check = checker.check_outdated_dependencies(repo)
        repo['dependency_check'] = dep_check
        
        # 准备 CodeQL 分析
        codeql_prep = checker.prepare_codeql_analysis(repo)
        repo['codeql_prep'] = codeql_prep
        
        if dep_check['has_outdated']:
            print("✓ 可能有过时依赖")
            projects_with_checks.append(repo)
        else:
            print("- 未检测到明显的依赖问题")
        
        time.sleep(0.5)  # 避免 API 限制
    
    # 显示结果
    if projects_with_checks:
        print_projects(projects_with_checks)
        
        # 导出结果
        output_file = "outdated_dependencies_targets.json"
        checker.export_results(projects_with_checks, output_file)
        
        print(f"\n✅ 完成! 共找到 {len(projects_with_checks)} 个可能有过时依赖的项目")
        print(f"📄 详细结果已保存到: {output_file}")
        
        # 统计 CodeQL 支持情况
        codeql_supported = sum(1 for p in projects_with_checks if p.get('codeql_prep', {}).get('supported'))
        print(f"🔍 其中 {codeql_supported} 个项目支持 CodeQL 分析")
    else:
        print("\n❌ 未找到有过时依赖的项目")


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
