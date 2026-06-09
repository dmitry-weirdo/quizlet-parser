package com.quizlet.parser.examples;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.quizlet.parser.model.Card;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ParsingExampleCard {

    private String question;
    private String answer;

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public Card toCard() {
        return new Card(question, answer);
    }
}
