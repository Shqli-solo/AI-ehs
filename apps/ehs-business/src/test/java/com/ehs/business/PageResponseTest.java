package com.ehs.business;

import com.ehs.business.interfaces.dto.PageResponse;
import com.ehs.business.interfaces.dto.PageResponse.DataWrapper;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * PageResponse DTO 单元测试
 *
 * 测试 ok() 和 fail() 工厂方法，以及 DataWrapper 内部类
 */
class PageResponseTest {

    @Nested
    @DisplayName("ok() 工厂方法")
    class OkTests {

        @Test
        @DisplayName("ok 返回 success=true")
        void okSuccessTrue() {
            DataWrapper<String> wrapper = new DataWrapper<>(10, 5, 3, 2, List.of("a"));
            PageResponse<String> response = PageResponse.ok(wrapper);

            assertTrue(response.isSuccess());
        }

        @Test
        @DisplayName("ok 返回 message=成功")
        void okMessage() {
            DataWrapper<String> wrapper = new DataWrapper<>(0, 0, 0, 0, List.of());
            PageResponse<String> response = PageResponse.ok(wrapper);

            assertEquals("成功", response.getMessage());
        }

        @Test
        @DisplayName("ok 设置 data 正确")
        void okData() {
            List<String> items = List.of("alert1", "alert2");
            DataWrapper<String> wrapper = new DataWrapper<>(2, 1, 0, 1, items);
            PageResponse<String> response = PageResponse.ok(wrapper);

            assertNotNull(response.getData());
            assertEquals(2, response.getData().getTotal());
            assertEquals(2, response.getData().getAlerts().size());
        }

        @Test
        @DisplayName("ok 空列表")
        void okEmptyList() {
            DataWrapper<String> wrapper = new DataWrapper<>(0, 0, 0, 0, List.of());
            PageResponse<String> response = PageResponse.ok(wrapper);

            assertTrue(response.isSuccess());
            assertEquals(0, response.getData().getTotal());
            assertTrue(response.getData().getAlerts().isEmpty());
        }
    }

    @Nested
    @DisplayName("fail() 工厂方法")
    class FailTests {

        @Test
        @DisplayName("fail 返回 success=false")
        void failSuccessFalse() {
            PageResponse<String> response = PageResponse.fail("查询失败");

            assertFalse(response.isSuccess());
        }

        @Test
        @DisplayName("fail 设置 message 正确")
        void failMessage() {
            PageResponse<String> response = PageResponse.fail("数据库连接超时");

            assertEquals("数据库连接超时", response.getMessage());
        }

        @Test
        @DisplayName("fail 的 data 为 null")
        void failDataNull() {
            PageResponse<String> response = PageResponse.fail("错误");

            assertNull(response.getData());
        }
    }

    @Nested
    @DisplayName("DataWrapper 内部类")
    class DataWrapperTests {

        @Test
        @DisplayName("无参构造函数 - 所有字段为默认值")
        void noArgsConstructor() {
            DataWrapper<String> wrapper = new DataWrapper<>();

            assertEquals(0, wrapper.getTotal());
            assertEquals(0, wrapper.getPending());
            assertEquals(0, wrapper.getProcessing());
            assertEquals(0, wrapper.getResolved());
            assertNull(wrapper.getAlerts());
        }

        @Test
        @DisplayName("全参构造函数 - 所有字段正确赋值")
        void allArgsConstructor() {
            List<String> alerts = List.of("a", "b", "c");
            DataWrapper<String> wrapper = new DataWrapper<>(100, 50, 30, 20, alerts);

            assertEquals(100, wrapper.getTotal());
            assertEquals(50, wrapper.getPending());
            assertEquals(30, wrapper.getProcessing());
            assertEquals(20, wrapper.getResolved());
            assertEquals(3, wrapper.getAlerts().size());
        }

        @Test
        @DisplayName("setter 正常工作")
        void settersWork() {
            DataWrapper<String> wrapper = new DataWrapper<>();
            wrapper.setTotal(10);
            wrapper.setPending(5);
            wrapper.setProcessing(3);
            wrapper.setResolved(2);
            wrapper.setAlerts(List.of("x"));

            assertEquals(10, wrapper.getTotal());
            assertEquals(5, wrapper.getPending());
            assertEquals(3, wrapper.getProcessing());
            assertEquals(2, wrapper.getResolved());
            assertEquals(1, wrapper.getAlerts().size());
        }
    }

    @Nested
    @DisplayName("通用泛型")
    class GenericTests {

        @Test
        @DisplayName("ok 支持不同类型")
        void okDifferentTypes() {
            DataWrapper<Integer> intWrapper = new DataWrapper<>(1, 0, 0, 1, List.of(42));
            PageResponse<Integer> intResponse = PageResponse.ok(intWrapper);
            assertTrue(intResponse.isSuccess());

            DataWrapper<Object> objWrapper = new DataWrapper<>(0, 0, 0, 0, List.of());
            PageResponse<Object> objResponse = PageResponse.ok(objWrapper);
            assertTrue(objResponse.isSuccess());
        }
    }
}
