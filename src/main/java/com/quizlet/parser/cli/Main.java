package com.quizlet.parser.cli;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.quizlet.parser.enricher.CardEnricher;
import com.quizlet.parser.enricher.LlmCardEnricher;
import com.quizlet.parser.enricher.RuleBasedCardEnricher;
import com.quizlet.parser.examples.CardMatcher;
import com.quizlet.parser.examples.FactTextRenderer;
import com.quizlet.parser.examples.GenerationResult;
import com.quizlet.parser.examples.ParsingExample;
import com.quizlet.parser.examples.ParsingExamplesLoader;
import com.quizlet.parser.examples.ParsingExamplesReporter;
import com.quizlet.parser.examples.ParsingExamplesWriter;
import com.quizlet.parser.examples.SourceCardGroup;
import com.quizlet.parser.examples.TextToCardsPipeline;
import com.quizlet.parser.generator.CardGenerator;
import com.quizlet.parser.io.QuizletTsvWriter;
import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.StructuredFact;
import com.quizlet.parser.morph.MystemMorphology;
import com.quizlet.parser.morph.RussianMorphology;
import com.quizlet.parser.morph.SimpleMorphology;
import com.quizlet.parser.telegram.HeuristicFactParser;
import com.quizlet.parser.telegram.ParseOptions;
import com.quizlet.parser.telegram.ParseResult;
import com.quizlet.parser.telegram.RawMessage;
import com.quizlet.parser.telegram.TelegramJsonReader;
import com.quizlet.parser.telegram.WikipediaTitleExtractor;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;

@Command(
        name = "quizlet-parser",
        mixinStandardHelpOptions = true,
        version = "1.0.0",
        description = "Generate Quizlet flashcards from structured facts or Telegram JSON export"
)
public final class Main implements Callable<Integer> {

    @Option(names = {"-i", "--input"}, description = "Input JSON file with StructuredFact array")
    private Path input;

    @Option(names = {"--telegram-json"}, description = "Telegram Desktop JSON export (result.json)")
    private Path telegramJson;

    @Option(names = {"-o", "--output"}, description = "Output Quizlet TSV file")
    private Path output;

    @Option(names = {"--output-examples"}, description = "Also write parsing-examples JSON (and .txt alongside)")
    private Path outputExamples;

    @Option(names = {"--output-examples-txt"}, description = "Override path for parsing-examples TXT output")
    private Path outputExamplesTxt;

    @Option(names = {"--dump-facts"}, description = "Write parsed StructuredFact JSON for debugging")
    private Path dumpFacts;

    @Option(names = {"--examples-report"}, description = "Compare heuristic pipeline vs parsing-examples.json")
    private Path examplesReport;

    @Option(names = {"--examples"}, description = "Path to parsing-examples.json (default: parsing-examples/parsing-examples.json)")
    private Path examplesPath;

    @Option(names = {"--no-examples-overlay"}, description = "Do not use parsing-examples.json as golden cards for matching texts")
    private boolean noExamplesOverlay;

    @Option(names = {"--fetch-wiki"}, description = "Fetch Wikipedia summaries for link-only messages")
    private boolean fetchWiki;

    @Option(names = {"--skip-link-only"}, description = "Skip messages that contain only a link")
    private boolean skipLinkOnly;

    @Option(names = {"--skip-orphan"}, description = "Skip short notes without —, :, ? or links (e.g. «паста Фузилли»)")
    private boolean skipOrphan;

    @Option(names = {"--mystem"}, description = "Use mystem for morphology when available")
    private boolean useMystem;

    @Option(names = {"--llm-url"}, description = "Optional LLM API URL for enrichment")
    private String llmUrl;

    @Option(names = {"--llm-key"}, description = "Optional LLM API key")
    private String llmKey;

    public static void main(String[] args) {
        int exitCode = new CommandLine(new Main()).execute(args);
        System.exit(exitCode);
    }

    @Override
    public Integer call() throws Exception {
        if (examplesReport != null) {
            return runExamplesReport();
        }

        if (output == null) {
            throw new CommandLine.ParameterException(
                    new CommandLine(this),
                    "Specify -o/--output or --examples-report"
            );
        }

        if (input == null && telegramJson == null) {
            throw new CommandLine.ParameterException(
                    new CommandLine(this),
                    "Specify either --input or --telegram-json"
            );
        }
        if (input != null && telegramJson != null) {
            throw new CommandLine.ParameterException(
                    new CommandLine(this),
                    "Use only one input source: --input or --telegram-json"
            );
        }

        GenerationResult result;
        List<StructuredFact> factsForDump = List.of();

        if (telegramJson != null) {
            result = generateFromTelegram();
        } else {
            List<StructuredFact> facts = loadFactsFromJson();
            factsForDump = facts;
            CardGenerator generator = new CardGenerator(createMorphology(), createEnricher());
            result = generateFromFacts(facts, generator);
        }

        List<Card> cards = result.cards();

        if (dumpFacts != null && telegramJson == null) {
            ObjectMapper mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
            mapper.writeValue(dumpFacts.toFile(), factsForDump);
            System.out.printf("Dumped %d facts -> %s%n", factsForDump.size(), dumpFacts.toAbsolutePath());
        }

        QuizletTsvWriter.write(output, cards);
        System.out.printf("Generated %d cards -> %s%n", cards.size(), output.toAbsolutePath());

        if (outputExamples != null) {
            ParsingExamplesWriter.writeJson(outputExamples, result.groups());
            Path txtPath = outputExamplesTxt != null
                    ? outputExamplesTxt
                    : ParsingExamplesWriter.txtPathForJson(outputExamples);
            ParsingExamplesWriter.writeTxt(txtPath, result.groups());
            System.out.printf(
                    "Wrote %d examples -> %s and %s%n",
                    result.groups().size(),
                    outputExamples.toAbsolutePath(),
                    txtPath.toAbsolutePath()
            );
        }

        printMorphologyInfo();
        return 0;
    }

    private int runExamplesReport() throws Exception {
        ParsingExamplesLoader loader = loadExamples();
        ParseOptions options = new ParseOptions(skipLinkOnly, fetchWiki, skipOrphan);
        TextToCardsPipeline pipeline = new TextToCardsPipeline(loader, options, false);
        ParsingExamplesReporter reporter = new ParsingExamplesReporter(pipeline, loader, CardMatcher.Mode.CONTAINS);
        ParsingExamplesReporter.Report report = reporter.run();
        reporter.printReport(report);
        return report.allPassed() ? 0 : 1;
    }

    private GenerationResult generateFromTelegram() throws Exception {
        ParsingExamplesLoader examplesLoader = loadExamples();
        ParseOptions options = new ParseOptions(skipLinkOnly, fetchWiki, skipOrphan);
        boolean useOverlay = !noExamplesOverlay;

        TelegramJsonReader reader = new TelegramJsonReader();
        List<RawMessage> messages = reader.readMessages(telegramJson);
        HeuristicFactParser parser = new HeuristicFactParser(options);
        CardGenerator generator = new CardGenerator(createMorphology(), createEnricher());

        List<Card> cards = new ArrayList<>();
        List<SourceCardGroup> groups = new ArrayList<>();
        int overlayHits = 0;
        int skipped = 0;

        for (RawMessage message : messages) {
            Optional<ParsingExample> example = findExample(examplesLoader, message);
            if (useOverlay && example.isPresent()) {
                List<Card> messageCards = example.get().toCards();
                cards.addAll(messageCards);
                groups.add(toSourceGroup(example.get(), messageCards));
                overlayHits++;
                continue;
            }

            ParseResult parseResult = new ParseResult();
            parser.parseMessage(message, parseResult);
            if (parseResult.getFacts().isEmpty()) {
                skipped++;
                continue;
            }
            List<Card> messageCards = generator.generateAll(parseResult.getFacts());
            if (!messageCards.isEmpty()) {
                cards.addAll(messageCards);
                groups.add(new SourceCardGroup(resolveSourceText(message), messageCards));
            }
        }

        cards = TextToCardsPipeline.deduplicate(cards);
        System.out.printf(
                "Telegram: %d messages, %d example overlays, %d skipped, %d cards, %d example groups%n",
                messages.size(), overlayHits, skipped, cards.size(), groups.size()
        );
        return new GenerationResult(cards, groups);
    }

    private static GenerationResult generateFromFacts(List<StructuredFact> facts, CardGenerator generator) {
        List<Card> cards = new ArrayList<>();
        List<SourceCardGroup> groups = new ArrayList<>();
        for (StructuredFact fact : facts) {
            List<Card> factCards = generator.generate(fact);
            if (factCards.isEmpty()) {
                continue;
            }
            cards.addAll(factCards);
            groups.add(new SourceCardGroup(FactTextRenderer.render(fact), factCards));
        }
        return new GenerationResult(cards, groups);
    }

    private static SourceCardGroup toSourceGroup(ParsingExample example, List<Card> cards) {
        SourceCardGroup group = new SourceCardGroup(example.getText(), cards);
        group.setId(example.getId());
        group.setTags(example.getTags());
        return group;
    }

    private static String resolveSourceText(RawMessage message) {
        if (message.plainText() != null && !message.plainText().isBlank()) {
            return message.plainText();
        }
        if (message.isLinkOnly() && !message.links().isEmpty()) {
            return WikipediaTitleExtractor.titleFromUrl(message.links().get(0));
        }
        return "";
    }

    private static Optional<ParsingExample> findExample(
            ParsingExamplesLoader loader,
            RawMessage message
    ) {
        Optional<ParsingExample> byText = loader.findByText(message.plainText());
        if (byText.isPresent()) {
            return byText;
        }
        if (message.isLinkOnly() && !message.links().isEmpty()) {
            String title = WikipediaTitleExtractor.titleFromUrl(message.links().get(0));
            return loader.findByText(title);
        }
        return Optional.empty();
    }

    private ParsingExamplesLoader loadExamples() throws Exception {
        if (examplesPath != null) {
            return ParsingExamplesLoader.load(examplesPath);
        }
        return ParsingExamplesLoader.loadDefault();
    }

    private List<StructuredFact> loadFactsFromJson() throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(input.toFile(), new TypeReference<>() {
        });
    }

    private void printMorphologyInfo() {
        RussianMorphology morphology = createMorphology();
        if (morphology instanceof MystemMorphology mystem && mystem.isAvailable()) {
            System.out.printf("Morphology: mystem (%s)%n", mystem.getMystemCommand());
        } else {
            System.out.println("Morphology: simple heuristics");
        }
    }

    private RussianMorphology createMorphology() {
        if (useMystem) {
            MystemMorphology mystem = new MystemMorphology();
            return mystem.isAvailable() ? mystem : new SimpleMorphology();
        }
        MystemMorphology auto = new MystemMorphology();
        return auto.isAvailable() ? auto : new SimpleMorphology();
    }

    private CardEnricher createEnricher() {
        if (llmUrl != null && !llmUrl.isBlank()) {
            return new LlmCardEnricher(llmUrl, llmKey);
        }
        return new RuleBasedCardEnricher();
    }
}
