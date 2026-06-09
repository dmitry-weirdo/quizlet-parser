package com.quizlet.parser.model;

import java.util.Objects;

public record Card(String question, String answer) {

    public Card {
        Objects.requireNonNull(question, "question");
        Objects.requireNonNull(answer, "answer");
    }
}
