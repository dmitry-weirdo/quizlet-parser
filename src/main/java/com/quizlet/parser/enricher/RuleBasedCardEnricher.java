package com.quizlet.parser.enricher;

import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.FactType;
import com.quizlet.parser.model.StructuredFact;

import java.util.ArrayList;
import java.util.List;

public final class RuleBasedCardEnricher implements CardEnricher {

    @Override
    public List<Card> enrich(StructuredFact fact) {
        List<Card> cards = new ArrayList<>();

        if (Boolean.TRUE.equals(parseBoolean(fact.getExtra().get("clickable")))
                || fact.getExtra().containsKey("clickHint")) {
            String hint = fact.getExtra().getOrDefault("clickHint", fact.getHint());
            String subject = firstNonBlank(fact.getName(), fact.getTerm(), fact.getTitle(), fact.getAlias());
            if (hint != null && subject != null) {
                cards.add(new Card(
                        subject,
                        "Какой " + roleForType(fact.getType()) + " должен щёлкать на " + hint + "?"
                ));
            }
        }

        if (fact.getAnswerHint() != null && !fact.getAnswerHint().isBlank()) {
            String term = firstNonBlank(fact.getTerm(), fact.getName(), fact.getTitle(), fact.getAlias());
            String definition = firstNonBlank(fact.getFact(), fact.getMeaning(), fact.getHint());
            if (term != null && definition != null) {
                cards.add(new Card(term, definition + " " + fact.getAnswerHint()));
            }
        }

        return cards;
    }

    private static String roleForType(FactType type) {
        return switch (type) {
            case PERSON -> "человек";
            case ARTWORK -> "произведение";
            case LOCATION -> "место";
            case TERM -> "термин";
            default -> "ответ";
        };
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.isBlank()) {
                return value;
            }
        }
        return null;
    }

    private static Boolean parseBoolean(String value) {
        if (value == null) {
            return false;
        }
        return "true".equalsIgnoreCase(value) || "1".equals(value);
    }
}
