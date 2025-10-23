#!/bin/bash

# Target Select - 快速启动脚本

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          Target Select - 自动化漏洞挖掘目标选择工具              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 检查Python版本
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    echo "   请先安装Python 3.7或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python版本: $PYTHON_VERSION"

# 检查pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到pip"
    echo "   请先安装pip"
    exit 1
fi

# 安装依赖
echo ""
echo "📦 安装依赖..."
if pip3 install -r requirements.txt --quiet; then
    echo "✓ 依赖安装成功"
else
    echo "⚠️  依赖安装失败，尝试使用用户模式..."
    pip3 install --user -r requirements.txt
fi

# 检查GitHub Token
echo ""
echo "🔑 检查GitHub Token..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  未设置GITHUB_TOKEN环境变量"
    echo ""
    echo "   建议设置token以避免API限制："
    echo "   1. 访问 https://github.com/settings/tokens"
    echo "   2. 生成新的 Personal Access Token (classic)"
    echo "   3. 不需要选择任何特殊权限"
    echo "   4. 运行: export GITHUB_TOKEN=your_token"
    echo ""
    read -p "是否继续使用匿名访问? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
else
    echo "✓ 已设置GITHUB_TOKEN"
fi

# 显示菜单
echo ""
echo "选择运行模式："
echo "  1) 🆕 过时依赖检测 (推荐 - 新功能)"
echo "  2) 基础搜索版本"
echo "  3) 高级搜索版本"
echo "  4) 查看使用指南"
echo "  5) 退出"
echo ""
read -p "请选择 [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动过时依赖检测..."
        python3 target_select_outdated.py
        ;;
    2)
        echo ""
        echo "🚀 启动基础搜索版本..."
        python3 target_select.py
        ;;
    3)
        echo ""
        echo "🚀 启动高级搜索版本..."
        python3 target_select_advanced.py --help
        echo ""
        echo "高级版本支持更多选项，请查看上面的帮助信息"
        echo ""
        read -p "按Enter键继续使用默认参数运行，或Ctrl+C退出..."
        python3 target_select_advanced.py
        ;;
    4)
        echo ""
        if command -v less &> /dev/null; then
            less USAGE_GUIDE.md
        else
            cat USAGE_GUIDE.md
        fi
        ;;
    5)
        echo "再见!"
        exit 0
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 完成!"
