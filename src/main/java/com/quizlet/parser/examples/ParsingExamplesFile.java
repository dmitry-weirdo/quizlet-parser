package com.quizlet.parser.examples;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import java.util.ArrayList;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ParsingExamplesFile {

    private List<ParsingExample> examples = new ArrayList<>();

    public List<ParsingExample> getExamples() {
        return examples;
    }

    public void setExamples(List<ParsingExample> examples) {
        this.examples = examples != null ? examples : new ArrayList<>();
    }
}
