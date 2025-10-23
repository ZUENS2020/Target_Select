#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Target Select的核心功能
"""

import unittest
import json
import os
import sys
from target_select import GitHubTargetSelector


class TestGitHubTargetSelector(unittest.TestCase):
    """测试GitHubTargetSelector类"""
    
    def setUp(self):
        """设置测试环境"""
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.selector = GitHubTargetSelector(
            github_token=self.github_token,
            min_stars=500
        )
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.selector.min_stars, 500)
        self.assertIn("Accept", self.selector.headers)
        
    def test_initialization_with_token(self):
        """测试带token的初始化"""
        if self.github_token:
            self.assertIn("Authorization", self.selector.headers)
        else:
            print("⚠️  未设置GITHUB_TOKEN，跳过token测试")
    
    def test_format_project_info(self):
        """测试项目信息格式化"""
        test_data = {
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "A test repository",
            "html_url": "https://github.com/owner/test-repo",
            "stargazers_count": 1000,
            "forks_count": 200,
            "language": "Python",
            "updated_at": "2024-01-01T00:00:00Z",
            "has_issues": True,
            "open_issues_count": 10
        }
        
        formatted = self.selector._format_project_info(test_data)
        
        self.assertEqual(formatted['name'], "test-repo")
        self.assertEqual(formatted['full_name'], "owner/test-repo")
        self.assertEqual(formatted['stars'], 1000)
        self.assertEqual(formatted['forks'], 200)
        self.assertEqual(formatted['language'], "Python")
    
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
                "updated_at": "2024-01-01T00:00:00Z",
                "has_issues": True,
                "open_issues": 10
            }
        ]
        
        test_filename = "/tmp/test_output.json"
        self.selector.export_results(test_projects, test_filename)
        
        # 验证文件已创建
        self.assertTrue(os.path.exists(test_filename))
        
        # 验证文件内容
        with open(test_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(data['total_projects'], 1)
        self.assertEqual(data['min_stars'], 500)
        self.assertEqual(len(data['projects']), 1)
        self.assertEqual(data['projects'][0]['name'], "test-repo")
        
        # 清理
        os.remove(test_filename)
    
    def test_min_stars_filter(self):
        """测试最小star数过滤"""
        self.assertEqual(self.selector.min_stars, 500)
        
        # 创建新的选择器with different min_stars
        selector2 = GitHubTargetSelector(min_stars=1000)
        self.assertEqual(selector2.min_stars, 1000)


class TestGitHubTargetSelectorIntegration(unittest.TestCase):
    """集成测试（需要网络连接和API访问）"""
    
    def setUp(self):
        """设置测试环境"""
        self.github_token = os.environ.get('GITHUB_TOKEN')
        if not self.github_token:
            self.skipTest("需要GITHUB_TOKEN来运行集成测试")
        
        self.selector = GitHubTargetSelector(
            github_token=self.github_token,
            min_stars=500
        )
    
    def test_search_repositories(self):
        """测试搜索仓库（需要API访问）"""
        # 使用一个很常见的查询
        results = self.selector._search_repositories(
            "security stars:>1000",
            per_page=5
        )
        
        # 验证返回结果
        self.assertIsInstance(results, list)
        # 注意：可能因为API限制返回空列表
        if results:
            self.assertIn('name', results[0])
            self.assertIn('full_name', results[0])
            self.assertIn('stars', results[0])


def run_tests():
    """运行所有测试"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              Target Select 测试套件                           ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestGitHubTargetSelector))
    
    # 如果有token，添加集成测试
    if os.environ.get('GITHUB_TOKEN'):
        print("✓ 检测到GITHUB_TOKEN，将运行集成测试")
        suite.addTests(loader.loadTestsFromTestCase(TestGitHubTargetSelectorIntegration))
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
