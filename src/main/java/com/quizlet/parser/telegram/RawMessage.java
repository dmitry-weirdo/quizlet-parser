package com.quizlet.parser.telegram;

import java.util.ArrayList;
import java.util.List;

public record RawMessage(
        long messageId,
        String plainText,
        List<String> links,
        List<String> hashtags
) {
    public RawMessage {
        links = links != null ? List.copyOf(links) : List.of();
        hashtags = hashtags != null ? List.copyOf(hashtags) : List.of();
    }

    public boolean isBlank() {
        return (plainText == null || plainText.isBlank()) && links.isEmpty();
    }

    public boolean isLinkOnly() {
        return links.size() == 1 && (plainText == null || plainText.isBlank());
    }

    public static RawMessage empty(long messageId) {
        return new RawMessage(messageId, "", List.of(), List.of());
    }
}
