package com.quizlet.parser.examples;

import com.quizlet.parser.enricher.CardEnricher;
import com.quizlet.parser.enricher.RuleBasedCardEnricher;
import com.quizlet.parser.generator.CardGenerator;
import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.StructuredFact;
import com.quizlet.parser.morph.RussianMorphology;
import com.quizlet.parser.morph.SimpleMorphology;
import com.quizlet.parser.telegram.HeuristicFactParser;
import com.quizlet.parser.telegram.ParseOptions;
import com.quizlet.parser.telegram.ParseResult;
import com.quizlet.parser.telegram.RawMessage;

import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

public final class TextToCardsPipeline {

    private final CardGenerator generator;
    private final HeuristicFactParser parser;
    private final ParsingExamplesLoader examplesLoader;
    private final boolean useExampleOverlay;

    public TextToCardsPipeline() throws IOException {
        this(ParsingExamplesLoader.loadDefault(), ParseOptions.defaults(), true);
    }

    public TextToCardsPipeline(ParsingExamplesLoader examplesLoader,
                               ParseOptions parseOptions,
                               boolean useExampleOverlay) throws IOException {
        this.examplesLoader = examplesLoader;
        this.useExampleOverlay = useExampleOverlay;
        RussianMorphology morphology = new SimpleMorphology();
        CardEnricher enricher = new RuleBasedCardEnricher();
        this.generator = new CardGenerator(morphology, enricher);
        this.parser = new HeuristicFactParser(parseOptions);
    }

    public List<Card> generateFromText(String text) {
        if (useExampleOverlay) {
            Optional<ParsingExample> example = examplesLoader.findByText(text);
            if (example.isPresent()) {
                return example.get().toCards();
            }
        }
        return generateHeuristic(text);
    }

    public List<Card> generateHeuristic(String text) {
        RawMessage message = new RawMessage(0L, ParsingExamplesLoader.normalizeText(text), List.of(), List.of());
        ParseResult parseResult = new ParseResult();
        parser.parseMessage(message, parseResult);
        return generator.generateAll(parseResult.getFacts());
    }

    public ParsingExamplesLoader getExamplesLoader() {
        return examplesLoader;
    }

    public static List<Card> deduplicate(List<Card> cards) {
        Set<String> seen = new LinkedHashSet<>();
        List<Card> result = new ArrayList<>();
        for (Card card : cards) {
            String key = card.question() + "\u0000" + card.answer();
            if (seen.add(key)) {
                result.add(card);
            }
        }
        return result;
    }
}
