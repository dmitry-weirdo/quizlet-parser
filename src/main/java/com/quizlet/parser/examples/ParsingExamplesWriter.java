package com.quizlet.parser.examples;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.quizlet.parser.model.Card;

import java.io.IOException;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class ParsingExamplesWriter {

    private static final ObjectMapper MAPPER = new ObjectMapper()
            .enable(SerializationFeature.INDENT_OUTPUT);

    private ParsingExamplesWriter() {
    }

    public static void writeJson(Path output, List<SourceCardGroup> groups) throws IOException {
        ParsingExamplesFile file = new ParsingExamplesFile();
        List<ParsingExample> examples = new ArrayList<>();
        for (SourceCardGroup group : groups) {
            if (group.getCards().isEmpty()) {
                continue;
            }
            examples.add(group.toParsingExample());
        }
        file.setExamples(examples);
        MAPPER.writeValue(output.toFile(), file);
    }

    public static void writeTxt(Path output, List<SourceCardGroup> groups) throws IOException {
        try (Writer writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            writeTxt(writer, groups);
        }
    }

    public static void writeTxt(Writer writer, List<SourceCardGroup> groups) throws IOException {
        int index = 0;
        for (SourceCardGroup group : groups) {
            if (group.getCards().isEmpty()) {
                continue;
            }
            index++;
            writeGroup(writer, group, index);
        }
    }

    private static void writeGroup(Writer writer, SourceCardGroup group, int index) throws IOException {
        writer.write("=====");
        if (group.getId() != null && !group.getId().isBlank()) {
            writer.write(" " + group.getId());
        } else {
            writer.write(" example-" + index);
        }
        writer.write(" =====\n");

        writer.write("TEXT:\n");
        writer.write(group.getText() != null ? group.getText() : "");
        writer.write("\n\n");

        if (!group.getTags().isEmpty()) {
            writer.write("TAGS: " + String.join(", ", group.getTags()));
            writer.write("\n\n");
        }

        writer.write("CARDS:\n");
        int cardNum = 0;
        for (Card card : group.getCards()) {
            cardNum++;
            writer.write("[");
            writer.write(String.valueOf(cardNum));
            writer.write("]\n");
            writer.write("Q: ");
            writer.write(card.question());
            writer.write("\n");
            writer.write("A: ");
            writer.write(card.answer());
            writer.write("\n\n");
        }

        writer.write("---\n\n");
    }

    public static Path txtPathForJson(Path jsonPath) {
        String fileName = jsonPath.getFileName().toString();
        int dot = fileName.lastIndexOf('.');
        String base = dot > 0 ? fileName.substring(0, dot) : fileName;
        return jsonPath.resolveSibling(base + ".txt");
    }
}
