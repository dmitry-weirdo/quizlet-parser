package com.quizlet.parser.telegram;

import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class WikipediaTitleExtractor {

    private static final Pattern WIKI_PATH = Pattern.compile("/wiki/([^?#]+)");

    private WikipediaTitleExtractor() {
    }

    public static boolean isWikipediaUrl(String url) {
        if (url == null || url.isBlank()) {
            return false;
        }
        String lower = url.toLowerCase(Locale.ROOT);
        return lower.contains("wikipedia.org/wiki/");
    }

    public static String titleFromUrl(String url) {
        if (url == null || url.isBlank()) {
            return "";
        }
        try {
            URI uri = URI.create(url.trim());
            Matcher matcher = WIKI_PATH.matcher(uri.getPath());
            if (matcher.find()) {
                return slugToTitle(matcher.group(1));
            }
        } catch (IllegalArgumentException ignored) {
            Matcher matcher = WIKI_PATH.matcher(url);
            if (matcher.find()) {
                return slugToTitle(matcher.group(1));
            }
        }
        return "";
    }

    public static String slugToTitle(String slug) {
        if (slug == null || slug.isBlank()) {
            return "";
        }
        String decoded = URLDecoder.decode(slug, StandardCharsets.UTF_8);
        return decoded.replace('_', ' ').trim();
    }
}
