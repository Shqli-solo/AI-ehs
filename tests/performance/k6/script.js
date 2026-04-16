/**
 * EHS 智能安保决策中台 - k6 性能测试脚本
 *
 * 测试场景:
 * 1. 健康检查接口 (/health)
 * 2. 告警上报接口 (/api/alert/report)
 * 3. 预案检索接口 (/api/plan/search)
 *
 * 性能阈值:
 * - P95 延迟 < 800ms
 * - 错误率 < 1%
 * - 50 并发用户 (VUs)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// ============================================================================
// 自定义指标
// ============================================================================

// 错误率指标
const errorRate = new Rate('errors');

// P95 延迟指标
const p95Latency = new Trend('p95_latency');

// 业务成功率指标
const businessSuccessRate = new Rate('business_success');

// ============================================================================
// 测试配置
// ============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// 测试场景配置
export const options = {
  // 阶段式负载测试
  stages: [
    { duration: '30s', target: 10 },   // 热身阶段：10 用户
    { duration: '1m', target: 50 },    // 爬坡阶段：50 用户
    { duration: '2m', target: 50 },    // 稳定阶段：50 用户
    { duration: '30s', target: 0 },    // 下降阶段：关闭
  ],

  // 性能阈值
  thresholds: {
    'http_req_duration': [
      'p(50)<500',  // P50 < 500ms
      'p(90)<700',  // P90 < 700ms
      'p(95)<800',  // P95 < 800ms
      'p(99)<1000', // P99 < 1000ms
    ],
    'errors': [
      'rate<0.01',  // 错误率 < 1%
    ],
    'business_success': [
      'rate>0.99',  // 业务成功率 > 99%
    ],
    'http_req_failed': [
      'rate<0.01',  // HTTP 失败率 < 1%
    ],
  },

  // 其他配置
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
  noVUConnectionReuse: true,  // 不重用连接，更真实的模拟
};

// ============================================================================
// 测试数据
// ============================================================================

const alertScenarios = [
  {
    alert_type: 'fire',
    alert_level: 4,
    location: '1 号楼生产车间',
    alert_content: '烟雾探测器检测到浓烟，温度异常升高',
  },
  {
    alert_type: 'gas_leak',
    alert_level: 5,
    location: '2 号楼化学品仓库',
    alert_content: '可燃气体浓度超标，达到爆炸下限',
  },
  {
    alert_type: 'temperature',
    alert_level: 3,
    location: '3 号楼配电室',
    alert_content: '设备温度异常，超过安全阈值',
  },
  {
    alert_type: 'intrusion',
    alert_level: 2,
    location: '厂区周界',
    alert_content: '红外对射探测器触发，检测到入侵行为',
  },
  {
    alert_type: 'water_leak',
    alert_level: 3,
    location: '地下室泵房',
    alert_content: '漏水检测绳报警，检测到积水',
  },
];

const searchQueries = [
  { query: '火灾应急处置流程', event_type: 'fire' },
  { query: '气体泄漏应急处理', event_type: 'gas_leak' },
  { query: '设备温度异常处理', event_type: 'temperature' },
  { query: '入侵事件应对措施', event_type: 'intrusion' },
  { query: '漏水事故应急预案', event_type: 'water_leak' },
  { query: '化学品泄漏处置', event_type: 'chemical' },
  { query: '电力故障应急处理', event_type: 'power' },
  { query: '自然灾害应急响应', event_type: 'natural_disaster' },
];

// ============================================================================
// 辅助函数
// ============================================================================

function getRandomItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function generateDeviceId() {
  return `device_${Math.floor(Math.random() * 9000 + 1000)}`;
}

function generateTimestamp() {
  const day = Math.floor(Math.random() * 28 + 1);
  const hour = Math.floor(Math.random() * 24);
  const minute = Math.floor(Math.random() * 60);
  return `2024-04-${day.toString().padStart(2, '0')}T${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}:00Z`;
}

// ============================================================================
// API 测试函数
// ============================================================================

/**
 * 测试：健康检查接口
 */
function healthCheck() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  };

  const response = http.get(`${BASE_URL}/health`, params);

  const checkResult = check(response, {
    'health status is 200': (r) => r.status === 200,
    'health status is healthy': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.status === 'healthy';
      } catch (e) {
        return false;
      }
    },
  });

  errorRate.add(!checkResult);
  businessSuccessRate.add(checkResult);

  return response;
}

/**
 * 测试：告警上报接口
 */
function reportAlert() {
  const scenario = getRandomItem(alertScenarios);

  const payload = {
    alert_type: scenario.alert_type,
    alert_level: scenario.alert_level,
    location: scenario.location,
    alert_content: scenario.alert_content,
    device_id: generateDeviceId(),
    timestamp: generateTimestamp(),
  };

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  };

  const response = http.post(
    `${BASE_URL}/api/alert/report`,
    JSON.stringify(payload),
    params
  );

  const checkResult = check(response, {
    'alert report status is 200': (r) => r.status === 200,
    'alert report success is true': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.success === true;
      } catch (e) {
        return false;
      }
    },
    'alert report has alert_id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.alert_id !== undefined;
      } catch (e) {
        return false;
      }
    },
  });

  errorRate.add(!checkResult);
  businessSuccessRate.add(checkResult);

  return response;
}

/**
 * 测试：预案检索接口
 */
function searchPlan() {
  const queryInfo = getRandomItem(searchQueries);

  const payload = {
    query: queryInfo.query,
    event_type: queryInfo.event_type,
    top_k: Math.floor(Math.random() * 8 + 3), // 3-10
  };

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  };

  const response = http.post(
    `${BASE_URL}/api/plan/search`,
    JSON.stringify(payload),
    params
  );

  const checkResult = check(response, {
    'plan search status is 200': (r) => r.status === 200,
    'plan search success is true': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.success === true;
      } catch (e) {
        return false;
      }
    },
    'plan search has plans array': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body.plans);
      } catch (e) {
        return false;
      }
    },
  });

  errorRate.add(!checkResult);
  businessSuccessRate.add(checkResult);

  return response;
}

// ============================================================================
// 主测试函数
// ============================================================================

export default function () {
  // 权重分配：告警上报 40%, 预案检索 40%, 健康检查 20%
  const choice = Math.random();

  if (choice < 0.4) {
    reportAlert();
  } else if (choice < 0.8) {
    searchPlan();
  } else {
    healthCheck();
  }

  // 思考时间 1-3 秒
  sleep(Math.random() * 2 + 1);
}

// ============================================================================
// 生命周期钩子
// ============================================================================

export function setup() {
  console.log('='.repeat(60));
  console.log('EHS 智能安保决策中台 - k6 性能测试');
  console.log('='.repeat(60));
  console.log(`目标地址：${BASE_URL}`);
  console.log('性能阈值:');
  console.log('  - P95 延迟 < 800ms');
  console.log('  - 错误率 < 1%');
  console.log('  - 并发用户数：50');
  console.log('='.repeat(60));

  return {
    startTime: new Date().toISOString(),
    baseUrl: BASE_URL,
  };
}

export function teardown(data) {
  console.log('\n' + '='.repeat(60));
  console.log('性能测试完成');
  console.log('='.repeat(60));
  console.log(`测试开始时间：${data.startTime}`);
  console.log(`测试结束时间：${new Date().toISOString()}`);
  console.log('='.repeat(60));
}

// ============================================================================
// 导出用于单独测试的函数
// ============================================================================

export function healthOnly() {
  healthCheck();
}

export function alertOnly() {
  reportAlert();
}

export function searchOnly() {
  searchPlan();
}
