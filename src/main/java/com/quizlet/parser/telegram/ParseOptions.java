package com.quizlet.parser.telegram;

public record ParseOptions(
        boolean skipLinkOnly,
        boolean fetchWiki,
        boolean skipOrphan
) {
    public static ParseOptions defaults() {
        return new ParseOptions(false, false, false);
    }
}