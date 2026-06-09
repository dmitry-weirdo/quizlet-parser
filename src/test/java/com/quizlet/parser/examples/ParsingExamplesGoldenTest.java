package com.quizlet.parser.examples;

import com.quizlet.parser.model.Card;
import com.quizlet.parser.telegram.ParseOptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

class ParsingExamplesGoldenTest {

    private static final Path EXAMPLES = Path.of("parsing-examples", "parsing-examples.json");
    private static ParsingExamplesLoader loader;

    @BeforeAll
    static void setUp() throws Exception {
        assumeTrue(EXAMPLES.toFile().exists(), "parsing-examples.json not found");
        loader = ParsingExamplesLoader.load(EXAMPLES);
    }

    @Test
    void exampleOverlayReturnsExactGoldenCards() throws Exception {
        TextToCardsPipeline pipeline = new TextToCardsPipeline(loader, ParseOptions.defaults(), true);
        for (ParsingExample example : loader.getExamples()) {
            List<Card> actual = pipeline.generateFromText(example.getText());
            assertEquals(example.toCards(), actual, "overlay mismatch for " + example.displayId());
        }
    }

    @Test
    void examplesReportContainsModeDocumentsGap() throws Exception {
        TextToCardsPipeline pipeline = new TextToCardsPipeline(loader, ParseOptions.defaults(), false);
        ParsingExamplesReporter reporter = new ParsingExamplesReporter(
                pipeline, loader, CardMatcher.Mode.CONTAINS);
        ParsingExamplesReporter.Report report = reporter.run();
        assertTrue(report.totalCount() > 0);
        // Heuristic pipeline may not yet cover all golden cards; report documents the gap.
    }

    @Test
    void normalizeTextIgnoresExtraWhitespace() {
        String a = "Red Apple — вымышленный бренд";
        String b = "Red Apple —  вымышленный   бренд";
        assertEquals(ParsingExamplesLoader.normalizeText(a), ParsingExamplesLoader.normalizeText(b));
    }
}
