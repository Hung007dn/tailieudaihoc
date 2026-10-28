package com.example.roombooking.service;

import com.example.roombooking.dto.BookingFormDto;
import com.example.roombooking.model.Booking;
import com.example.roombooking.model.BookingStatus;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;
import org.springframework.validation.BindingResult;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class BookingService {

    // In-memory data store using ArrayList as required
    private final List<Booking> bookings = new ArrayList<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    @PostConstruct
    public void initSampleData() {
        LocalDateTime tomorrow = LocalDateTime.now().plusDays(1).truncatedTo(ChronoUnit.HOURS);
        
        // Sample 1: Room A101 tomorrow 09:00 - 10:00 (Can be cancelled, can test overlap)
        bookings.add(new Booking(
                idGenerator.getAndIncrement(),
                "A101",
                "Nguyen Van A",
                tomorrow.withHour(9).withMinute(0),
                tomorrow.withHour(10).withMinute(0),
                "Họp phòng ban kỹ thuật",
                BookingStatus.CONFIRMED
        ));

        // Sample 2: Room B202 tomorrow 14:00 - 15:00
        bookings.add(new Booking(
                idGenerator.getAndIncrement(),
                "B202",
                "Nguyen Van A",
                tomorrow.withHour(14).withMinute(0),
                tomorrow.withHour(15).withMinute(0),
                "Phỏng vấn ứng viên",
                BookingStatus.CONFIRMED
        ));

        // Sample 3: Room C303 starts in 15 minutes (Used to test Cancel Too Late rule)
        LocalDateTime nearNow = LocalDateTime.now().plusMinutes(15).truncatedTo(ChronoUnit.MINUTES);
        bookings.add(new Booking(
                idGenerator.getAndIncrement(),
                "C303",
                "Tran Thi B",
                nearNow,
                nearNow.plusMinutes(60),
                "Thảo luận khẩn cấp",
                BookingStatus.CONFIRMED
        ));
    }

    public List<Booking> getAllBookings() {
        return new ArrayList<>(bookings);
    }

    public Optional<Booking> getBookingById(Long id) {
        return bookings.stream()
                .filter(b -> b.getId().equals(id))
                .findFirst();
    }

    public Booking createBooking(BookingFormDto dto) {
        Booking booking = new Booking();
        booking.setId(idGenerator.getAndIncrement());
        booking.setRoomName(dto.getRoomName().trim());
        booking.setBookedBy(dto.getBookedBy().trim());
        booking.setStartAt(dto.getStartAt());
        booking.setEndAt(dto.getEndAt());
        booking.setPurpose(dto.getPurpose().trim());
        booking.setStatus(BookingStatus.CONFIRMED);

        bookings.add(booking);
        return booking;
    }

    public boolean updateBooking(Long id, BookingFormDto dto) {
        Optional<Booking> optionalBooking = getBookingById(id);
        if (optionalBooking.isEmpty()) {
            return false;
        }

        Booking booking = optionalBooking.get();
        if (booking.getStatus() == BookingStatus.CANCELLED) {
            return false; // Cannot edit cancelled booking
        }

        booking.setRoomName(dto.getRoomName().trim());
        booking.setBookedBy(dto.getBookedBy().trim());
        booking.setStartAt(dto.getStartAt());
        booking.setEndAt(dto.getEndAt());
        booking.setPurpose(dto.getPurpose().trim());
        return true;
    }

    /**
     * Cancel booking policy:
     * - Only cancel when at least 30 minutes remain before startAt
     * - Status changed to CANCELLED (record is not deleted)
     * @return null if successful, or error message string if refused
     */
    public String cancelBooking(Long id) {
        Optional<Booking> optionalBooking = getBookingById(id);
        if (optionalBooking.isEmpty()) {
            return "Không tìm thấy thông tin đặt phòng cần hủy.";
        }

        Booking booking = optionalBooking.get();
        if (booking.getStatus() == BookingStatus.CANCELLED) {
            return "Đặt phòng này đã bị hủy trước đó.";
        }

        LocalDateTime now = LocalDateTime.now();
        long minutesUntilStart = Duration.between(now, booking.getStartAt()).toMinutes();

        if (minutesUntilStart < 30) {
            return "Từ chối hủy: Chỉ được phép hủy phòng trước thời gian bắt đầu ít nhất 30 phút. (Thời gian còn lại: " 
                    + (minutesUntilStart < 0 ? "đã qua giờ bắt đầu" : minutesUntilStart + " phút") + ").";
        }

        booking.setStatus(BookingStatus.CANCELLED);
        return null; // Success
    }

    /**
     * Validates business policies and binds failures directly to the field to correct.
     */
    public void validateBusinessRules(BookingFormDto dto, Long currentBookingId, BindingResult result) {
        LocalDateTime startAt = dto.getStartAt();
        LocalDateTime endAt = dto.getEndAt();

        // 1. Start must not lie in the past
        if (startAt != null && startAt.isBefore(LocalDateTime.now())) {
            result.rejectValue("startAt", "startAt.past", "Thời gian bắt đầu không được ở trong quá khứ.");
        }

        // 2. End date-time must be strictly after its start
        if (startAt != null && endAt != null) {
            if (!endAt.isAfter(startAt)) {
                result.rejectValue("endAt", "endAt.notAfterStart", "Thời gian kết thúc phải sau thời gian bắt đầu.");
            } else {
                // 3. Single booking may last at most 120 minutes
                long durationMinutes = Duration.between(startAt, endAt).toMinutes();
                if (durationMinutes > 120) {
                    result.rejectValue("endAt", "endAt.tooLong", "Thời lượng đặt phòng tối đa là 120 phút (hiện tại: " + durationMinutes + " phút).");
                }
            }
        }

        // 4. Same-room overlap check (only for CONFIRMED bookings; CANCELLED bookings are ignored)
        if (dto.getRoomName() != null && !dto.getRoomName().isBlank() && startAt != null && endAt != null && endAt.isAfter(startAt)) {
            String targetRoom = dto.getRoomName().trim();
            boolean hasOverlap = bookings.stream()
                    .filter(b -> currentBookingId == null || !b.getId().equals(currentBookingId))
                    .filter(b -> b.getStatus() == BookingStatus.CONFIRMED)
                    .filter(b -> b.getRoomName().equalsIgnoreCase(targetRoom))
                    .anyMatch(b -> startAt.isBefore(b.getEndAt()) && endAt.isAfter(b.getStartAt()));

            if (hasOverlap) {
                result.rejectValue("roomName", "roomName.overlap", "Phòng " + targetRoom + " đã có người đặt trong khoảng thời gian này.");
            }
        }

        // 5. One person (bookedBy) may hold at most two CONFIRMED bookings at a time
        if (dto.getBookedBy() != null && !dto.getBookedBy().isBlank()) {
            String targetPerson = dto.getBookedBy().trim();
            long confirmedCount = bookings.stream()
                    .filter(b -> currentBookingId == null || !b.getId().equals(currentBookingId))
                    .filter(b -> b.getStatus() == BookingStatus.CONFIRMED)
                    .filter(b -> b.getBookedBy().equalsIgnoreCase(targetPerson))
                    .count();

            if (confirmedCount >= 2) {
                result.rejectValue("bookedBy", "bookedBy.limitExceeded", "Người đặt '" + targetPerson + "' đã giữ tối đa 2 lượt đặt phòng CONFIRMED.");
            }
        }
    }
}
