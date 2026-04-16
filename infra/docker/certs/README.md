# EHS gRPC TLS 证书配置指南

> **版本**: 2.0.0  
> **最后更新**: 2026-04-16  
> **安全等级**: 生产环境必需

---

## 概述

本文档说明如何为 EHS 智能安保决策中台的 gRPC 通信配置 TLS 双向认证（mTLS）。

### 为什么需要 TLS 双向认证？

- **服务器认证**: 客户端验证服务器身份，防止中间人攻击
- **客户端认证**: 服务器验证客户端身份，确保只有授权服务可以调用
- **加密通信**: 所有 gRPC 通信内容加密，防止窃听

---

## 证书结构

```
infra/docker/certs/
├── ca/
│   ├── ca.key          # CA 私钥（机密）
│   └── ca.crt          # CA 公钥证书（公开）
├── server/
│   ├── server.key      # 服务器私钥（机密）
│   ├── server.crt      # 服务器证书（公开）
│   └── server.csr      # 服务器证书签名请求
├── client/
│   ├── client.key      # 客户端私钥（机密）
│   ├── client.crt      # 客户端证书（公开）
│   └── client.csr      # 客户端证书签名请求
└── README.md           # 本文档
```

---

## 快速开始（开发环境）

### 1. 生成自签名证书（仅开发环境）

```bash
cd infra/docker/certs

# 生成 CA
openssl genrsa -out ca/ca.key 4096
openssl req -new -x509 -days 3650 -key ca/ca.key -out ca/ca.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=EHS/OU=Security/CN=EHS Root CA"

# 生成服务器证书
openssl genrsa -out server/server.key 2048
openssl req -new -key server/server.key -out server/server.csr \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=EHS/OU=Server/CN=ehs-ai"
openssl x509 -req -days 365 -in server/server.csr -CA ca/ca.crt -CAkey ca/ca.key \
    -CAcreateserial -out server/server.crt \
    -extfile <(echo "subjectAltName=DNS:localhost,IP:127.0.0.1")

# 生成客户端证书
openssl genrsa -out client/client.key 2048
openssl req -new -key client/client.key -out client/client.csr \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=EHS/OU=Client/CN=ehs-business"
openssl x509 -req -days 365 -in client/client.csr -CA ca/ca.crt -CAkey ca/ca.key \
    -CAcreateserial -out client/client.crt
```

### 2. 验证证书

```bash
# 验证服务器证书
openssl verify -CAfile ca/ca.crt server/server.crt

# 验证客户端证书
openssl verify -CAfile ca/ca.crt client/client.crt

# 查看证书详情
openssl x509 -in server/server.crt -text -noout
```

---

## 生产环境配置

### 1. 使用正式 CA 签发证书

生产环境应使用企业 CA 或公共 CA 签发的证书：

```bash
# 生成证书签名请求（CSR）
openssl req -new -key server.key -out server.csr \
    -subj "/C=CN/ST=Shanghai/L=Shanghai/O=YourCompany/OU=EHS/CN=ehs-ai.yourcompany.com"

# 将 CSR 提交给 CA 签发
# CA 将返回签名的证书 server.crt
```

### 2. 证书要求

| 项目 | 要求 |
|------|------|
| 密钥算法 | RSA 2048+ 或 ECDSA P-256+ |
| 签名算法 | SHA-256 或更高 |
| 有效期 | 服务器证书 ≤ 1 年，客户端证书 ≤ 2 年 |
| SAN | 必须包含服务域名和 IP |
| 密钥用途 | digitalSignature, keyEncipherment |
| 扩展密钥用途 | serverAuth / clientAuth |

---

## Kubernetes 部署

### 1. 创建 TLS Secret

```bash
# 服务器证书
kubectl create secret tls ehs-ai-tls \
    --cert=server/server.crt \
    --key=server/server.key \
    -n ehs-system

# 客户端证书
kubectl create secret generic ehs-business-tls \
    --from-file=client.crt=client/client.crt \
    --from-file=client.key=client/client.key \
    --from-file=ca.crt=ca/ca.crt \
    -n ehs-system

# CA 证书（用于验证）
kubectl create secret configmap ehs-ca \
    --from-file=ca.crt=ca/ca.crt \
    -n ehs-system
```

### 2. 在 Pod 中挂载证书

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ehs-ai
spec:
  containers:
  - name: ehs-ai
    image: ehs-ai:latest
    volumeMounts:
    - name: tls-certs
      mountPath: /etc/certs
      readOnly: true
  volumes:
  - name: tls-certs
    projected:
      sources:
      - secret:
          name: ehs-ai-tls
      - secret:
          name: ehs-ca
```

---

## 应用配置

### Java gRPC Client (application.yml)

```yaml
grpc:
  python-ai:
    host: ehs-ai.ehs-system.svc.cluster.local
    port: 50051
  timeout:
    seconds: 120
  retry:
    max: 3
    initial-backoff:
      ms: 100
    max-backoff:
      ms: 10000
  circuit-breaker:
    failure-threshold: 10
    reset-timeout:
      ms: 60000
  tls:
    enabled: true
    ca-cert: /etc/certs/ca.crt
    client-cert: /etc/certs/client.crt
    client-key: /etc/certs/client.key
```

### Python gRPC Server

```python
# 服务器配置
GRPC_SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 50051,
    "tls": {
        "enabled": True,
        "cert_file": "/etc/certs/server.crt",
        "key_file": "/etc/certs/server.key",
        "ca_file": "/etc/certs/ca.crt",
    }
}
```

---

## 证书轮换

### 自动轮换（推荐）

使用 cert-manager 自动管理证书：

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: ehs-ai-tls
  namespace: ehs-system
spec:
  secretName: ehs-ai-tls
  issuerRef:
    name: ehs-ca-issuer
    kind: ClusterIssuer
  commonName: ehs-ai.ehs-system.svc.cluster.local
  dnsNames:
  - ehs-ai.ehs-system.svc.cluster.local
  - ehs-ai
  ipAddresses:
  - 10.96.0.1
  duration: 8760h  # 1 年
  renewBefore: 720h  # 30 天前续签
```

### 手动轮换

```bash
# 1. 生成新证书
# 2. 更新 Kubernetes Secret
kubectl create secret tls ehs-ai-tls \
    --cert=new-server.crt \
    --key=new-server.key \
    -n ehs-system --dry-run=client -o yaml | kubectl apply -f -

# 3. 重启 Pod
kubectl rollout restart deployment/ehs-ai -n ehs-system
```

---

## 故障排查

### 常见问题

#### 1. 证书验证失败

```
error: x509: certificate signed by unknown authority
```

**原因**: CA 证书不匹配或未正确配置

**解决**:
- 确认使用正确的 CA 证书
- 检查证书链是否完整

#### 2. 主机名不匹配

```
error: x509: certificate is valid for localhost, not ehs-ai
```

**原因**: 证书 SAN 不包含访问的主机名

**解决**:
- 重新生成证书，添加正确的 SAN

#### 3. 证书过期

```
error: x509: certificate has expired or is not yet valid
```

**原因**: 证书已过期

**解决**:
- 更新证书并重启服务

### 调试命令

```bash
# 检查证书有效期
openssl x509 -in server.crt -noout -dates

# 检查证书主题
openssl x509 -in server.crt -noout -subject

# 检查证书 SAN
openssl x509 -in server.crt -noout -ext subjectAltName

# 测试 TLS 连接
openssl s_client -connect localhost:50051 -CAfile ca/ca.crt
```

---

## 安全最佳实践

1. **密钥保护**
   - 私钥永远不要提交到版本控制
   - 使用 Kubernetes Secrets 或 HashiCorp Vault 存储密钥
   - 设置严格的文件权限（600）

2. **证书管理**
   - 定期轮换证书（建议 90 天）
   - 使用自动化证书管理工具（cert-manager）
   - 监控证书过期时间

3. **网络隔离**
   - 在 Kubernetes 中使用 NetworkPolicy 限制访问
   - 仅允许授权服务访问 gRPC 端口

4. **审计日志**
   - 记录所有 TLS 握手失败
   - 监控异常连接尝试

---

## 参考资料

- [gRPC TLS 认证官方文档](https://grpc.io/docs/guides/auth/)
- [OpenSSL 证书生成指南](https://www.openssl.org/docs/man1.1.1/man1/req.html)
- [Kubernetes TLS Secrets](https://kubernetes.io/docs/concepts/configuration/secret/#tls-secrets)
- [cert-manager 文档](https://cert-manager.io/docs/)

---

**Last Updated**: 2026-04-16  
**Contact**: EHS Security Team <security@ehs.example.com>
