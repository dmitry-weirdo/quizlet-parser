package com.quizlet.parser.telegram;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.ArrayList;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class TelegramExport {

    private String name;
    private String type;
    private Long id;
    private List<TelegramMessage> messages = new ArrayList<>();

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public List<TelegramMessage> getMessages() {
        return messages;
    }

    public void setMessages(List<TelegramMessage> messages) {
        this.messages = messages != null ? messages : new ArrayList<>();
    }
}
