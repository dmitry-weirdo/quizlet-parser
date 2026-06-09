package com.quizlet.parser.examples;

import com.quizlet.parser.model.StructuredFact;

import java.util.Map;

public final class FactTextRenderer {

    private FactTextRenderer() {
    }

    public static String render(StructuredFact fact) {
        if (fact == null) {
            return "";
        }
        Map<String, String> fields = fact.asFieldMap();
        if (fields.isEmpty()) {
            return fact.getType() != null ? fact.getType().name() : "";
        }
        StringBuilder builder = new StringBuilder();
        if (fact.getType() != null) {
            builder.append('[').append(fact.getType().name()).append("] ");
        }
        boolean first = true;
        for (Map.Entry<String, String> entry : fields.entrySet()) {
            if (!first) {
                builder.append(" | ");
            }
            builder.append(entry.getKey()).append('=').append(entry.getValue());
            first = false;
        }
        return builder.toString();
    }
}
