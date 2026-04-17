package com.ehs.business.interfaces.dto;

import java.util.List;

/**
 * 分页响应 DTO
 */
public class PageResponse<T> {
    private boolean success;
    private String message;
    private DataWrapper<T> data;

    public static <T> PageResponse<T> ok(DataWrapper<T> data) {
        PageResponse<T> resp = new PageResponse<>();
        resp.success = true;
        resp.message = "成功";
        resp.data = data;
        return resp;
    }

    public static <T> PageResponse<T> fail(String message) {
        PageResponse<T> resp = new PageResponse<>();
        resp.success = false;
        resp.message = message;
        return resp;
    }

    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public DataWrapper<T> getData() { return data; }
    public void setData(DataWrapper<T> data) { this.data = data; }

    public static class DataWrapper<T> {
        private long total;
        private long pending;
        private long processing;
        private long resolved;
        private List<T> alerts;

        public DataWrapper() {}

        public DataWrapper(long total, long pending, long processing, long resolved, List<T> alerts) {
            this.total = total;
            this.pending = pending;
            this.processing = processing;
            this.resolved = resolved;
            this.alerts = alerts;
        }

        public long getTotal() { return total; }
        public void setTotal(long total) { this.total = total; }
        public long getPending() { return pending; }
        public void setPending(long pending) { this.pending = pending; }
        public long getProcessing() { return processing; }
        public void setProcessing(long processing) { this.processing = processing; }
        public long getResolved() { return resolved; }
        public void setResolved(long resolved) { this.resolved = resolved; }
        public List<T> getAlerts() { return alerts; }
        public void setAlerts(List<T> alerts) { this.alerts = alerts; }
    }
}
