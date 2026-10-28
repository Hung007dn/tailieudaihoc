package com.example.roombooking.controller;

import com.example.roombooking.dto.BookingFormDto;
import com.example.roombooking.model.Booking;
import com.example.roombooking.model.BookingStatus;
import com.example.roombooking.service.BookingService;
import jakarta.validation.Valid;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.Optional;

@Controller
@RequestMapping("/bookings")
public class BookingController {

    private final BookingService bookingService;

    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    @GetMapping
    public String listBookings(@RequestParam(value = "cancelError", required = false) String cancelError,
                               @RequestParam(value = "cancelSuccess", required = false) String cancelSuccess,
                               Model model) {
        model.addAttribute("bookings", bookingService.getAllBookings());
        if (cancelError != null) {
            model.addAttribute("cancelError", cancelError);
        }
        if (cancelSuccess != null) {
            model.addAttribute("cancelSuccess", cancelSuccess);
        }
        return "bookings/list";
    }

    @GetMapping("/new")
    public String showCreateForm(Model model) {
        if (!model.containsAttribute("bookingFormDto")) {
            model.addAttribute("bookingFormDto", new BookingFormDto());
        }
        model.addAttribute("isEdit", false);
        return "bookings/form";
    }

    @PostMapping
    public String createBooking(@Valid @ModelAttribute("bookingFormDto") BookingFormDto bookingFormDto,
                                BindingResult bindingResult,
                                Model model,
                                RedirectAttributes redirectAttributes) {
        // Enforce business rules
        bookingService.validateBusinessRules(bookingFormDto, null, bindingResult);

        if (bindingResult.hasErrors()) {
            model.addAttribute("isEdit", false);
            // Stay on the form page, do not redirect, retain entered values, display errors beside fields
            return "bookings/form";
        }

        bookingService.createBooking(bookingFormDto);
        redirectAttributes.addFlashAttribute("successMessage", "Đặt phòng thành công!");
        return "redirect:/bookings";
    }

    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable("id") Long id, Model model, RedirectAttributes redirectAttributes) {
        Optional<Booking> optionalBooking = bookingService.getBookingById(id);
        if (optionalBooking.isEmpty()) {
            redirectAttributes.addFlashAttribute("errorMessage", "Không tìm thấy booking ID: " + id);
            return "redirect:/bookings";
        }

        Booking booking = optionalBooking.get();
        if (booking.getStatus() == BookingStatus.CANCELLED) {
            redirectAttributes.addFlashAttribute("errorMessage", "Không thể chỉnh sửa booking đã bị hủy!");
            return "redirect:/bookings";
        }

        if (!model.containsAttribute("bookingFormDto")) {
            BookingFormDto dto = new BookingFormDto(
                    booking.getRoomName(),
                    booking.getBookedBy(),
                    booking.getStartAt(),
                    booking.getEndAt(),
                    booking.getPurpose()
            );
            model.addAttribute("bookingFormDto", dto);
        }

        model.addAttribute("isEdit", true);
        model.addAttribute("bookingId", id);
        return "bookings/form";
    }

    @PostMapping("/{id}/edit")
    public String updateBooking(@PathVariable("id") Long id,
                                @Valid @ModelAttribute("bookingFormDto") BookingFormDto bookingFormDto,
                                BindingResult bindingResult,
                                Model model,
                                RedirectAttributes redirectAttributes) {
        // Enforce business rules against other existing bookings
        bookingService.validateBusinessRules(bookingFormDto, id, bindingResult);

        if (bindingResult.hasErrors()) {
            model.addAttribute("isEdit", true);
            model.addAttribute("bookingId", id);
            return "bookings/form";
        }

        boolean updated = bookingService.updateBooking(id, bookingFormDto);
        if (!updated) {
            redirectAttributes.addFlashAttribute("errorMessage", "Cập nhật thất bại. Booking không tồn tại hoặc đã bị hủy.");
            return "redirect:/bookings";
        }

        redirectAttributes.addFlashAttribute("successMessage", "Cập nhật đặt phòng thành công!");
        return "redirect:/bookings";
    }

    @PostMapping("/{id}/cancel")
    public String cancelBooking(@PathVariable("id") Long id, RedirectAttributes redirectAttributes) {
        String errorMsg = bookingService.cancelBooking(id);
        if (errorMsg != null) {
            // Cancel refused: remain on list page and show the message there
            redirectAttributes.addFlashAttribute("cancelError", errorMsg);
        } else {
            redirectAttributes.addFlashAttribute("cancelSuccess", "Hủy đặt phòng #" + id + " thành công!");
        }
        return "redirect:/bookings";
    }
}
