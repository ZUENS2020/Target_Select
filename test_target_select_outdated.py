#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Target Select Outdated 的核心功能
"""

import unittest
import json
import os
import sys
from datetime import datetime, timedelta
from target_select_outdated import OutdatedDependencyChecker


class TestOutdatedDependencyChecker(unittest.TestCase):
    """测试 OutdatedDependencyChecker 类"""
    
    def setUp(self):
        """设置测试环境"""
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.checker = OutdatedDependencyChecker(
            github_token=self.github_token,
            min_stars=500,
            days_back=60
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.checker.min_stars, 500)
        self.assertEqual(self.checker.days_back, 60)
        self.assertIn("Accept", self.checker.headers)
        self.assertIsNotNone(self.checker.cutoff_date)
        
        # 验证 cutoff_date 是大约60天前
        expected_cutoff = datetime.now() - timedelta(days=60)
        time_diff = abs((self.checker.cutoff_date - expected_cutoff).total_seconds())
        self.assertLess(time_diff, 60)  # 应该在60秒内
    
    def test_initialization_with_token(self):
        """测试带token的初始化"""
        if self.github_token:
            self.assertIn("Authorization", self.checker.headers)
        else:
            print("⚠️  未设置GITHUB_TOKEN，跳过token测试")
    
    def test_format_project_info(self):
        """测试项目信息格式化"""
        test_data = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "A test repository",
            "html_url": "https://github.com/owner/test-repo",
            "clone_url": "https://github.com/owner/test-repo.git",
            "stargazers_count": 1000,
            "forks_count": 200,
            "language": "Python",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_at": "2023-01-01T00:00:00Z",
            "has_issues": True,
            "open_issues_count": 10,
            "topics": ["security", "test"],
            "default_branch": "main"
        }
        
        formatted = self.checker._format_project_info(test_data)
        
        self.assertEqual(formatted['name'], "test-repo")
        self.assertEqual(formatted['full_name'], "owner/test-repo")
        self.assertEqual(formatted['stars'], 1000)
        self.assertEqual(formatted['forks'], 200)
        self.assertEqual(formatted['language'], "Python")
        self.assertEqual(formatted['default_branch'], "main")
        self.assertEqual(formatted['clone_url'], "https://github.com/owner/test-repo.git")
    
    def test_is_recent_and_popular(self):
        """测试仓库是否最近更新且流行"""
        # 最近更新且流行的仓库
        recent_repo = {
            "stars": 1000,
            "updated_at": datetime.now().isoformat()
        }
        self.assertTrue(self.checker._is_recent_and_popular(recent_repo))
        
        # Star数不足
        unpopular_repo = {
            "stars": 100,
            "updated_at": datetime.now().isoformat()
        }
        self.assertFalse(self.checker._is_recent_and_popular(unpopular_repo))
        
        # 更新时间太久
        old_repo = {
            "stars": 1000,
            "updated_at": (datetime.now() - timedelta(days=365)).isoformat()
        }
        self.assertFalse(self.checker._is_recent_and_popular(old_repo))
    
    def test_generate_codeql_workflow(self):
        """测试生成 CodeQL 工作流配置"""
        test_repo = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "language": "Python"
        }
        
        workflow = self.checker._generate_codeql_workflow(test_repo, "python")
        
        self.assertIn("CodeQL Analysis", workflow)
        self.assertIn("owner/test-repo", workflow)
        self.assertIn("python", workflow)
        self.assertIn("github/codeql-action", workflow)
    
    def test_prepare_codeql_analysis_supported_language(self):
        """测试准备 CodeQL 分析 - 支持的语言"""
        test_repo = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "language": "Python",
            "clone_url": "https://github.com/owner/test-repo.git"
        }
        
        result = self.checker.prepare_codeql_analysis(test_repo, "/tmp/test_codeql")
        
        self.assertTrue(result['supported'])
        self.assertEqual(result['codeql_language'], 'python')
        self.assertIn('config_file', result)
    
    def test_prepare_codeql_analysis_unsupported_language(self):
        """测试准备 CodeQL 分析 - 不支持的语言"""
        test_repo = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "language": "Brainfuck",  # 不支持的语言
            "clone_url": "https://github.com/owner/test-repo.git"
        }
        
        result = self.checker.prepare_codeql_analysis(test_repo, "/tmp/test_codeql")
        
        self.assertFalse(result['supported'])
        self.assertIn('reason', result)
    
    def test_check_outdated_dependencies_structure(self):
        """测试检查过时依赖的返回结构"""
        test_repo = {
            "full_name": "owner/test-repo",
            "name": "test-repo"
        }
        
        result = self.checker.check_outdated_dependencies(test_repo)
        
        # 验证返回结构
        self.assertIn('has_outdated', result)
        self.assertIn('dependabot_alerts', result)
        self.assertIn('dependency_files', result)
        self.assertIn('checked_at', result)
        self.assertIsInstance(result['has_outdated'], bool)
        self.assertIsInstance(result['dependabot_alerts'], bool)
        self.assertIsInstance(result['dependency_files'], list)
    
    def test_export_results(self):
        """测试结果导出"""
        test_projects = [
            {
                "name": "test-repo",
                "full_name": "owner/test-repo",
                "description": "Test",
                "url": "https://github.com/owner/test-repo",
                "stars": 1000,
                "forks": 200,
                "language": "Python",
                "updated_at": datetime.now().isoformat(),
                "dependency_check": {
                    "has_outdated": True,
                    "dependabot_alerts": False,
                    "dependency_files": ["requirements.txt"]
                }
            }
        ]
        
        test_filename = "/tmp/test_outdated_output.json"
        self.checker.export_results(test_projects, test_filename)
        
        # 验证文件已创建
        self.assertTrue(os.path.exists(test_filename))
        
        # 验证文件内容
        with open(test_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data['total_projects'], 1)
        self.assertEqual(data['min_stars'], 500)
        self.assertEqual(data['days_back'], 60)
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['name'], "test-repo")
        self.assertIn('cutoff_date', data)
        
        # 清理
        os.remove(test_filename)


class TestOutdatedDependencyCheckerIntegration(unittest.TestCase):
    """集成测试（需要网络连接和API访问）"""
    
    def setUp(self):
        """设置测试环境"""
        self.github_token = os.environ.get('GITHUB_TOKEN')
        if not self.github_token:
            self.skipTest("需要GITHUB_TOKEN来运行集成测试")
        
        self.checker = OutdatedDependencyChecker(
            github_token=self.github_token,
            min_stars=500,
            days_back=60
        )
    
    def test_get_repo_details(self):
        """测试获取仓库详情（需要API访问）"""
        # 使用一个已知的仓库
        repo_details = self.checker._get_repo_details("github/docs")
        
        if repo_details:
            self.assertIn('name', repo_details)
            self.assertIn('full_name', repo_details)
            self.assertIn('stars', repo_details)
            self.assertEqual(repo_details['full_name'], 'github/docs')


def run_tests():
    """运行所有测试"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║       Target Select Outdated 测试套件                         ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestOutdatedDependencyChecker))
    
    # 如果有token，添加集成测试
    if os.environ.get('GITHUB_TOKEN'):
        print("✓ 检测到GITHUB_TOKEN，将运行集成测试")
        suite.addTests(loader.loadTestsFromTestCase(TestOutdatedDependencyCheckerIntegration))
    else:
        print("⚠️  未设置GITHUB_TOKEN，跳过集成测试")
    
    print()
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果摘要
    print("\n" + "="*70)
    print("测试摘要:")
    print(f"  运行: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print(f"  跳过: {len(result.skipped)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
