package com.quizlet.parser.examples;

import com.quizlet.parser.model.Card;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ParsingExamplesWriterTest {

    @TempDir
    Path tempDir;

    @Test
    void writesJsonAndTxtInParsingExamplesFormat() throws Exception {
        SourceCardGroup group = new SourceCardGroup(
                "Red Apple — вымышленный бренд",
                List.of(
                        new Card("Вымышленный бренд сигарет в фильмах Тарантино.", "Red Apple"),
                        new Card("Red Apple — вымышленный бренд сигарет, используемый ТАМ.", "В фильмах Тарантино")
                )
        );
        group.setId("red-apple");
        group.setTags(List.of("multi-card"));

        Path jsonPath = tempDir.resolve("output-examples.json");
        Path txtPath = tempDir.resolve("output-examples.txt");

        ParsingExamplesWriter.writeJson(jsonPath, List.of(group));
        ParsingExamplesWriter.writeTxt(txtPath, List.of(group));

        String json = Files.readString(jsonPath);
        assertTrue(json.contains("\"examples\""));
        assertTrue(json.contains("\"red-apple\""));
        assertTrue(json.contains("Red Apple"));

        String txt = Files.readString(txtPath);
        assertTrue(txt.contains("===== red-apple ====="));
        assertTrue(txt.contains("TEXT:"));
        assertTrue(txt.contains("TAGS: multi-card"));
        assertTrue(txt.contains("Q: Вымышленный бренд"));
        assertTrue(txt.contains("A: Red Apple"));
        assertTrue(txt.contains("---"));
    }

    @Test
    void txtPathForJsonReplacesExtension() {
        assertEquals(
                Path.of("output/examples.txt"),
                ParsingExamplesWriter.txtPathForJson(Path.of("output/examples.json"))
        );
    }
}
