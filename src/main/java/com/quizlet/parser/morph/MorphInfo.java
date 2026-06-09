package com.quizlet.parser.morph;

public record MorphInfo(Gender gender, GrammaticalCase grammaticalCase, boolean plural) {

    public static MorphInfo unknown(String phrase) {
        Gender gender = SimpleMorphology.guessGender(phrase);
        return new MorphInfo(gender, GrammaticalCase.NOMINATIVE, gender == Gender.PLURAL);
    }
}
