package com.quizlet.parser.examples;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public final class ParsingExamplesLoader {

    private static final ObjectMapper MAPPER = new ObjectMapper();
    private static final Path DEFAULT_PATH = Path.of("parsing-examples", "parsing-examples.json");

    private final Map<String, ParsingExample> byNormalizedText = new LinkedHashMap<>();
    private final List<ParsingExample> examples;

    private ParsingExamplesLoader(List<ParsingExample> examples) {
        this.examples = List.copyOf(examples);
        for (ParsingExample example : examples) {
            byNormalizedText.put(normalizeText(example.getText()), example);
        }
    }

    public static ParsingExamplesLoader load(Path path) throws IOException {
        ParsingExamplesFile file = MAPPER.readValue(path.toFile(), ParsingExamplesFile.class);
        return new ParsingExamplesLoader(file.getExamples());
    }

    public static ParsingExamplesLoader loadFromClasspath() throws IOException {
        try (InputStream input = ParsingExamplesLoader.class.getClassLoader()
                .getResourceAsStream("parsing-examples.json")) {
            if (input == null) {
                return load(DEFAULT_PATH);
            }
            ParsingExamplesFile file = MAPPER.readValue(input, ParsingExamplesFile.class);
            return new ParsingExamplesLoader(file.getExamples());
        }
    }

    public static ParsingExamplesLoader loadDefault() throws IOException {
        if (DEFAULT_PATH.toFile().exists()) {
            return load(DEFAULT_PATH);
        }
        return loadFromClasspath();
    }

    public List<ParsingExample> getExamples() {
        return examples;
    }

    public Optional<ParsingExample> findByText(String text) {
        return Optional.ofNullable(byNormalizedText.get(normalizeText(text)));
    }

    public static String normalizeText(String text) {
        if (text == null) {
            return "";
        }
        return text.replaceAll("\\s+", " ").trim();
    }
}
