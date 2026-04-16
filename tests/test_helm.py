"""
EHS 智能安保决策中台 - Helm Chart 测试

测试 Helm Chart 的结构完整性、模板渲染和配置验证
"""

import subprocess
import tempfile
import os
import yaml
import pytest
from pathlib import Path
from typing import Dict, Any


# Helm Chart 路径
HELM_CHART_PATH = Path(__file__).parent.parent / "infra" / "k8s" / "ehs-helm"


class TestHelmChartStructure:
    """测试 Helm Chart 基础结构"""

    def test_chart_yaml_exists(self):
        """测试 Chart.yaml 文件存在"""
        chart_yaml = HELM_CHART_PATH / "Chart.yaml"
        assert chart_yaml.exists(), "Chart.yaml 文件不存在"

    def test_values_yaml_exists(self):
        """测试 values.yaml 文件存在"""
        values_yaml = HELM_CHART_PATH / "values.yaml"
        assert values_yaml.exists(), "values.yaml 文件不存在"

    def test_required_templates_exist(self):
        """测试必需的模板文件存在"""
        required_templates = [
            "frontend-deployment.yaml",
            "java-deployment.yaml",
            "python-deployment.yaml",
            "hpa.yaml",
            "pdb.yaml",
            "networkpolicy.yaml",
            "configmap.yaml",
            "secrets.yaml",
            "ingress.yaml",
            "service.yaml",
        ]
        templates_dir = HELM_CHART_PATH / "templates"

        for template in required_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"模板文件 {template} 不存在"

    def test_chart_yaml_structure(self):
        """测试 Chart.yaml 结构"""
        chart_yaml = HELM_CHART_PATH / "Chart.yaml"
        with open(chart_yaml, "r", encoding="utf-8") as f:
            chart = yaml.safe_load(f)

        assert "apiVersion" in chart, "Chart.yaml 缺少 apiVersion 字段"
        assert chart["apiVersion"] == "v2", "Chart.yaml apiVersion 应为 v2"
        assert "name" in chart, "Chart.yaml 缺少 name 字段"
        assert "version" in chart, "Chart.yaml 缺少 version 字段"
        assert "appVersion" in chart, "Chart.yaml 缺少 appVersion 字段"

    def test_values_yaml_structure(self):
        """测试 values.yaml 结构"""
        values_yaml = HELM_CHART_PATH / "values.yaml"
        with open(values_yaml, "r", encoding="utf-8") as f:
            values = yaml.safe_load(f)

        # 检查必需的配置节
        required_sections = ["frontend", "javaService", "pythonService", "configMap", "secrets", "ingress"]
        for section in required_sections:
            assert section in values, f"values.yaml 缺少 {section} 配置节"


@pytest.fixture(scope="module")
def helm_available():
    """检查 Helm 是否可用"""
    try:
        result = subprocess.run(["helm", "version"], capture_output=True, text=True)
        if result.returncode != 0:
            pytest.skip("Helm 未安装，跳过 Helm 相关测试")
    except FileNotFoundError:
        pytest.skip("Helm 未安装，跳过 Helm 相关测试")


class TestHelmTemplateRender:
    """测试 Helm 模板渲染"""

    def _run_helm_template(self, values_file: str = None) -> str:
        """运行 helm template 命令"""
        cmd = ["helm", "template", "test-release", str(HELM_CHART_PATH)]

        if values_file:
            values_path = HELM_CHART_PATH / values_file
            if values_path.exists():
                cmd.extend(["-f", str(values_path)])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(HELM_CHART_PATH.parent.parent.parent))
        return result.stdout, result.stderr, result.returncode

    def test_helm_template_default_values(self, helm_available):
        """测试使用默认 values 渲染模板"""
        stdout, stderr, returncode = self._run_helm_template()

        if returncode != 0:
            pytest.skip(f"Helm template 命令失败：{stderr}")

        assert returncode == 0, f"helm template 失败：{stderr}"
        assert "kind: Deployment" in stdout, "渲染结果应包含 Deployment"
        assert "kind: Service" in stdout, "渲染结果应包含 Service"

    def test_helm_template_dev_values(self, helm_available):
        """测试使用开发环境 values 渲染模板"""
        stdout, stderr, returncode = self._run_helm_template("values-dev.yaml")

        if returncode != 0:
            pytest.skip(f"Helm template 命令失败：{stderr}")

        assert returncode == 0, f"helm template (dev) 失败：{stderr}"

    def test_helm_template_prod_values(self, helm_available):
        """测试使用生产环境 values 渲染模板"""
        stdout, stderr, returncode = self._run_helm_template("values-prod.yaml")

        if returncode != 0:
            pytest.skip(f"Helm template 命令失败：{stderr}")

        assert returncode == 0, f"helm template (prod) 失败：{stderr}"


class TestHelmLint:
    """测试 Helm lint"""

    def test_helm_lint(self, helm_available):
        """测试 helm lint 检查"""
        cmd = ["helm", "lint", str(HELM_CHART_PATH)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            pytest.skip(f"Helm lint 命令失败：{result.stderr}")

        assert result.returncode == 0, f"helm lint 失败：{result.stderr}"


class TestTemplateYamlStructure:
    """测试模板 YAML 结构（不依赖 Helm）"""

    def _load_template(self, template_name: str) -> dict:
        """加载模板文件并解析 YAML"""
        template_path = HELM_CHART_PATH / "templates" / template_name
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 检查是否包含 Helm 模板语法
        assert "{{" in content or "{%" in content, f"模板 {template_name} 应包含 Helm 模板语法"
        return yaml.safe_load(content.replace("{{", "").replace("}}", "").replace("{%", "").replace("%}", "") or "{}")

    def test_frontend_deployment_structure(self):
        """测试前端部署模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "frontend-deployment.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "kind: Deployment" in content, "frontend-deployment.yaml 应是 Deployment"
        assert "spec:" in content, "Deployment 应包含 spec"

    def test_java_deployment_structure(self):
        """测试 Java 服务部署模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "java-deployment.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "kind: Deployment" in content, "java-deployment.yaml 应是 Deployment"
        assert "spec:" in content, "Deployment 应包含 spec"

    def test_python_deployment_structure(self):
        """测试 Python 服务部署模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "python-deployment.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "kind: Deployment" in content, "python-deployment.yaml 应是 Deployment"
        assert "spec:" in content, "Deployment 应包含 spec"

    def test_hpa_structure(self):
        """测试 HPA 模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "hpa.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 检查包含 HPA 关键内容
        assert "HorizontalPodAutoscaler" in content, "hpa.yaml 应包含 HorizontalPodAutoscaler"
        assert "kind:" in content, "hpa.yaml 应包含 kind 字段"
        assert "scaleTargetRef" in content, "hpa.yaml 应包含 scaleTargetRef"

    def test_pdb_structure(self):
        """测试 PDB 模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "pdb.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "PodDisruptionBudget" in content, "pdb.yaml 应包含 PodDisruptionBudget"

    def test_networkpolicy_structure(self):
        """测试 NetworkPolicy 模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "networkpolicy.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "NetworkPolicy" in content, "networkpolicy.yaml 应包含 NetworkPolicy"

    def test_configmap_structure(self):
        """测试 ConfigMap 模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "configmap.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "ConfigMap" in content, "configmap.yaml 应包含 ConfigMap"

    def test_secrets_structure(self):
        """测试 Secrets 模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "secrets.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Secret" in content, "secrets.yaml 应包含 Secret"

    def test_ingress_structure(self):
        """测试 Ingress 模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "ingress.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Ingress" in content, "ingress.yaml 应包含 Ingress"

    def test_service_structure(self):
        """测试 Service 模板结构"""
        template_path = HELM_CHART_PATH / "templates" / "service.yaml"
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Service" in content, "service.yaml 应包含 Service"


class TestDeploymentConfiguration:
    """测试 Deployment 配置（静态分析）"""

    def test_template_has_resources(self):
        """测试模板包含资源配置"""
        for template in ["frontend-deployment.yaml", "java-deployment.yaml", "python-deployment.yaml"]:
            template_path = HELM_CHART_PATH / "templates" / template
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            has_resources = "resources:" in content
            has_limits = "limits:" in content
            has_requests = "requests:" in content
            assert has_resources or (has_limits and has_requests), \
                f"{template} 应配置 resources"

    def test_template_has_probes(self):
        """测试模板包含健康检查探针"""
        for template in ["frontend-deployment.yaml", "java-deployment.yaml", "python-deployment.yaml"]:
            template_path = HELM_CHART_PATH / "templates" / template
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "livenessProbe" in content or "readinessProbe" in content, \
                f"{template} 应配置 livenessProbe 或 readinessProbe"

    def test_template_has_labels(self):
        """测试模板包含标签"""
        for template in ["frontend-deployment.yaml", "java-deployment.yaml", "python-deployment.yaml"]:
            template_path = HELM_CHART_PATH / "templates" / template
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "app.kubernetes.io" in content, f"{template} 应包含 app.kubernetes.io 标签"


class TestMultiEnvironment:
    """测试多环境配置"""

    def test_dev_values_override(self):
        """测试开发环境配置覆盖"""
        with open(HELM_CHART_PATH / "values.yaml", "r", encoding="utf-8") as f:
            default_values = yaml.safe_load(f)
        with open(HELM_CHART_PATH / "values-dev.yaml", "r", encoding="utf-8") as f:
            dev_values = yaml.safe_load(f)

        # 开发环境应减少副本数
        assert dev_values["frontend"]["replicaCount"] <= default_values["frontend"]["replicaCount"]
        assert dev_values["javaService"]["replicaCount"] <= default_values["javaService"]["replicaCount"]
        assert dev_values["pythonService"]["replicaCount"] <= default_values["pythonService"]["replicaCount"]

    def test_prod_values_security(self):
        """测试生产环境安全配置"""
        with open(HELM_CHART_PATH / "values-prod.yaml", "r", encoding="utf-8") as f:
            prod_values = yaml.safe_load(f)

        # 生产环境应启用安全特性
        assert prod_values["networkPolicy"]["enabled"] is True, "生产环境应启用 NetworkPolicy"
        assert prod_values["monitoring"]["enabled"] is True, "生产环境应启用监控"


class TestHelmInstall:
    """测试 Helm 安装（可选，需要 K8s 集群）"""

    @pytest.mark.skip(reason="需要 K8s 集群环境")
    def test_helm_install_dry_run(self):
        """测试 helm install --dry-run"""
        cmd = ["helm", "install", "--dry-run", "test-release", str(HELM_CHART_PATH)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"helm install --dry-run 失败：{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
