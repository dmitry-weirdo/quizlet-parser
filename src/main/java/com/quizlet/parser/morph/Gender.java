package com.quizlet.parser.morph;

public enum Gender {
    MASCULINE,
    FEMININE,
    NEUTER,
    PLURAL,
    UNKNOWN;

    public static Gender fromMystemTag(String tag) {
        if (tag == null) {
            return UNKNOWN;
        }
        if (tag.contains("pl") || tag.contains("mult")) {
            return PLURAL;
        }
        if (tag.contains("femn")) {
            return FEMININE;
        }
        if (tag.contains("neut")) {
            return NEUTER;
        }
        if (tag.contains("masc")) {
            return MASCULINE;
        }
        return UNKNOWN;
    }
}
