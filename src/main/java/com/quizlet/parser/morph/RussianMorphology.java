package com.quizlet.parser.morph;

public interface RussianMorphology {

    MorphInfo analyze(String phrase);

    String inflect(String phrase, GrammaticalCase grammaticalCase);

    String pronounNominative(String phrase);

    String pronounPrepositional(String phrase);

    String pronounGenitive(String phrase);

    String prepositionalPhrase(String phrase);

    default boolean isAvailable() {
        return true;
    }
}
