package com.quizlet.parser.examples;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.quizlet.parser.model.Card;

import java.util.ArrayList;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ParsingExample {

    private String id;
    private String text;
    private List<String> tags = new ArrayList<>();
    private List<ParsingExampleCard> cards = new ArrayList<>();

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public List<String> getTags() {
        return tags;
    }

    public void setTags(List<String> tags) {
        this.tags = tags != null ? tags : new ArrayList<>();
    }

    public List<ParsingExampleCard> getCards() {
        return cards;
    }

    public void setCards(List<ParsingExampleCard> cards) {
        this.cards = cards != null ? cards : new ArrayList<>();
    }

    public List<Card> toCards() {
        return cards.stream().map(ParsingExampleCard::toCard).toList();
    }

    public String displayId() {
        if (id != null && !id.isBlank()) {
            return id;
        }
        String normalized = ParsingExamplesLoader.normalizeText(text);
        return normalized.length() > 40 ? normalized.substring(0, 40) + "..." : normalized;
    }
}
