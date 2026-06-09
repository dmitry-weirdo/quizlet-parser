package com.quizlet.parser.examples;

import com.quizlet.parser.model.Card;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class CardMatcher {

    public enum Mode {
        STRICT,
        CONTAINS
    }

    private CardMatcher() {
    }

    public static MatchResult compare(List<Card> expected, List<Card> actual, Mode mode) {
        Set<String> expectedKeys = toKeys(expected);
        Set<String> actualKeys = toKeys(actual);

        List<Card> missing = new ArrayList<>();
        for (Card card : expected) {
            if (!actualKeys.contains(key(card))) {
                missing.add(card);
            }
        }

        List<Card> extra = new ArrayList<>();
        if (mode == Mode.STRICT) {
            for (Card card : actual) {
                if (!expectedKeys.contains(key(card))) {
                    extra.add(card);
                }
            }
        }

        boolean passed = missing.isEmpty() && (mode != Mode.STRICT || extra.isEmpty());
        return new MatchResult(passed, missing, extra, actual);
    }

    private static Set<String> toKeys(List<Card> cards) {
        Set<String> keys = new HashSet<>();
        for (Card card : cards) {
            keys.add(key(card));
        }
        return keys;
    }

    private static String key(Card card) {
        return normalize(card.question()) + "\u0000" + normalize(card.answer());
    }

    private static String normalize(String value) {
        return value == null ? "" : value.replaceAll("\\s+", " ").trim();
    }

    public record MatchResult(
            boolean passed,
            List<Card> missing,
            List<Card> extra,
            List<Card> actual
    ) {
    }
}
