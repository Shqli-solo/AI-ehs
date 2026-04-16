# EHS 性能测试

本目录包含 EHS 智能安保决策中台的性能测试脚本，支持 Locust 和 k6 两种负载测试工具。

## 目录结构

```
tests/performance/
├── locustfile.py          # Locust 负载测试脚本
├── k6/
│   └── script.js          # k6 性能测试脚本
├── requirements.txt       # Python 依赖
└── reports/               # 测试报告输出目录 (自动生成)
    ├── locust/
    └── k6/
```

## 快速开始

### 1. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 k6 (可选)
# macOS: brew install k6
# Windows: scoop install k6
# Linux: 参考 https://k6.io/docs/getting-started/installation/
```

### 2. 启动服务

确保目标服务已启动：

```bash
# Python AI Service
cd python-ai-service
python -m uvicorn src.api.rest:app --reload --host 0.0.0.0 --port 8000
```

### 3. 运行测试

```bash
# 运行 Locust 测试 (50 并发用户)
./scripts/run_performance_test.sh locust

# 运行 k6 测试
./scripts/run_performance_test.sh k6

# 运行所有测试
./scripts/run_performance_test.sh all
```

## 配置选项

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `BASE_URL` | 目标服务地址 | `http://localhost:8000` |
| `LOCUST_USERS` | Locust 并发用户数 | `50` |
| `LOCUST_SPAWN_RATE` | Locust 用户生成速率 | `5` 用户/秒 |
| `LOCUST_RUN_TIME` | Locust 运行时间 | `60s` |
| `K6_DURATION` | k6 测试持续时间 | `3m` |
| `K6_VUS` | k6 并发用户数 | `50` |

### 自定义运行

```bash
# 自定义并发用户数和运行时间
LOCUST_USERS=100 LOCUST_RUN_TIME=120s ./scripts/run_performance_test.sh locust

# 指定目标服务
BASE_URL=http://api.ehs.example.com ./scripts/run_performance_test.sh k6
```

## 性能指标

### 验收标准

| 指标 | 阈值 | 说明 |
|------|------|------|
| P95 延迟 | < 800ms | 95% 请求响应时间 |
| 错误率 | < 1% | HTTP 错误和业务错误比例 |
| 并发用户 | 50 | 同时在线用户数 |

### Locust 指标

- **Requests/s**: 每秒请求数
- **P95**: 95% 请求响应时间
- **Failures/s**: 每秒失败数
- **Failures %**: 失败率

### k6 指标

k6 使用阈值断言自动判断测试是否通过：

```javascript
thresholds: {
  'http_req_duration': ['p(95)<800'],  // P95 < 800ms
  'errors': ['rate<0.01'],             // 错误率 < 1%
  'business_success': ['rate>0.99'],   // 业务成功率 > 99%
}
```

## 测试场景

### 告警上报 (`/api/alert/report`)

模拟 AIoT 设备上报告警事件，包含 5 种预设场景：
- 火灾告警 (fire)
- 气体泄漏 (gas_leak)
- 温度异常 (temperature)
- 入侵检测 (intrusion)
- 漏水检测 (water_leak)

### 预案检索 (`/api/plan/search`)

模拟用户搜索应急预案，支持 8 种事件类型查询。

### 健康检查 (`/health`)

模拟系统健康检查请求。

### 权重分配

- 告警上报：40%
- 预案检索：40%
- 健康检查：20%

## 测试报告

### Locust 报告

运行后生成以下文件：

- `report.html`: HTML 格式测试报告
- `results_*.csv`: CSV 格式原始数据
- `results.json`: JSON 格式测试结果

### k6 报告

运行后生成以下文件：

- `results.csv`: CSV 格式指标数据
- `results.json`: JSON 格式测试结果
- `output.log`: 控制台输出日志

## 结果分析

### 通过标准

测试完成后，检查以下指标：

1. **P95 延迟**: 应小于 800ms
2. **错误率**: 应小于 1%
3. **业务成功率**: 应大于 99%

### 性能优化建议

如果测试未通过，考虑以下优化方向：

1. **数据库优化**: 添加索引、优化查询语句
2. **缓存策略**: 使用 Redis 缓存热点数据
3. **异步处理**: 将非关键操作异步化
4. **资源扩容**: 增加 CPU/内存资源
5. **代码优化**: 分析性能瓶颈，优化热点代码

## 故障排查

### 服务不可用

```bash
# 检查服务状态
curl http://localhost:8000/health

# 查看服务日志
docker-compose logs -f
```

### Locust 安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 重新安装
pip install --force-reinstall locust
```

### k6 阈值未通过

查看 k6 输出中的详细阈值信息：

```
✓ http_req_duration...: avg=123ms min=50ms med=100ms max=500ms p(90)=200ms p(95)=300ms p(99)=450ms
✗ errors:             rate=1.5% < 1%  (FAIL)
```

## 参考资料

- [Locust 官方文档](https://docs.locust.io/)
- [k6 官方文档](https://k6.io/docs/)
- [性能测试最佳实践](https://k6.io/docs/using-k6/thresholds/)
