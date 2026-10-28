package com.example.roombooking.service;

import com.example.roombooking.dto.BookingFormDto;
import com.example.roombooking.model.Booking;
import com.example.roombooking.model.BookingStatus;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.BindingResult;

import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

class BookingServiceTest {

    private BookingService bookingService;

    @BeforeEach
    void setUp() {
        bookingService = new BookingService();
        // Clear or re-init
        bookingService.initSampleData();
    }

    @Test
    @DisplayName("Rule 1: Start must not lie in the past")
    void testStartInPast_ShouldFail() {
        LocalDateTime past = LocalDateTime.now().minusHours(2);
        BookingFormDto dto = new BookingFormDto("A101", "UserTest", past, past.plusMinutes(60), "Testing past");
        BindingResult result = new BeanPropertyBindingResult(dto, "bookingFormDto");

        bookingService.validateBusinessRules(dto, null, result);

        assertTrue(result.hasFieldErrors("startAt"), "Phải có lỗi ở trường startAt khi thời gian ở quá khứ");
    }

    @Test
    @DisplayName("Rule 2: End date-time must be strictly after start")
    void testEndBeforeStart_ShouldFail() {
        LocalDateTime future = LocalDateTime.now().plusDays(2);
        BookingFormDto dto = new BookingFormDto("A101", "UserTest", future, future.minusMinutes(30), "End before start");
        BindingResult result = new BeanPropertyBindingResult(dto, "bookingFormDto");

        bookingService.validateBusinessRules(dto, null, result);

        assertTrue(result.hasFieldErrors("endAt"), "Phải có lỗi ở trường endAt khi endAt <= startAt");
    }

    @Test
    @DisplayName("Rule 3: Duration too long (over 120 minutes)")
    void testDurationTooLong_ShouldFail() {
        LocalDateTime future = LocalDateTime.now().plusDays(2);
        BookingFormDto dto = new BookingFormDto("A101", "UserTest", future, future.plusMinutes(125), "Duration > 120m");
        BindingResult result = new BeanPropertyBindingResult(dto, "bookingFormDto");

        bookingService.validateBusinessRules(dto, null, result);

        assertTrue(result.hasFieldErrors("endAt"), "Phải có lỗi ở trường endAt khi thời lượng > 120 phút");
    }

    @Test
    @DisplayName("Rule 4: Same-room overlap in CONFIRMED status must be rejected")
    void testSameRoomOverlap_ShouldFail() {
        // Room A101 tomorrow 09:00 - 10:00 already exists in sample data
        LocalDateTime tomorrow = LocalDateTime.now().plusDays(1);
        LocalDateTime overlapStart = tomorrow.withHour(9).withMinute(30);
        LocalDateTime overlapEnd = tomorrow.withHour(10).withMinute(30);

        BookingFormDto dto = new BookingFormDto("A101", "UserOther", overlapStart, overlapEnd, "Overlapping A101");
        BindingResult result = new BeanPropertyBindingResult(dto, "bookingFormDto");

        bookingService.validateBusinessRules(dto, null, result);

        assertTrue(result.hasFieldErrors("roomName"), "Phải có lỗi trùng phòng ở roomName");
    }

    @Test
    @DisplayName("Rule 5: Different room at the same time is ALLOWED")
    void testDifferentRoomSameTime_ShouldPass() {
        LocalDateTime tomorrow = LocalDateTime.now().plusDays(1);
        LocalDateTime sameStart = tomorrow.withHour(9).withMinute(0);
        LocalDateTime sameEnd = tomorrow.withHour(10).withMinute(0);

        BookingFormDto dto = new BookingFormDto("D404", "UserOther", sameStart, sameEnd, "Different room same time");
        BindingResult result = new BeanPropertyBindingResult(dto, "bookingFormDto");

        bookingService.validateBusinessRules(dto, null, result);

        assertFalse(result.hasErrors(), "Khác phòng cùng giờ phải hợp lệ, không có lỗi");
    }

    @Test
    @DisplayName("Rule 6: A person may hold at most two CONFIRMED bookings")
    void testThirdBookingBySamePerson_ShouldFail() {
        // "Nguyen Van A" already has 2 bookings in sample data
        LocalDateTime future = LocalDateTime.now().plusDays(3);
        BookingFormDto dto = new BookingFormDto("D404", "Nguyen Van A", future, future.plusMinutes(60), "Third booking attempt");
        BindingResult result = new BeanPropertyBindingResult(dto, "bookingFormDto");

        bookingService.validateBusinessRules(dto, null, result);

        assertTrue(result.hasFieldErrors("bookedBy"), "Phải báo lỗi ở bookedBy khi người này đã có 2 booking CONFIRMED");
    }

    @Test
    @DisplayName("Rule 7: Cancel too late (< 30 minutes before start) must be refused")
    void testCancelTooLate_ShouldBeRefused() {
        // Sample 3 (C303) starts in 15 minutes (< 30 minutes)
        Booking sample3 = bookingService.getAllBookings().stream()
                .filter(b -> b.getRoomName().equals("C303"))
                .findFirst().orElseThrow();

        String error = bookingService.cancelBooking(sample3.getId());

        assertNotNull(error, "Phải trả về thông báo từ chối hủy khi còn dưới 30 phút");
        assertEquals(BookingStatus.CONFIRMED, sample3.getStatus(), "Trạng thái vẫn phải là CONFIRMED");
    }

    @Test
    @DisplayName("Rule 8: Cancel in time (>= 30 minutes before start) must succeed")
    void testCancelInTime_ShouldSucceed() {
        // Sample 1 (A101) starts tomorrow (> 30 minutes)
        Booking sample1 = bookingService.getAllBookings().stream()
                .filter(b -> b.getRoomName().equals("A101"))
                .findFirst().orElseThrow();

        String error = bookingService.cancelBooking(sample1.getId());

        assertNull(error, "Hủy hợp lệ phải trả về null (thành công)");
        assertEquals(BookingStatus.CANCELLED, sample1.getStatus(), "Trạng thái phải chuyển thành CANCELLED");
    }

    @Test
    @DisplayName("Rule 9: Overlap is ignored for CANCELLED bookings (Freed slot reuse)")
    void testReuseFreedSlotOfCancelledBooking() {
        // First cancel Sample 1 (A101 tomorrow 09:00 - 10:00)
        Booking sample1 = bookingService.getAllBookings().stream()
                .filter(b -> b.getRoomName().equals("A101"))
                .findFirst().orElseThrow();
        bookingService.cancelBooking(sample1.getId());

        // Now book the exact same slot for A101
        BookingFormDto dto = new BookingFormDto("A101", "NewPerson", sample1.getStartAt(), sample1.getEndAt(), "Rebooking freed slot");
        BindingResult result = new BeanPropertyBindingResult(dto, "bookingFormDto");

        bookingService.validateBusinessRules(dto, null, result);

        assertFalse(result.hasErrors(), "Đặt lại khung giờ của booking đã CANCELLED phải thành công");
    }
}
