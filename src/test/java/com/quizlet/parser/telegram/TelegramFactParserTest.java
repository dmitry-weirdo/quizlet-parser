package com.quizlet.parser.telegram;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.quizlet.parser.generator.CardGenerator;
import com.quizlet.parser.model.FactType;
import com.quizlet.parser.model.RelationType;
import com.quizlet.parser.model.StructuredFact;
import com.quizlet.parser.enricher.RuleBasedCardEnricher;
import com.quizlet.parser.morph.SimpleMorphology;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

class TelegramFactParserTest {

    private static final Path TELEGRAM_EXPORT = Path.of("telegram-export-json", "result.json");

    @Test
    void normalizesStringText() {
        RawMessage raw = MessageTextNormalizer.normalize(1L, new ObjectMapper().valueToTree("Бродский: test"));
        assertEquals("Бродский: test", raw.plainText());
    }

    @Test
    void normalizesMixedArrayWithLink() throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        var node = mapper.readTree("""
                ["Кончина Фидельки ", {"type":"link","text":"https://example.com/a"}, ""]
                """);
        RawMessage raw = MessageTextNormalizer.normalize(2L, node);
        assertEquals("Кончина Фидельки", raw.plainText());
        assertEquals(List.of("https://example.com/a"), raw.links());
    }

    @Test
    void wikiTitleFromUrl() {
        String title = WikipediaTitleExtractor.titleFromUrl(
                "https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D1%85%D0%B8%D1%89%D0%B5%D0%BD%D0%BD%D0%BE%D0%B5_%D0%BF%D0%B8%D1%81%D1%8C%D0%BC%D0%BE"
        );
        assertEquals("Похищенное письмо", title);
    }

    @Test
    void parsesAuthorQuote() {
        RawMessage raw = new RawMessage(3L,
                "Бродский: Если Евтушенко против, то я за",
                List.of(), List.of());
        ParseResult result = new HeuristicFactParser().parseAll(List.of(raw));
        assertEquals(1, result.getFacts().size());
        StructuredFact fact = result.getFacts().get(0);
        assertEquals(FactType.QUOTE, fact.getType());
        assertEquals("Бродский", fact.getAuthor());
        assertTrue(fact.getQuote().contains("Евтушенко"));
    }

    @Test
    void parsesTitleAuthorLink() {
        RawMessage raw = new RawMessage(4L,
                "Украденное письмо — Эдгар Аллан По — ",
                List.of("https://ru.wikipedia.org/wiki/%D0%9F%D0%BE%D1%85%D0%B8%D1%89%D0%B5%D0%BD%D0%BD%D0%BE%D0%B5_%D0%BF%D0%B8%D1%81%D1%8C%D0%BC%D0%BE"),
                List.of());
        ParseResult result = new HeuristicFactParser().parseAll(List.of(raw));
        StructuredFact fact = result.getFacts().get(0);
        assertEquals(FactType.ARTWORK, fact.getType());
        assertEquals("Украденное письмо", fact.getTitle());
        assertEquals("Эдгар Аллан По", fact.getAuthor());
    }

    @Test
    void parsesTermDefinitionDash() {
        RawMessage raw = new RawMessage(5L, "Птицы — комедия Аристофана", List.of(), List.of());
        StructuredFact fact = new HeuristicFactParser().parseAll(List.of(raw)).getFacts().get(0);
        assertEquals(FactType.TERM, fact.getType());
        assertEquals("Птицы", fact.getTerm());
        assertEquals("комедия Аристофана", fact.getFact());
    }

    @Test
    void parsesLinkOnlyAsTerm() {
        RawMessage raw = new RawMessage(6L, "",
                List.of("https://ru.wikipedia.org/wiki/%D0%AD%D1%84%D1%84%D0%B5%D0%BA%D1%82_%D0%A4%D0%BB%D0%B8%D0%BD%D0%BD%D0%B0"),
                List.of());
        StructuredFact fact = new HeuristicFactParser().parseAll(List.of(raw)).getFacts().get(0);
        assertEquals(FactType.TERM, fact.getType());
        assertEquals("Эффект Флинна", fact.getTerm());
    }

    @Test
    void skipsLinkOnlyWhenConfigured() {
        RawMessage raw = new RawMessage(7L, "",
                List.of("https://ru.wikipedia.org/wiki/Test"),
                List.of());
        ParseResult result = new HeuristicFactParser(new ParseOptions(true, false, false)).parseAll(List.of(raw));
        assertTrue(result.getFacts().isEmpty());
        assertEquals(1, result.getSkipped());
    }

    @Test
    void parsesLocatedInRelation() {
        RawMessage raw = new RawMessage(8L,
                "Пентагон находится в штате Вирджиния, округе Арлингтон",
                List.of(), List.of());
        StructuredFact fact = new HeuristicFactParser().parseAll(List.of(raw)).getFacts().get(0);
        assertEquals(FactType.RELATION, fact.getType());
        assertEquals(RelationType.LOCATED_IN, fact.getRelation());
        assertEquals("Пентагон", fact.getChild());
    }

    @Test
    void telegramReaderSkipsServiceMessages() throws Exception {
        assumeTrue(TELEGRAM_EXPORT.toFile().exists(), "telegram export not available");
        TelegramJsonReader reader = new TelegramJsonReader();
        List<RawMessage> messages = reader.readMessages(TELEGRAM_EXPORT);
        assertFalse(messages.isEmpty());
        assertTrue(messages.stream().noneMatch(RawMessage::isBlank));
    }

    @Test
    void parsesWikiLinkWithAuthorComment() {
        RawMessage raw = new RawMessage(9L, " — Евтушенко",
                List.of("https://ru.wikipedia.org/wiki/%D0%A2%D0%B0%D0%BD%D0%BA%D0%B8_%D0%B8%D0%B4%D1%83%D1%82_%D0%BF%D0%BE_%D0%9F%D1%80%D0%B0%D0%B3%D0%B5"),
                List.of());
        StructuredFact fact = new HeuristicFactParser().parseAll(List.of(raw)).getFacts().get(0);
        assertEquals("Евтушенко", fact.getName());
        assertEquals("Танки идут по Праге", fact.getWork());
    }

    @Test
    void parsesQuestionWithEmDash() {
        RawMessage raw = new RawMessage(10L,
                "Сторожевая собака не лаяла — кто автор романа??",
                List.of(), List.of());
        StructuredFact fact = new HeuristicFactParser().parseAll(List.of(raw)).getFacts().get(0);
        assertEquals("Сторожевая собака не лаяла", fact.getTerm());
        assertTrue(fact.getFact().contains("кто автор"));
    }

    @Test
    void endToEndFromTelegramExport(@TempDir Path tempDir) throws Exception {
        assumeTrue(TELEGRAM_EXPORT.toFile().exists(), "telegram export not available");

        TelegramJsonReader reader = new TelegramJsonReader();
        List<RawMessage> messages = reader.readMessages(TELEGRAM_EXPORT).stream().limit(200).toList();
        ParseResult parseResult = new HeuristicFactParser(new ParseOptions(false, false, false)).parseAll(messages);
        assertFalse(parseResult.getFacts().isEmpty());

        CardGenerator generator = new CardGenerator(new SimpleMorphology(), new RuleBasedCardEnricher());
        assertFalse(generator.generateAll(parseResult.getFacts()).isEmpty());
    }
}
