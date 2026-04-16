# EHS Helm Chart

EHS 智能安保决策中台的 Kubernetes Helm Chart，用于在 K8s 集群中部署完整平台。

## Chart 结构

```
ehs-helm/
├── Chart.yaml              # Helm Chart 元数据
├── values.yaml             # 默认配置
├── values-dev.yaml         # 开发环境配置
├── values-prod.yaml        # 生产环境配置
└── templates/
    ├── _helpers.tpl        # Helm 模板辅助函数
    ├── frontend-deployment.yaml    # 前端 Deployment
    ├── java-deployment.yaml        # Java 服务 Deployment
    ├── python-deployment.yaml      # Python AI 服务 Deployment
    ├── hpa.yaml                    # 水平自动伸缩 (HPA)
    ├── pdb.yaml                    # Pod 离散预算 (PDB)
    ├── networkpolicy.yaml          # 网络策略 (NetworkPolicy)
    ├── configmap.yaml              # 配置映射
    ├── secrets.yaml                # 密钥管理
    ├── ingress.yaml                # Ingress 路由
    ├── service.yaml                # Service 服务
    ├── serviceaccount.yaml         # ServiceAccount
    └── servicemonitor.yaml         # Prometheus ServiceMonitor
```

## 功能特性

- **多环境支持**: 开发环境 (dev) 和生产环境 (prod) 分离配置
- **自动伸缩**: HPA 支持 CPU 和内存自动伸缩
- **高可用**: PDB 确保 Pod 分布，支持滚动更新
- **网络安全**: NetworkPolicy 限制 Pod 间通信
- **监控集成**: Prometheus ServiceMonitor 支持
- **安全加固**: Pod Security Standards、密钥管理

## 安装

### 前置条件

- Kubernetes 1.21+
- Helm 3.0+
- Ingress Controller (nginx)
- Prometheus Operator (可选，用于监控)

### 安装命令

```bash
# 开发环境
helm install ehs-dev ./ehs-helm -f values-dev.yaml -n ehs-dev --create-namespace

# 生产环境
helm install ehs-prod ./ehs-helm -f values-prod.yaml -n ehs-prod --create-namespace
```

### 自定义配置

```bash
# 使用自定义 values 覆盖
helm install ehs ./ehs-helm \
  --set frontend.replicaCount=3 \
  --set pythonService.autoscaling.maxReplicas=50 \
  -n ehs
```

## 卸载

```bash
helm uninstall ehs -n ehs
```

## 配置说明

### 核心参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `global.environment` | 环境标识 | `dev` |
| `frontend.replicaCount` | 前端副本数 | `2` |
| `javaService.replicaCount` | Java 服务副本数 | `2` |
| `pythonService.replicaCount` | Python 服务副本数 | `2` |
| `ingress.enabled` | 启用 Ingress | `true` |
| `networkPolicy.enabled` | 启用网络策略 | `true` |
| `monitoring.enabled` | 启用监控 | `true` |

### 资源配置

每个服务都支持资源配置：

```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

### 自动伸缩

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 70
```

## 测试

```bash
# 运行测试
pytest tests/test_helm.py -v

# Helm lint 检查
helm lint ./ehs-helm

# 模板渲染测试
helm template test-release ./ehs-helm
```

## 安全建议

1. **生产环境必须使用外部密钥管理** (如 AWS Secrets Manager、HashiCorp Vault)
2. **启用 NetworkPolicy** 限制 Pod 间通信
3. **配置 TLS** 加密 Ingress 流量
4. **使用私有镜像仓库** 并配置 imagePullSecrets
5. **启用 Pod Security Standards** 限制容器权限

## 监控

启用监控后，Helm Chart 会自动创建 ServiceMonitor，需要 Prometheus Operator 支持。

Grafana Dashboard 指标：
- 请求量 (QPS)
- 响应时间 (P50/P90/P99)
- 错误率
- 资源使用率 (CPU/Memory)
- HPA 副本数

## 故障排查

### Pod 无法启动

```bash
# 查看 Pod 状态
kubectl get pods -n ehs

# 查看 Pod 详情
kubectl describe pod <pod-name> -n ehs

# 查看日志
kubectl logs <pod-name> -n ehs
```

### HPA 不工作

确保 metrics-server 已安装：

```bash
kubectl top nodes
kubectl top pods
```

### NetworkPolicy 问题

```bash
# 查看 NetworkPolicy
kubectl get networkpolicy -n ehs

# 测试网络连通性
kubectl run test-pod --rm -it --image=busybox --restart=Never -- sh
```

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-16 | 初始版本 |

## 参考资料

- [Helm 官方文档](https://helm.sh/docs/)
- [Kubernetes 部署](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [HPA 文档](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [NetworkPolicy 指南](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
