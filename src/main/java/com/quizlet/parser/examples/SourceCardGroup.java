package com.quizlet.parser.examples;

import com.quizlet.parser.model.Card;

import java.util.ArrayList;
import java.util.List;

public final class SourceCardGroup {

    private String id;
    private String text;
    private List<String> tags = new ArrayList<>();
    private List<Card> cards = new ArrayList<>();

    public SourceCardGroup() {
    }

    public SourceCardGroup(String text, List<Card> cards) {
        this.text = text;
        this.cards = cards != null ? new ArrayList<>(cards) : new ArrayList<>();
    }

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

    public List<Card> getCards() {
        return cards;
    }

    public void setCards(List<Card> cards) {
        this.cards = cards != null ? cards : new ArrayList<>();
    }

    public ParsingExample toParsingExample() {
        ParsingExample example = new ParsingExample();
        example.setId(id);
        example.setText(text);
        example.setTags(tags);
        List<ParsingExampleCard> exampleCards = new ArrayList<>();
        for (Card card : cards) {
            ParsingExampleCard item = new ParsingExampleCard();
            item.setQuestion(card.question());
            item.setAnswer(card.answer());
            exampleCards.add(item);
        }
        example.setCards(exampleCards);
        return example;
    }
}
