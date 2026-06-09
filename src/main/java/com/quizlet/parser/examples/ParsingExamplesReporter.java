package com.quizlet.parser.examples;

import com.quizlet.parser.model.Card;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public final class ParsingExamplesReporter {

    private final TextToCardsPipeline pipeline;
    private final ParsingExamplesLoader loader;
    private final CardMatcher.Mode mode;

    public ParsingExamplesReporter(TextToCardsPipeline pipeline,
                                   ParsingExamplesLoader loader,
                                   CardMatcher.Mode mode) {
        this.pipeline = pipeline;
        this.loader = loader;
        this.mode = mode;
    }

    public static ParsingExamplesReporter create(CardMatcher.Mode mode) throws IOException {
        ParsingExamplesLoader loader = ParsingExamplesLoader.loadDefault();
        TextToCardsPipeline heuristicPipeline = new TextToCardsPipeline(loader, 
                com.quizlet.parser.telegram.ParseOptions.defaults(), false);
        return new ParsingExamplesReporter(heuristicPipeline, loader, mode);
    }

    public Report run() {
        List<ExampleReport> exampleReports = new ArrayList<>();
        int passed = 0;
        for (ParsingExample example : loader.getExamples()) {
            List<Card> expected = example.toCards();
            List<Card> actual = pipeline.generateHeuristic(example.getText());
            CardMatcher.MatchResult match = CardMatcher.compare(expected, actual, mode);
            exampleReports.add(new ExampleReport(example, expected, match));
            if (match.passed()) {
                passed++;
            }
        }
        return new Report(exampleReports, passed, loader.getExamples().size());
    }

    public void printReport(Report report) {
        System.out.printf("Examples report: %d/%d passed (%s mode)%n",
                report.passedCount(), report.totalCount(), mode.name().toLowerCase());
        for (ExampleReport item : report.items()) {
            if (item.match().passed()) {
                System.out.printf("[PASS] %s%n", item.example().displayId());
                continue;
            }
            System.out.printf("[FAIL] %s%n", item.example().displayId());
            System.out.printf("  text: %s%n", truncate(item.example().getText(), 120));
            for (Card missing : item.match().missing()) {
                System.out.printf("  missing: %s -> %s%n", missing.question(), missing.answer());
            }
            if (!item.match().actual().isEmpty()) {
                Card first = item.match().actual().get(0);
                System.out.printf("  got (first): %s -> %s%n", first.question(), first.answer());
            }
            if (mode == CardMatcher.Mode.STRICT && !item.match().extra().isEmpty()) {
                System.out.printf("  extra cards: %d%n", item.match().extra().size());
            }
        }
    }

    private static String truncate(String value, int max) {
        if (value == null) {
            return "";
        }
        String oneLine = value.replaceAll("\\s+", " ").trim();
        return oneLine.length() <= max ? oneLine : oneLine.substring(0, max) + "...";
    }

    public record ExampleReport(
            ParsingExample example,
            List<Card> expected,
            CardMatcher.MatchResult match
    ) {
    }

    public record Report(
            List<ExampleReport> items,
            int passedCount,
            int totalCount
    ) {
        public boolean allPassed() {
            return passedCount == totalCount;
        }
    }
}
