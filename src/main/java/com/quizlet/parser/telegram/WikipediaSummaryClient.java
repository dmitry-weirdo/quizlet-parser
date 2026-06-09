package com.quizlet.parser.telegram;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Locale;
import java.util.Optional;

public final class WikipediaSummaryClient {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private final HttpClient httpClient;
    private final Duration timeout;

    public WikipediaSummaryClient() {
        this(HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(5))
                .build(), Duration.ofSeconds(10));
    }

    WikipediaSummaryClient(HttpClient httpClient, Duration timeout) {
        this.httpClient = httpClient;
        this.timeout = timeout;
    }

    public Optional<String> fetchExtract(String title) {
        if (title == null || title.isBlank()) {
            return Optional.empty();
        }
        String wikiLang = "ru";
        String encodedTitle = URLEncoder.encode(title, StandardCharsets.UTF_8).replace("+", "%20");
        URI uri = URI.create("https://" + wikiLang + ".wikipedia.org/api/rest_v1/page/summary/" + encodedTitle);

        HttpRequest request = HttpRequest.newBuilder(uri)
                .timeout(timeout)
                .header("Accept", "application/json")
                .header("User-Agent", "quizlet-parser/1.0")
                .GET()
                .build();

        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                return Optional.empty();
            }
            JsonNode root = MAPPER.readTree(response.body());
            String extract = root.path("extract").asText("").trim();
            if (extract.isBlank()) {
                return Optional.empty();
            }
            int dot = extract.indexOf('.');
            if (dot > 0 && dot < 400) {
                return Optional.of(extract.substring(0, dot + 1));
            }
            return Optional.of(truncate(extract, 300));
        } catch (IOException | InterruptedException e) {
            if (e instanceof InterruptedException) {
                Thread.currentThread().interrupt();
            }
            return Optional.empty();
        }
    }

    public Optional<String> fetchExtractFromUrl(String url) {
        if (!WikipediaTitleExtractor.isWikipediaUrl(url)) {
            return Optional.empty();
        }
        String title = WikipediaTitleExtractor.titleFromUrl(url);
        return fetchExtract(title);
    }

    private static String truncate(String value, int maxLen) {
        if (value.length() <= maxLen) {
            return value;
        }
        return value.substring(0, maxLen).trim() + "...";
    }
}
