package com.quizlet.parser.telegram;

import com.fasterxml.jackson.databind.JsonNode;

import java.util.ArrayList;
import java.util.List;

public final class MessageTextNormalizer {

    private MessageTextNormalizer() {
    }

    public static RawMessage normalize(long messageId, JsonNode textNode) {
        if (textNode == null || textNode.isNull()) {
            return RawMessage.empty(messageId);
        }

        StringBuilder plain = new StringBuilder();
        List<String> links = new ArrayList<>();
        List<String> hashtags = new ArrayList<>();

        if (textNode.isTextual()) {
            appendPlain(plain, textNode.asText());
        } else if (textNode.isArray()) {
            for (JsonNode part : textNode) {
                if (part.isTextual()) {
                    appendPlain(plain, part.asText());
                } else if (part.isObject()) {
                    String type = part.path("type").asText("");
                    String value = part.path("text").asText("");
                    switch (type) {
                        case "link" -> links.add(value.trim());
                        case "hashtag" -> hashtags.add(value.replace("#", "").trim());
                        case "plain", "bold", "italic", "underline", "strikethrough",
                             "code", "pre", "text_link", "mention", "phone", "email" ->
                                appendPlain(plain, value);
                        default -> appendPlain(plain, value);
                    }
                }
            }
        }

        return new RawMessage(
                messageId,
                collapseWhitespace(plain.toString()),
                links,
                hashtags
        );
    }

    private static void appendPlain(StringBuilder builder, String value) {
        if (value == null || value.isEmpty()) {
            return;
        }
        if (!builder.isEmpty() && !builder.toString().endsWith(" ") && !value.startsWith(" ")) {
            char last = builder.charAt(builder.length() - 1);
            char first = value.charAt(0);
            if (Character.isLetterOrDigit(last) && Character.isLetterOrDigit(first)) {
                builder.append(' ');
            }
        }
        builder.append(value);
    }

    private static String collapseWhitespace(String value) {
        return value.replaceAll("\\s+", " ").trim();
    }
}
