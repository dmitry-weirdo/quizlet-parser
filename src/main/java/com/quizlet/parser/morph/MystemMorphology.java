package com.quizlet.parser.morph;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

public final class MystemMorphology implements RussianMorphology {

    private final RussianMorphology fallback = new SimpleMorphology();
    private final String mystemCommand;
    private final boolean available;

    public MystemMorphology() {
        this(detectMystemCommand());
    }

    MystemMorphology(String mystemCommand) {
        this.mystemCommand = mystemCommand;
        this.available = mystemCommand != null && probe(mystemCommand);
    }

    private static String detectMystemCommand() {
        for (String candidate : List.of("mystem", "mystem3", "mystem.exe")) {
            if (probe(candidate)) {
                return candidate;
            }
        }
        return null;
    }

    private static boolean probe(String command) {
        try {
            Process process = new ProcessBuilder(command, "-help")
                    .redirectErrorStream(true)
                    .start();
            boolean finished = process.waitFor(2, TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                return false;
            }
            return process.exitValue() == 0 || process.exitValue() == 1;
        } catch (Exception e) {
            return false;
        }
    }

    @Override
    public boolean isAvailable() {
        return available;
    }

    @Override
    public MorphInfo analyze(String phrase) {
        if (!available || phrase == null || phrase.isBlank()) {
            return fallback.analyze(phrase);
        }
        try {
            List<String> lines = runMystem(phrase);
            Gender gender = Gender.UNKNOWN;
            for (String line : lines) {
                String[] parts = line.split("\\s+");
                if (parts.length >= 2) {
                    gender = Gender.fromMystemTag(parts[1]);
                    if (gender != Gender.UNKNOWN) {
                        break;
                    }
                }
            }
            if (gender == Gender.UNKNOWN) {
                gender = SimpleMorphology.guessGender(phrase);
            }
            return new MorphInfo(gender, GrammaticalCase.NOMINATIVE, gender == Gender.PLURAL);
        } catch (Exception e) {
            return fallback.analyze(phrase);
        }
    }

    @Override
    public String inflect(String phrase, GrammaticalCase grammaticalCase) {
        return fallback.inflect(phrase, grammaticalCase);
    }

    @Override
    public String pronounNominative(String phrase) {
        return pronounFrom(analyze(phrase), true);
    }

    @Override
    public String pronounPrepositional(String phrase) {
        MorphInfo info = analyze(phrase);
        if (info.gender() == Gender.FEMININE) {
            return "НЕЙ";
        }
        if (info.gender() == Gender.PLURAL) {
            return "НИХ";
        }
        return "НЁМ";
    }

    @Override
    public String pronounGenitive(String phrase) {
        MorphInfo info = analyze(phrase);
        if (info.gender() == Gender.FEMININE) {
            return "НЕЁ";
        }
        if (info.gender() == Gender.PLURAL) {
            return "НИХ";
        }
        return "НЕГО";
    }

    @Override
    public String prepositionalPhrase(String phrase) {
        return fallback.prepositionalPhrase(phrase);
    }

    private String pronounFrom(MorphInfo info, boolean nominative) {
        if (nominative) {
            return switch (info.gender()) {
                case FEMININE -> "ОНА";
                case NEUTER -> "ОНО";
                case PLURAL -> "ОНИ";
                default -> "ОН";
            };
        }
        return pronounPrepositional("");
    }

    private List<String> runMystem(String phrase) throws Exception {
        Process process = new ProcessBuilder(mystemCommand, "-l", "-i")
                .redirectErrorStream(true)
                .start();

        process.getOutputStream().write((phrase + System.lineSeparator()).getBytes(StandardCharsets.UTF_8));
        process.getOutputStream().close();

        List<String> lines = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (!line.isBlank()) {
                    lines.add(line.trim());
                }
            }
        }

        if (!process.waitFor(5, TimeUnit.SECONDS)) {
            process.destroyForcibly();
            throw new IllegalStateException("mystem timeout");
        }
        return lines;
    }

    public String getMystemCommand() {
        return mystemCommand;
    }
}
