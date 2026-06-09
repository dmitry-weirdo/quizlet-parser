package com.quizlet.parser.morph;

import java.util.Locale;

public final class SimpleMorphology implements RussianMorphology {

    public static Gender guessGender(String phrase) {
        if (phrase == null || phrase.isBlank()) {
            return Gender.UNKNOWN;
        }
        String[] words = phrase.trim().split("\\s+");
        String last = words[words.length - 1].toLowerCase(Locale.ROOT);

        if (last.endsWith("ы") || last.endsWith("и") && !last.endsWith("ии") && last.length() > 3) {
            if (last.endsWith("ии") || last.endsWith("и")) {
                // ambiguous; check common plural patterns
            }
        }
        if (last.endsWith("а") && !last.endsWith("ка") && last.length() > 2) {
            return Gender.FEMININE;
        }
        if (last.endsWith("я") && last.length() > 2) {
            return Gender.FEMININE;
        }
        if (last.endsWith("о") || last.endsWith("е") && last.length() <= 5) {
            return Gender.NEUTER;
        }
        if (last.endsWith("и") && (last.endsWith("ки") || last.endsWith("ги") || last.endsWith("цы"))) {
            return Gender.PLURAL;
        }
        return Gender.MASCULINE;
    }

    @Override
    public MorphInfo analyze(String phrase) {
        return MorphInfo.unknown(phrase);
    }

    @Override
    public String inflect(String phrase, GrammaticalCase grammaticalCase) {
        if (phrase == null || phrase.isBlank()) {
            return phrase;
        }
        return switch (grammaticalCase) {
            case NOMINATIVE -> phrase;
            case GENITIVE -> toGenitive(phrase);
            case ACCUSATIVE -> toAccusative(phrase);
            case PREPOSITIONAL -> toPrepositional(phrase);
            default -> phrase;
        };
    }

    @Override
    public String pronounNominative(String phrase) {
        return switch (analyze(phrase).gender()) {
            case FEMININE -> "ОНА";
            case NEUTER -> "ОНО";
            case PLURAL -> "ОНИ";
            default -> "ОН";
        };
    }

    @Override
    public String pronounPrepositional(String phrase) {
        return switch (analyze(phrase).gender()) {
            case FEMININE -> "НЕЙ";
            case PLURAL -> "НИХ";
            default -> "НЁМ";
        };
    }

    @Override
    public String pronounGenitive(String phrase) {
        return switch (analyze(phrase).gender()) {
            case FEMININE -> "НЕЁ";
            case PLURAL -> "НИХ";
            default -> "НЕГО";
        };
    }

    @Override
    public String prepositionalPhrase(String phrase) {
        Gender gender = analyze(phrase).gender();
        String preposition = gender == Gender.FEMININE ? "на " : "в ";
        if (phrase.toLowerCase(Locale.ROOT).contains("остров")
                || phrase.toLowerCase(Locale.ROOT).contains("полуостров")
                || phrase.toLowerCase(Locale.ROOT).contains("гор")
                || phrase.toLowerCase(Locale.ROOT).contains("берег")) {
            preposition = "на ";
        }
        return preposition + toPrepositional(phrase);
    }

    private String toGenitive(String phrase) {
        String[] words = phrase.split("\\s+");
        words[words.length - 1] = inflectWordGenitive(words[words.length - 1], guessGender(phrase));
        return String.join(" ", words);
    }

    private String toAccusative(String phrase) {
        Gender gender = guessGender(phrase);
        if (gender == Gender.FEMININE || gender == Gender.NEUTER) {
            return toNominativeAsAccusative(phrase, gender);
        }
        return toGenitive(phrase);
    }

    private String toPrepositional(String phrase) {
        String[] words = phrase.split("\\s+");
        words[words.length - 1] = inflectWordPrepositional(words[words.length - 1], guessGender(phrase));
        return String.join(" ", words);
    }

    private String toNominativeAsAccusative(String phrase, Gender gender) {
        return phrase;
    }

    private String inflectWordGenitive(String word, Gender gender) {
        if (word.endsWith("а")) {
            return word.substring(0, word.length() - 1) + "ы";
        }
        if (word.endsWith("я")) {
            return word.substring(0, word.length() - 1) + "и";
        }
        if (word.endsWith("ь")) {
            return word.substring(0, word.length() - 1) + "я";
        }
        if (gender == Gender.FEMININE && word.endsWith("ия")) {
            return word.substring(0, word.length() - 1) + "и";
        }
        return word + "а";
    }

    private String inflectWordPrepositional(String word, Gender gender) {
        if (word.endsWith("а")) {
            return word.substring(0, word.length() - 1) + "е";
        }
        if (word.endsWith("я")) {
            return word.substring(0, word.length() - 1) + "е";
        }
        if (word.endsWith("ь")) {
            return word.substring(0, word.length() - 1) + "и";
        }
        if (word.endsWith("й")) {
            return word.substring(0, word.length() - 1) + "е";
        }
        if (word.endsWith("о")) {
            return word.substring(0, word.length() - 1) + "е";
        }
        return word + "е";
    }
}
