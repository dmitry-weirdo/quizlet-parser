package com.quizlet.parser.enricher;

import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.StructuredFact;

import java.util.List;

/**
 * Optional LLM-backed enricher stub. Requires external API configuration.
 * Falls back to empty list when not configured.
 */
public final class LlmCardEnricher implements CardEnricher {

    private final String apiUrl;
    private final String apiKey;
    private final CardEnricher fallback;

    public LlmCardEnricher(String apiUrl, String apiKey) {
        this(apiUrl, apiKey, new RuleBasedCardEnricher());
    }

    public LlmCardEnricher(String apiUrl, String apiKey, CardEnricher fallback) {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.fallback = fallback;
    }

    @Override
    public List<Card> enrich(StructuredFact fact) {
        if (!isConfigured()) {
            return fallback.enrich(fact);
        }
        // Placeholder for LLM integration: POST fact JSON to apiUrl, parse Card list from response.
        return fallback.enrich(fact);
    }

    public boolean isConfigured() {
        return apiUrl != null && !apiUrl.isBlank() && apiKey != null && !apiKey.isBlank();
    }
}
