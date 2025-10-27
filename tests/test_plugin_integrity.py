#!/usr/bin/env python3
"""
Schema Validator Pro - Plugin Integrity Test
测试插件文件完整性和后端 API 可用性
"""

import os
import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def test_plugin_files():
    """测试插件文件完整性"""
    print("\n" + "="*60)
    print("测试 1: 插件文件完整性")
    print("="*60)
    
    plugin_dir = project_root / "wordpress-plugin" / "schema-validator-pro"
    
    required_files = [
        "schema-validator-pro.php",
        "readme.txt",
        "assets/admin/js/metabox.js",
        "assets/admin/css/metabox.css",
        "assets/admin/css/admin.css",
    ]
    
    all_passed = True
    
    for file_path in required_files:
        full_path = plugin_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print_success(f"{file_path} ({size} bytes)")
        else:
            print_error(f"{file_path} 不存在")
            all_passed = False
    
    return all_passed

def test_plugin_php_syntax():
    """测试 PHP 文件语法"""
    print("\n" + "="*60)
    print("测试 2: PHP 文件语法检查")
    print("="*60)
    
    plugin_file = project_root / "wordpress-plugin" / "schema-validator-pro" / "schema-validator-pro.php"
    
    # 检查基本语法（简单的文本检查）
    try:
        with open(plugin_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键元素
        checks = [
            ("Plugin Name", "Plugin Name: Schema Validator Pro" in content),
            ("Text Domain", "Text Domain: schema-validator-pro" in content),
            ("Version", "Version: 1.0.0" in content),
            ("svp_inject_schema", "function svp_inject_schema()" in content),
            ("svp_enqueue_admin_assets", "function svp_enqueue_admin_assets(" in content),
            ("wp_json_encode", "wp_json_encode(" in content),
            ("check_ajax_referer", "check_ajax_referer(" in content),
        ]
        
        all_passed = True
        for name, check in checks:
            if check:
                print_success(f"{name} 存在")
            else:
                print_error(f"{name} 缺失")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"读取文件失败: {e}")
        return False

def test_js_syntax():
    """测试 JavaScript 文件语法"""
    print("\n" + "="*60)
    print("测试 3: JavaScript 文件语法检查")
    print("="*60)
    
    js_file = project_root / "wordpress-plugin" / "schema-validator-pro" / "assets" / "admin" / "js" / "metabox.js"
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键元素
        checks = [
            ("IIFE 包装", "(function($)" in content),
            ("use strict", "'use strict'" in content),
            ("initMetabox", "function initMetabox()" in content),
            ("generateSchema", "function generateSchema()" in content),
            ("svpMetaboxData", "svpMetaboxData" in content),
            ("AJAX 调用", "$.ajax(" in content),
        ]
        
        all_passed = True
        for name, check in checks:
            if check:
                print_success(f"{name} 存在")
            else:
                print_error(f"{name} 缺失")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"读取文件失败: {e}")
        return False

def test_css_files():
    """测试 CSS 文件"""
    print("\n" + "="*60)
    print("测试 4: CSS 文件检查")
    print("="*60)
    
    css_files = [
        "assets/admin/css/metabox.css",
        "assets/admin/css/admin.css",
    ]
    
    plugin_dir = project_root / "wordpress-plugin" / "schema-validator-pro"
    all_passed = True
    
    for css_file in css_files:
        full_path = plugin_dir / css_file
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含 CSS 规则
            if '{' in content and '}' in content:
                lines = len(content.split('\n'))
                print_success(f"{css_file} ({lines} 行)")
            else:
                print_error(f"{css_file} 格式错误")
                all_passed = False
                
        except Exception as e:
            print_error(f"{css_file} 读取失败: {e}")
            all_passed = False
    
    return all_passed

def test_readme_txt():
    """测试 readme.txt"""
    print("\n" + "="*60)
    print("测试 5: readme.txt 检查")
    print("="*60)
    
    readme_file = project_root / "wordpress-plugin" / "schema-validator-pro" / "readme.txt"
    
    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必需的 WordPress.org 字段
        checks = [
            ("Plugin Name", "=== Schema Validator Pro ===" in content),
            ("Contributors", "Contributors:" in content),
            ("Tags", "Tags:" in content),
            ("Requires at least", "Requires at least:" in content),
            ("Tested up to", "Tested up to:" in content),
            ("Stable tag", "Stable tag:" in content),
            ("License", "License:" in content),
            ("Description", "== Description ==" in content),
            ("Installation", "== Installation ==" in content),
            ("FAQ", "== Frequently Asked Questions ==" in content),
            ("Changelog", "== Changelog ==" in content),
        ]
        
        all_passed = True
        for name, check in checks:
            if check:
                print_success(f"{name} 存在")
            else:
                print_error(f"{name} 缺失")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_error(f"读取文件失败: {e}")
        return False

def test_backend_imports():
    """测试后端模块导入"""
    print("\n" + "="*60)
    print("测试 6: 后端模块导入")
    print("="*60)
    
    try:
        from backend.services.schema_generator import SchemaGenerator
        print_success("SchemaGenerator 导入成功")
        
        from backend.services.schema_validator import SchemaValidator
        print_success("SchemaValidator 导入成功")
        
        from backend.models.schema import SchemaGenerateRequest, SchemaValidateRequest
        print_success("Schema 模型导入成功")
        
        return True
        
    except Exception as e:
        print_error(f"导入失败: {e}")
        return False

def test_generator_basic():
    """测试生成器基本功能"""
    print("\n" + "="*60)
    print("测试 7: Schema Generator 基本功能")
    print("="*60)
    
    try:
        from backend.services.schema_generator import SchemaGenerator
        
        generator = SchemaGenerator()
        
        # 测试支持的类型
        types = generator.get_supported_types()
        if len(types) == 9:
            print_success(f"支持 {len(types)} 种 Schema 类型")
        else:
            print_error(f"预期 9 种类型，实际 {len(types)} 种")
            return False
        
        # 测试生成 Article
        schema = generator.generate(
            schema_type="Article",
            content="Test Article\n\nThis is a test article.",
            url="https://example.com/test"
        )
        
        if schema.get("@type") == "Article" and schema.get("headline") == "Test Article":
            print_success("Article Schema 生成成功")
        else:
            print_error("Article Schema 生成失败")
            return False
        
        # 测试嵌套对象
        if isinstance(schema.get("author"), dict) and schema["author"].get("@type") == "Person":
            print_success("嵌套 Person 对象正确")
        else:
            print_error("嵌套 Person 对象错误")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_validator_basic():
    """测试验证器基本功能"""
    print("\n" + "="*60)
    print("测试 8: Schema Validator 基本功能")
    print("="*60)
    
    try:
        from backend.services.schema_validator import SchemaValidator
        
        validator = SchemaValidator()
        
        # 测试有效的 Schema
        valid_schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": "Test Article",
            "author": {
                "@type": "Person",
                "name": "Test Author"
            }
        }
        
        is_valid, errors, warnings = validator.validate(valid_schema)
        
        if is_valid:
            print_success("有效 Schema 验证通过")
        else:
            print_error(f"有效 Schema 验证失败: {errors}")
            return False
        
        # 测试无效的 Schema
        invalid_schema = {
            "@context": "https://schema.org",
            "@type": "Article"
            # 缺少 headline
        }
        
        is_valid, errors, warnings = validator.validate(invalid_schema)
        
        if not is_valid and len(errors) > 0:
            print_success(f"无效 Schema 正确检测到错误: {len(errors)} 个")
        else:
            print_error("无效 Schema 未检测到错误")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Schema Validator Pro - 插件完整性测试")
    print("="*60)
    
    results = []
    
    # 运行所有测试
    results.append(("插件文件完整性", test_plugin_files()))
    results.append(("PHP 文件语法", test_plugin_php_syntax()))
    results.append(("JavaScript 文件语法", test_js_syntax()))
    results.append(("CSS 文件", test_css_files()))
    results.append(("readme.txt", test_readme_txt()))
    results.append(("后端模块导入", test_backend_imports()))
    results.append(("Schema Generator", test_generator_basic()))
    results.append(("Schema Validator", test_validator_basic()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print("\n" + "="*60)
    if passed == total:
        print_success(f"所有测试通过！({passed}/{total})")
        print("="*60)
        return 0
    else:
        print_error(f"部分测试失败 ({passed}/{total})")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

