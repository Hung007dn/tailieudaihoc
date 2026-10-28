package com.example.todolist.controller.api.v2;

import com.example.todolist.model.Todo;
import com.example.todolist.service.TodoService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController("v2TodoRestController")
@RequestMapping("/api/v2/todos")
public class TodoRestController {

    private final TodoService todoService;

    public TodoRestController(TodoService todoService) {
        this.todoService = todoService;
    }

    @GetMapping
    public Map<String, Object> list() {
        List<Todo> todos = todoService.findAll();
        return Map.of(
                "version", "v2",
                "count", todos.size(),
                "items", todos
        );
    }
}
