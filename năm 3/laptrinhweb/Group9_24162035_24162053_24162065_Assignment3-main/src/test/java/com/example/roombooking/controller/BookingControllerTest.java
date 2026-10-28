package com.example.roombooking.controller;

import com.example.roombooking.service.BookingService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class BookingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private BookingService bookingService;

    @Test
    @DisplayName("GET /bookings - Hiển thị danh sách booking và các cột theo quy định")
    void testGetBookingsList() throws Exception {
        mockMvc.perform(get("/bookings"))
                .andExpect(status().isOk())
                .andExpect(view().name("bookings/list"))
                .andExpect(model().attributeExists("bookings"))
                .andExpect(content().string(containsString("Quản Lý Đặt Phòng Họp")))
                .andExpect(content().string(containsString("Tên Phòng")))
                .andExpect(content().string(containsString("Người Đặt")))
                .andExpect(content().string(containsString("Bắt Đầu")))
                .andExpect(content().string(containsString("Kết Thúc")))
                .andExpect(content().string(containsString("Mục Đích")))
                .andExpect(content().string(containsString("Trạng Thái")))
                .andExpect(content().string(containsString("Hành Động")));
    }

    @Test
    @DisplayName("GET /bookings/new - Hiển thị form tạo mới")
    void testGetNewBookingForm() throws Exception {
        mockMvc.perform(get("/bookings/new"))
                .andExpect(status().isOk())
                .andExpect(view().name("bookings/form"))
                .andExpect(model().attributeExists("bookingFormDto"))
                .andExpect(model().attribute("isEdit", false))
                .andExpect(content().string(containsString("Tạo Mới Đặt Phòng")));
    }

    @Test
    @DisplayName("POST /bookings rỗng - Báo lỗi cạnh từng field, không reset trắng form, giữ lại dữ liệu")
    void testPostEmptyForm_ShouldShowFieldErrorsAndRetainInputs() throws Exception {
        mockMvc.perform(post("/bookings")
                        .param("roomName", "")
                        .param("bookedBy", "Nguyen Van B") // partial input
                        .param("purpose", "")
                )
                .andExpect(status().isOk())
                .andExpect(view().name("bookings/form"))
                .andExpect(model().attributeHasFieldErrors("bookingFormDto", "roomName", "startAt", "endAt", "purpose"))
                // Ensure the entered bookedBy is retained and not reset
                .andExpect(model().attribute("bookingFormDto", hasProperty("bookedBy", equalTo("Nguyen Van B"))))
                .andExpect(content().string(containsString("value=\"Nguyen Van B\"")))
                // Ensure error messages exist beside fields
                .andExpect(content().string(containsString("Tên phòng không được để trống")))
                .andExpect(content().string(containsString("Thời gian bắt đầu không được để trống")))
                .andExpect(content().string(containsString("Thời gian kết thúc không được để trống")))
                .andExpect(content().string(containsString("Mục đích sử dụng không được để trống")));
    }

    @Test
    @DisplayName("POST /bookings hợp lệ - Tạo mới thành công và chuyển hướng về danh sách")
    void testCreateBookingSuccess() throws Exception {
        LocalDateTime future = LocalDateTime.now().plusDays(5).withHour(10).withMinute(0);
        mockMvc.perform(post("/bookings")
                        .param("roomName", "E505")
                        .param("bookedBy", "Test Creator")
                        .param("startAt", future.toString().substring(0, 16))
                        .param("endAt", future.plusMinutes(45).toString().substring(0, 16))
                        .param("purpose", "Họp đồ án test controller")
                )
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/bookings"))
                .andExpect(flash().attribute("successMessage", "Đặt phòng thành công!"));
    }

    @Test
    @DisplayName("POST /bookings/{id}/cancel quá sát giờ (< 30p) - Từ chối hủy, hiển thị thông báo đỏ")
    void testCancelTooLate_RedirectsWithCancelError() throws Exception {
        // Sample 3 (C303) starts in 15 minutes (< 30 minutes)
        mockMvc.perform(post("/bookings/3/cancel"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/bookings"))
                .andExpect(flash().attributeExists("cancelError"));
    }

    @Test
    @DisplayName("POST /bookings/{id}/cancel hợp lệ (> 30p) - Hủy thành công, hiển thị thông báo xanh")
    void testCancelInTime_RedirectsWithCancelSuccess() throws Exception {
        // Sample 2 (B202) is tomorrow (> 30 minutes)
        mockMvc.perform(post("/bookings/2/cancel"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/bookings"))
                .andExpect(flash().attribute("cancelSuccess", "Hủy đặt phòng #2 thành công!"));
    }

    @Test
    @DisplayName("GET /bookings/{id}/edit khi booking đã CANCELLED - Bị chặn và báo lỗi")
    void testEditCancelledBooking_Blocked() throws Exception {
        // Ensure a booking is CANCELLED first
        bookingService.cancelBooking(1L);

        mockMvc.perform(get("/bookings/1/edit"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/bookings"))
                .andExpect(flash().attribute("errorMessage", "Không thể chỉnh sửa booking đã bị hủy!"));
    }
}
