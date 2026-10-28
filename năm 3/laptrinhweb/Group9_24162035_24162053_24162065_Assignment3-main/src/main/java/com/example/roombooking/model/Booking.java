package com.example.roombooking.model;

import java.time.LocalDateTime;

public class Booking {
    private Long id;
    private String roomName;
    private String bookedBy;
    private LocalDateTime startAt;
    private LocalDateTime endAt;
    private String purpose;
    private BookingStatus status;

    public Booking() {
        this.status = BookingStatus.CONFIRMED;
    }

    public Booking(Long id, String roomName, String bookedBy, LocalDateTime startAt, LocalDateTime endAt, String purpose, BookingStatus status) {
        this.id = id;
        this.roomName = roomName;
        this.bookedBy = bookedBy;
        this.startAt = startAt;
        this.endAt = endAt;
        this.purpose = purpose;
        this.status = (status != null) ? status : BookingStatus.CONFIRMED;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getRoomName() {
        return roomName;
    }

    public void setRoomName(String roomName) {
        this.roomName = roomName;
    }

    public String getBookedBy() {
        return bookedBy;
    }

    public void setBookedBy(String bookedBy) {
        this.bookedBy = bookedBy;
    }

    public LocalDateTime getStartAt() {
        return startAt;
    }

    public void setStartAt(LocalDateTime startAt) {
        this.startAt = startAt;
    }

    public LocalDateTime getEndAt() {
        return endAt;
    }

    public void setEndAt(LocalDateTime endAt) {
        this.endAt = endAt;
    }

    public String getPurpose() {
        return purpose;
    }

    public void setPurpose(String purpose) {
        this.purpose = purpose;
    }

    public BookingStatus getStatus() {
        return status;
    }

    public void setStatus(BookingStatus status) {
        this.status = status;
    }
}
