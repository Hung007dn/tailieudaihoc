package com.example.todolist;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.redirectedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.view;

@SpringBootTest
@AutoConfigureMockMvc
@DirtiesContext(classMode = DirtiesContext.ClassMode.BEFORE_EACH_TEST_METHOD)
class TodolistApplicationTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void listPageLoads() throws Exception {
        mockMvc.perform(get("/todos"))
                .andExpect(status().isOk())
                .andExpect(view().name("todos/list"))
                .andExpect(model().attributeExists("todos"));
    }

    @Test
    void blankTitleReturnsValidationError() throws Exception {
        mockMvc.perform(post("/todos")
                        .param("title", "")
                        .param("description", "Missing title"))
                .andExpect(status().isOk())
                .andExpect(view().name("todos/form"))
                .andExpect(model().attributeHasFieldErrors("todo", "title"));

        mockMvc.perform(get("/api/v1/todos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void createUpdateAndDeleteTodo() throws Exception {
        mockMvc.perform(post("/todos")
                        .param("title", "Finish Lab 1")
                        .param("description", "Build the Thymeleaf application")
                        .param("dueDate", "2026-09-25"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/todos"));

        mockMvc.perform(post("/todos/{id}", 1)
                        .param("title", "Finish Lab 1")
                        .param("description", "CRUD is working")
                        .param("dueDate", "2026-09-26")
                        .param("completed", "true"))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/todos"));

        mockMvc.perform(get("/todos"))
                .andExpect(status().isOk())
                .andExpect(content().string(org.hamcrest.Matchers.containsString("Completed")))
                .andExpect(content().string(org.hamcrest.Matchers.containsString("CRUD is working")));

        mockMvc.perform(post("/todos/{id}/delete", 1))
                .andExpect(status().is3xxRedirection())
                .andExpect(redirectedUrl("/todos"));

        mockMvc.perform(get("/api/v1/todos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void restApiCreateListUpdateAndDeleteTodo() throws Exception {
        mockMvc.perform(post("/api/v1/todos")
                        .contentType("application/json")
                        .content("""
                                {
                                  "title": "Buy milk",
                                  "description": "2 liters",
                                  "dueDate": "2026-09-25",
                                  "completed": false
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.title").value("Buy milk"))
                .andExpect(jsonPath("$.completed").value(false));

        mockMvc.perform(get("/api/v1/todos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value(1))
                .andExpect(jsonPath("$[0].title").value("Buy milk"));

        mockMvc.perform(put("/api/v1/todos/{id}", 1)
                        .contentType("application/json")
                        .content("""
                                {
                                  "title": "Buy milk",
                                  "description": "Bought at the corner store",
                                  "dueDate": "2026-09-26",
                                  "completed": true
                                }
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.description").value("Bought at the corner store"))
                .andExpect(jsonPath("$.completed").value(true));

        mockMvc.perform(get("/todos"))
                .andExpect(status().isOk())
                .andExpect(content().string(org.hamcrest.Matchers.containsString("Bought at the corner store")))
                .andExpect(content().string(org.hamcrest.Matchers.containsString("Completed")));

        mockMvc.perform(delete("/api/v1/todos/{id}", 1))
                .andExpect(status().isOk());

        mockMvc.perform(get("/api/v1/todos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void restApiBlankTitleReturnsValidationError() throws Exception {
        mockMvc.perform(post("/api/v1/todos")
                        .contentType("application/json")
                        .content("""
                                {
                                  "title": "",
                                  "description": "Missing title"
                                }
                                """))
                .andExpect(status().isBadRequest());

        mockMvc.perform(get("/api/v1/todos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    void restApiNotFoundReturnsJson404() throws Exception {
        mockMvc.perform(get("/api/v1/todos/10000"))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.error").value("NOT_FOUND"))
                .andExpect(jsonPath("$.message").value("Todo not found with id: 10000"));
    }

    @Test
    void restApiV2ShowsVersionedResponseShape() throws Exception {
        mockMvc.perform(post("/api/v1/todos")
                        .contentType("application/json")
                        .content("""
                                {
                                  "title": "Versioned todo"
                                }
                                """))
                .andExpect(status().isOk());

        mockMvc.perform(get("/api/v2/todos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.version").value("v2"))
                .andExpect(jsonPath("$.count").value(1))
                .andExpect(jsonPath("$.items[0].title").value("Versioned todo"));
    }
}
