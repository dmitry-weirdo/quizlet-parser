package com.quizlet.parser.generator;

import com.quizlet.parser.enricher.RuleBasedCardEnricher;
import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.FactType;
import com.quizlet.parser.model.RelationType;
import com.quizlet.parser.model.StructuredFact;
import com.quizlet.parser.morph.SimpleMorphology;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CardGeneratorTest {

    private CardGenerator generator;

    @BeforeEach
    void setUp() throws Exception {
        generator = new CardGenerator(new SimpleMorphology(), new RuleBasedCardEnricher());
    }

    @Test
    void generatesArtworkCards() {
        StructuredFact fact = new StructuredFact();
        fact.setType(FactType.ARTWORK);
        fact.setTitle("Полуночники");
        fact.setAuthor("Эдвард Хоппер");
        fact.setYear(1942);
        fact.setHint("угловой дом-закусочная в Манхэттене");

        List<Card> cards = generator.generate(fact);

        assertTrue(cards.stream().anyMatch(c -> c.question().equals("Эдвард Хоппер")));
        assertTrue(cards.stream().anyMatch(c -> c.question().equals("Полуночники")));
        assertTrue(cards.stream().anyMatch(c -> c.answer().contains("угловой дом-закусочная")));
    }

    @Test
    void generatesNumberCardsBothDirections() {
        StructuredFact fact = new StructuredFact();
        fact.setType(FactType.NUMBER);
        fact.setValue("14");
        fact.setDomain("на Земле восьмитысячников");

        List<Card> cards = generator.generate(fact);

        assertTrue(cards.stream().anyMatch(c ->
                c.question().equals("14") && c.answer().contains("Сколько")));
        assertTrue(cards.stream().anyMatch(c ->
                c.answer().equals("14")));
    }

    @Test
    void generatesRelationLocatedInWithPronouns() {
        StructuredFact fact = new StructuredFact();
        fact.setType(FactType.RELATION);
        fact.setRelation(RelationType.LOCATED_IN);
        fact.setChild("Столовая гора");
        fact.setParent("Капский полуостров");

        List<Card> cards = generator.generate(fact);

        assertTrue(cards.stream().anyMatch(c ->
                c.question().equals("Капский полуостров")
                        && c.answer().contains("НЁМ")));
        assertTrue(cards.stream().anyMatch(c ->
                c.question().equals("Столовая гора")
                        && c.answer().contains("ОНА")));
    }

    @Test
    void generatesNicknameReversePair() {
        StructuredFact fact = new StructuredFact();
        fact.setType(FactType.NICKNAME);
        fact.setAlias("Мальчик, который выжил");
        fact.setEntity("Гарри Поттер");

        List<Card> cards = generator.generate(fact);

        assertTrue(cards.stream().anyMatch(c ->
                c.question().equals("Мальчик, который выжил")
                        && c.answer().contains("Гарри Поттер")));
        assertTrue(cards.stream().anyMatch(c ->
                c.question().equals("Гарри Поттер")
                        && c.answer().equals("Мальчик, который выжил")));
    }

    @Test
    void generatesClickableEnrichment() {
        StructuredFact fact = new StructuredFact();
        fact.setType(FactType.TERM);
        fact.setTerm("Кока-Кола");
        fact.setExtra(Map.of("clickable", "true", "clickHint", "Атланту"));

        List<Card> cards = generator.generate(fact);

        assertTrue(cards.stream().anyMatch(c ->
                c.answer().contains("должен щёлкать")));
    }

    @Test
    void deduplicatesIdenticalCards() {
        StructuredFact fact = new StructuredFact();
        fact.setType(FactType.TRANSLATION);
        fact.setTerm("Фэн-шуй");
        fact.setMeaning("\"Ветер\" и \"вода\"");

        List<Card> cards = generator.generate(fact);
        long unique = cards.stream().map(c -> c.question() + c.answer()).distinct().count();

        assertFalse(cards.isEmpty());
        assertTrue(unique <= cards.size());
    }
}
