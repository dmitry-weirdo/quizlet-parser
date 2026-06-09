package com.quizlet.parser.examples;

import com.quizlet.parser.model.Card;

import java.util.List;

public record GenerationResult(
        List<Card> cards,
        List<SourceCardGroup> groups
) {
}
