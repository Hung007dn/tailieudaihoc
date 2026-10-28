package com.example.todolist.service;

import com.example.todolist.dto.TodoRequest;
import com.example.todolist.exception.TodoNotFoundException;
import com.example.todolist.model.Todo;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class TodoService {

    private final List<Todo> store = new ArrayList<>();
    private final AtomicLong sequence = new AtomicLong(1);

    public List<Todo> findAll() {
        return new ArrayList<>(store);
    }

    public Todo findById(Long id) {
        return store.stream()
                .filter(todo -> todo.getId().equals(id))
                .findFirst()
                .orElseThrow(() -> new TodoNotFoundException(id));
    }

    public Todo create(TodoRequest request) {
        Todo todo = new Todo(
                sequence.getAndIncrement(),
                request.getTitle(),
                request.getDescription(),
                request.getDueDate(),
                request.isCompleted()
        );
        store.add(todo);
        return todo;
    }

    public Todo update(Long id, TodoRequest request) {
        Todo todo = findById(id);
        todo.setTitle(request.getTitle());
        todo.setDescription(request.getDescription());
        todo.setDueDate(request.getDueDate());
        todo.setCompleted(request.isCompleted());
        return todo;
    }

    public void deleteById(Long id) {
        store.remove(findById(id));
    }
}
