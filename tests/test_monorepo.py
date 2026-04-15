"""
EHS Monorepo - 项目骨架验证测试

验证 Monorepo 目录结构和配置文件的正确性。
"""

import os
import json
import sys
import xml.etree.ElementTree as ET
import tomllib
from pathlib import Path
import pytest


# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class TestMonorepoStructure:
    """测试 Monorepo 目录结构"""

    def test_apps_directory_exists(self):
        """验证 apps 目录存在"""
        apps_dir = PROJECT_ROOT / "apps"
        assert apps_dir.exists(), "apps 目录不存在"
        assert apps_dir.is_dir(), "apps 不是一个目录"

    def test_admin_console_directory_exists(self):
        """验证 admin-console 目录存在"""
        admin_console_dir = PROJECT_ROOT / "apps" / "admin-console"
        assert admin_console_dir.exists(), "apps/admin-console 目录不存在"

    def test_ehs_business_directory_exists(self):
        """验证 ehs-business 目录存在"""
        ehs_business_dir = PROJECT_ROOT / "apps" / "ehs-business"
        assert ehs_business_dir.exists(), "apps/ehs-business 目录不存在"

    def test_ehs_ai_directory_exists(self):
        """验证 ehs-ai 目录存在"""
        ehs_ai_dir = PROJECT_ROOT / "apps" / "ehs-ai"
        assert ehs_ai_dir.exists(), "apps/ehs-ai 目录不存在"

    def test_scripts_directory_exists(self):
        """验证 scripts 目录存在"""
        scripts_dir = PROJECT_ROOT / "scripts"
        assert scripts_dir.exists(), "scripts 目录不存在"

    def test_tests_directory_exists(self):
        """验证 tests 目录存在"""
        tests_dir = PROJECT_ROOT / "tests"
        assert tests_dir.exists(), "tests 目录不存在"


class TestConfigurationFiles:
    """测试配置文件"""

    def test_root_package_json_exists(self):
        """验证根目录 package.json 存在"""
        package_json = PROJECT_ROOT / "package.json"
        assert package_json.exists(), "根目录 package.json 不存在"

    def test_root_package_json_valid(self):
        """验证根目录 package.json 格式正确"""
        package_json = PROJECT_ROOT / "package.json"
        with open(package_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["name"] == "ehs-monorepo", "项目名应为 ehs-monorepo"
        assert "workspaces" in data, "应配置 workspaces"
        assert "apps/*" in data["workspaces"], "应包含 apps/*工作区"

    def test_admin_console_package_json_exists(self):
        """验证 admin-console package.json 存在"""
        package_json = PROJECT_ROOT / "apps" / "admin-console" / "package.json"
        assert package_json.exists(), "apps/admin-console/package.json 不存在"

    def test_admin_console_package_json_valid(self):
        """验证 admin-console package.json 格式正确"""
        package_json = PROJECT_ROOT / "apps" / "admin-console" / "package.json"
        with open(package_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["name"] == "@ehs/admin-console", "项目名应为@ehs/admin-console"
        assert "next" in data.get("dependencies", {}), "应依赖 next"
        assert "react" in data.get("dependencies", {}), "应依赖 react"

    def test_ehs_business_pom_xml_exists(self):
        """验证 ehs-business pom.xml 存在"""
        pom_xml = PROJECT_ROOT / "apps" / "ehs-business" / "pom.xml"
        assert pom_xml.exists(), "apps/ehs-business/pom.xml 不存在"

    def test_ehs_business_pom_xml_valid(self):
        """验证 ehs-business pom.xml 格式正确"""
        pom_xml = PROJECT_ROOT / "apps" / "ehs-business" / "pom.xml"
        tree = ET.parse(pom_xml)
        root = tree.getroot()

        # 处理 XML 命名空间
        ns = {"maven": "http://maven.apache.org/POM/4.0.0"}

        # 查找 artifactId
        artifact_id = root.find(".//maven:artifactId", ns)
        assert artifact_id is not None, "应包含 artifactId"
        assert artifact_id.text == "ehs-business", "artifactId 应为 ehs-business"

        # 查找 Java 版本
        java_version = root.find(".//maven:java.version", ns)
        assert java_version is not None, "应配置 java.version"
        assert java_version.text == "17", "Java 版本应为 17"

    def test_ehs_ai_pyproject_toml_exists(self):
        """验证 ehs-ai pyproject.toml 存在"""
        pyproject_toml = PROJECT_ROOT / "apps" / "ehs-ai" / "pyproject.toml"
        assert pyproject_toml.exists(), "apps/ehs-ai/pyproject.toml 不存在"

    def test_ehs_ai_pyproject_toml_valid(self):
        """验证 ehs-ai pyproject.toml 格式正确"""
        pyproject_toml = PROJECT_ROOT / "apps" / "ehs-ai" / "pyproject.toml"
        with open(pyproject_toml, "rb") as f:
            data = tomllib.load(f)

        assert data["tool"]["poetry"]["name"] == "ehs-ai", "项目名应为 ehs-ai"
        assert "fastapi" in data["tool"]["poetry"]["dependencies"], "应依赖 fastapi"
        assert "pytest" in data["tool"]["poetry"]["group"]["dev"]["dependencies"], "应包含 pytest 开发依赖"

    def test_gitignore_exists(self):
        """验证 .gitignore 存在"""
        gitignore = PROJECT_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore 不存在"

    def test_gitignore_content(self):
        """验证 .gitignore 内容"""
        gitignore = PROJECT_ROOT / ".gitignore"
        with open(gitignore, "r", encoding="utf-8") as f:
            content = f.read()

        assert "node_modules" in content, "应忽略 node_modules"
        assert "__pycache__" in content, "应忽略 __pycache__"
        assert "target/" in content, "应忽略 Maven target 目录"
        assert ".venv" in content or "venv" in content, "应忽略虚拟环境"

    def test_makefile_exists(self):
        """验证 Makefile 存在"""
        makefile = PROJECT_ROOT / "Makefile"
        assert makefile.exists(), "Makefile 不存在"

    def test_makefile_targets(self):
        """验证 Makefile 包含必要目标"""
        makefile = PROJECT_ROOT / "Makefile"
        with open(makefile, "r", encoding="utf-8") as f:
            content = f.read()

        assert "dev:" in content, "应包含 dev 目标"
        assert "test:" in content, "应包含 test 目标"
        assert "build:" in content, "应包含 build 目标"


class TestScripts:
    """测试脚本文件"""

    def test_setup_script_exists(self):
        """验证 setup.sh 存在"""
        setup_script = PROJECT_ROOT / "scripts" / "setup.sh"
        assert setup_script.exists(), "scripts/setup.sh 不存在"

    @pytest.mark.skipif(sys.platform == "win32", reason="Windows does not use Unix executable permission bits")
    def test_setup_script_executable(self):
        """验证 setup.sh 可执行"""
        setup_script = PROJECT_ROOT / "scripts" / "setup.sh"
        assert os.access(setup_script, os.X_OK), "scripts/setup.sh 应可执行"

    def test_run_tests_script_exists(self):
        """验证 run-tests.sh 存在"""
        run_tests_script = PROJECT_ROOT / "scripts" / "run-tests.sh"
        assert run_tests_script.exists(), "scripts/run-tests.sh 不存在"

    @pytest.mark.skipif(sys.platform == "win32", reason="Windows does not use Unix executable permission bits")
    def test_run_tests_script_executable(self):
        """验证 run-tests.sh 可执行"""
        run_tests_script = PROJECT_ROOT / "scripts" / "run-tests.sh"
        assert os.access(run_tests_script, os.X_OK), "scripts/run-tests.sh 应可执行"

    def test_setup_script_content(self):
        """验证 setup.sh 内容"""
        setup_script = PROJECT_ROOT / "scripts" / "setup.sh"
        with open(setup_script, "r", encoding="utf-8") as f:
            content = f.read()

        assert "npm install" in content, "应安装 npm 依赖"
        assert "poetry install" in content, "应安装 poetry 依赖"

    def test_run_tests_script_content(self):
        """验证 run-tests.sh 内容"""
        run_tests_script = PROJECT_ROOT / "scripts" / "run-tests.sh"
        with open(run_tests_script, "r", encoding="utf-8") as f:
            content = f.read()

        assert "pytest" in content, "应运行 pytest"
        assert "npm test" in content, "应运行 npm test"


class TestMonorepoIntegration:
    """测试 Monorepo 集成"""

    def test_workspace_configuration(self):
        """验证工作区配置"""
        package_json = PROJECT_ROOT / "package.json"
        with open(package_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        workspaces = data.get("workspaces", [])
        assert "apps/*" in workspaces, "应配置 apps/*工作区"

    def test_all_subprojects_have_package_files(self):
        """验证所有子项目都有配置文件"""
        subprojects = [
            ("admin-console", "package.json"),
            ("ehs-business", "pom.xml"),
            ("ehs-ai", "pyproject.toml"),
        ]

        for project, config_file in subprojects:
            config_path = PROJECT_ROOT / "apps" / project / config_file
            assert config_path.exists(), f"apps/{project}/{config_file} 不存在"

    def test_scripts_are_shell_scripts(self):
        """验证脚本是 Shell 脚本"""
        scripts = ["setup.sh", "run-tests.sh"]

        for script in scripts:
            script_path = PROJECT_ROOT / "scripts" / script
            with open(script_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
            assert first_line.startswith("#!/bin/bash"), f"{script} 应以 #!/bin/bash 开头"
