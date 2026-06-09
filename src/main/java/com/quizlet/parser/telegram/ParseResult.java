package com.quizlet.parser.telegram;

import com.quizlet.parser.model.StructuredFact;

import java.util.ArrayList;
import java.util.List;

public final class ParseResult {

    private final List<StructuredFact> facts = new ArrayList<>();
    private final List<String> warnings = new ArrayList<>();
    private int skipped;

    public void addFact(StructuredFact fact) {
        if (fact != null) {
            facts.add(fact);
        }
    }

    public void addFacts(List<StructuredFact> newFacts) {
        if (newFacts != null) {
            facts.addAll(newFacts);
        }
    }

    public void addWarning(String warning) {
        warnings.add(warning);
    }

    public void incrementSkipped() {
        skipped++;
    }

    public List<StructuredFact> getFacts() {
        return List.copyOf(facts);
    }

    public List<String> getWarnings() {
        return List.copyOf(warnings);
    }

    public int getSkipped() {
        return skipped;
    }
}
