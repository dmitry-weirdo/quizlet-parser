package com.quizlet.parser.templates;

import java.util.List;

public record CardTemplate(
        String id,
        List<String> required,
        String question,
        String answer,
        List<String> relations
) {
    public CardTemplate {
        relations = relations != null ? List.copyOf(relations) : List.of();
        required = required != null ? List.copyOf(required) : List.of();
    }
}
