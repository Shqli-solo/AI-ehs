/**
 * API 错误码映射和错误处理
 *
 * 错误消息结构：问题 + 原因 + 修复
 * 例如："网络连接失败（原因：后端服务未启动，修复：请检查后端服务是否运行在 http://localhost:8000）"
 */

/**
 * HTTP 状态码映射
 */
export const HTTP_STATUS_MAP: Record<number, { title: string; message: string; fix: string }> = {
  400: {
    title: '请求参数错误',
    message: '请求参数格式不正确或包含无效数据',
    fix: '请检查输入数据是否符合要求',
  },
  401: {
    title: '未授权访问',
    message: '用户未登录或登录已过期',
    fix: '请重新登录后重试',
  },
  403: {
    title: '禁止访问',
    message: '没有权限执行此操作',
    fix: '请联系管理员获取相应权限',
  },
  404: {
    title: '资源不存在',
    message: '请求的资源或接口不存在',
    fix: '请检查请求地址是否正确',
  },
  408: {
    title: '请求超时',
    message: '服务器响应超时',
    fix: '请检查网络连接或稍后重试',
  },
  422: {
    title: '数据验证失败',
    message: '输入数据未通过服务器验证',
    fix: '请检查输入数据的格式和内容',
  },
  429: {
    title: '请求过于频繁',
    message: '短时间内发送了太多请求',
    fix: '请稍后再试',
  },
  500: {
    title: '服务器错误',
    message: '服务器内部发生错误',
    fix: '请稍后重试或联系技术支持',
  },
  502: {
    title: '网关错误',
    message: '网关服务器响应异常',
    fix: '请稍后重试或联系技术支持',
  },
  503: {
    title: '服务不可用',
    message: '服务器暂时不可用',
    fix: '请稍后重试或联系技术支持',
  },
  504: {
    title: '网关超时',
    message: '网关服务器响应超时',
    fix: '请稍后重试或联系技术支持',
  },
};

/**
 * 业务错误码映射（后端定义的错误码）
 */
export const BUSINESS_ERROR_MAP: Record<string, { title: string; message: string; fix: string }> = {
  // 告警相关错误
  'ALERT_NOT_FOUND': {
    title: '告警不存在',
    message: '指定的告警记录不存在',
    fix: '请检查告警 ID 是否正确',
  },
  'ALREADY_REPORTED': {
    title: '重复上报',
    message: '该告警已经被上报过',
    fix: '无需重复上报，可在告警列表中查看',
  },
  'INVALID_DEVICE': {
    title: '设备无效',
    message: '设备 ID 不存在或已被禁用',
    fix: '请检查设备 ID 是否正确',
  },

  // 预案相关错误
  'PLAN_NOT_FOUND': {
    title: '预案不存在',
    message: '未找到匹配的应急预案',
    fix: '请尝试其他关键词或联系管理员添加相关预案',
  },

  // 系统相关错误
  'SERVICE_UNAVAILABLE': {
    title: '服务不可用',
    message: 'AI 服务暂时不可用',
    fix: '请稍后重试或联系技术支持',
  },
  'DATABASE_ERROR': {
    title: '数据库错误',
    message: '数据库操作失败',
    fix: '请稍后重试或联系技术支持',
  },
  'EXTERNAL_SERVICE_ERROR': {
    title: '外部服务错误',
    message: '依赖的外部服务（如 ES、Milvus、LLM）不可用',
    fix: '系统已降级处理，如持续报错请联系技术支持',
  },
};

/**
 * 网络错误信息
 */
export const NETWORK_ERROR_INFO = {
  title: '网络连接失败',
  message: '无法连接到后端服务器',
  fix: '请检查：1) 后端服务是否运行在 http://localhost:8000 2) 网络连接是否正常 3) 防火墙设置',
};

/**
 * API 错误类型
 */
export type ApiErrorType =
  | 'NETWORK_ERROR'      // 网络错误
  | 'HTTP_ERROR'         // HTTP 状态码错误
  | 'BUSINESS_ERROR'     // 业务错误
  | 'TIMEOUT_ERROR'      // 超时错误
  | 'UNKNOWN_ERROR';     // 未知错误

/**
 * API 错误接口
 */
export interface ApiError {
  /** 错误类型 */
  type: ApiErrorType;
  /** 错误码（HTTP 状态码或业务错误码） */
  code: number | string;
  /** 错误标题（简短描述） */
  title: string;
  /** 错误详情（问题 + 原因 + 修复） */
  message: string;
  /** 原始错误对象 */
  originalError?: unknown;
  /** 请求 URL */
  url?: string;
  /** 请求方法 */
  method?: string;
}

/**
 * 创建友好的错误消息（问题 + 原因 + 修复）
 */
function createFriendlyMessage(
  problem: string,
  cause: string,
  fix: string
): string {
  return `${problem}（原因：${cause}，修复：${fix}）`;
}

/**
 * 将 HTTP 响应转换为 ApiError
 */
export function createHttpError(
  status: number,
  data?: unknown,
  url?: string,
  method?: string,
  originalError?: unknown
): ApiError {
  const errorInfo = HTTP_STATUS_MAP[status] || {
    title: '未知错误',
    message: '发生了未知错误',
    fix: '请联系技术支持',
  };

  return {
    type: 'HTTP_ERROR',
    code: status,
    title: errorInfo.title,
    message: createFriendlyMessage(errorInfo.title, errorInfo.message, errorInfo.fix),
    url,
    method,
    originalError,
  };
}

/**
 * 将业务错误码转换为 ApiError
 */
export function createBusinessError(
  errorCode: string,
  url?: string,
  method?: string,
  originalError?: unknown
): ApiError {
  const errorInfo = BUSINESS_ERROR_MAP[errorCode] || {
    title: '业务错误',
    message: '业务处理失败',
    fix: '请稍后重试',
  };

  return {
    type: 'BUSINESS_ERROR',
    code: errorCode,
    title: errorInfo.title,
    message: createFriendlyMessage(errorInfo.title, errorInfo.message, errorInfo.fix),
    url,
    method,
    originalError,
  };
}

/**
 * 创建网络错误
 */
export function createNetworkError(
  url?: string,
  method?: string,
  originalError?: unknown
): ApiError {
  return {
    type: 'NETWORK_ERROR',
    code: 'NETWORK_ERROR',
    title: NETWORK_ERROR_INFO.title,
    message: createFriendlyMessage(
      NETWORK_ERROR_INFO.title,
      NETWORK_ERROR_INFO.message,
      NETWORK_ERROR_INFO.fix
    ),
    url,
    method,
    originalError,
  };
}

/**
 * 创建超时错误
 */
export function createTimeoutError(
  timeoutMs: number,
  url?: string,
  method?: string,
  originalError?: unknown
): ApiError {
  return {
    type: 'TIMEOUT_ERROR',
    code: 'TIMEOUT',
    title: '请求超时',
    message: createFriendlyMessage(
      '请求超时',
      `服务器在 ${timeoutMs}ms 内未返回响应`,
      '1) 检查网络连接 2) 增加超时时间 3) 稍后重试'
    ),
    url,
    method,
    originalError,
  };
}

/**
 * 创建未知错误
 */
export function createUnknownError(
  originalError?: unknown,
  url?: string,
  method?: string
): ApiError {
  const errorMessage = originalError instanceof Error
    ? originalError.message
    : String(originalError ?? '未知错误');

  return {
    type: 'UNKNOWN_ERROR',
    code: 'UNKNOWN',
    title: '未知错误',
    message: createFriendlyMessage(
      '发生了未知错误',
      errorMessage,
      '请检查控制台日志或联系技术支持'
    ),
    url,
    method,
    originalError,
  };
}

/**
 * 从响应中解析错误
 */
export function parseErrorFromResponse(
  status: number,
  data: unknown,
  url?: string,
  method?: string,
  originalError?: unknown
): ApiError {
  // 尝试从响应数据中提取业务错误码
  if (data && typeof data === 'object') {
    const dataObj = data as Record<string, unknown>;

    // 尝试获取业务错误码
    const errorCode = dataObj.error_code as string | undefined;
    if (errorCode && BUSINESS_ERROR_MAP[errorCode]) {
      return createBusinessError(errorCode, url, method, originalError);
    }

    // 尝试获取错误字段
    const error = dataObj.error as string | undefined;
    const message = dataObj.message as string | undefined;

    if (error && BUSINESS_ERROR_MAP[error]) {
      return createBusinessError(error, url, method, originalError);
    }

    if (message && BUSINESS_ERROR_MAP[message]) {
      return createBusinessError(message, url, method, originalError);
    }
  }

  // 默认使用 HTTP 状态码映射
  return createHttpError(status, data, url, method, originalError);
}

/**
 * 判断是否为可重试的错误
 */
export function isRetryableError(error: ApiError): boolean {
  // 网络错误和超时错误可重试
  if (error.type === 'NETWORK_ERROR' || error.type === 'TIMEOUT_ERROR') {
    return true;
  }

  // 429 请求过于频繁可重试（优先检查，因为 429 < 500）
  if (error.type === 'HTTP_ERROR' && error.code === 429) {
    return true;
  }

  // 5xx 服务器错误可重试
  if (error.type === 'HTTP_ERROR' && typeof error.code === 'number') {
    return error.code >= 500 && error.code < 600;
  }

  return false;
}

/**
 * 获取错误摘要（用于 Toast 显示）
 */
export function getErrorSummary(error: ApiError): string {
  return `${error.title}: ${error.message.split('（')[0]}`;
}
