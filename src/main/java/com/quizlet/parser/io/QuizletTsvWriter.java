package com.quizlet.parser.io;

import com.quizlet.parser.model.Card;

import java.io.IOException;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class QuizletTsvWriter {

    private QuizletTsvWriter() {
    }

    public static void write(Path output, List<Card> cards) throws IOException {
        try (Writer writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            write(writer, cards);
        }
    }

    public static void write(Writer writer, List<Card> cards) throws IOException {
        for (Card card : cards) {
            writer.write(sanitize(card.question()));
            writer.write('\t');
            writer.write(sanitize(card.answer()));
            writer.write(System.lineSeparator());
        }
    }

    private static String sanitize(String value) {
        return value.replace('\t', ' ').replace('\r', ' ').trim();
    }
}
