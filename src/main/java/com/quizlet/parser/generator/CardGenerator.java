package com.quizlet.parser.generator;

import com.quizlet.parser.enricher.CardEnricher;
import com.quizlet.parser.enricher.RuleBasedCardEnricher;
import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.FactType;
import com.quizlet.parser.model.StructuredFact;
import com.quizlet.parser.morph.MystemMorphology;
import com.quizlet.parser.morph.RussianMorphology;
import com.quizlet.parser.morph.SimpleMorphology;
import com.quizlet.parser.templates.CardTemplateEngine;
import com.quizlet.parser.templates.TemplateLoader;

import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

public final class CardGenerator {

    private final CardTemplateEngine templateEngine;
    private final CardEnricher enricher;
    private final RussianMorphology morphology;

    public CardGenerator() throws IOException {
        this(createDefaultMorphology(), new RuleBasedCardEnricher());
    }

    public CardGenerator(RussianMorphology morphology, CardEnricher enricher) throws IOException {
        this.morphology = morphology;
        this.templateEngine = new CardTemplateEngine(TemplateLoader.loadFromClasspath(), morphology);
        this.enricher = enricher;
    }

    public List<Card> generate(StructuredFact fact) {
        StructuredFact normalized = normalize(fact);
        List<Card> cards = new ArrayList<>(templateEngine.generate(normalized));
        cards.addAll(enricher.enrich(normalized));
        return deduplicate(cards);
    }

    public List<Card> generateAll(List<StructuredFact> facts) {
        List<Card> all = new ArrayList<>();
        for (StructuredFact fact : facts) {
            all.addAll(generate(fact));
        }
        return deduplicate(all);
    }

    public RussianMorphology getMorphology() {
        return morphology;
    }

    private StructuredFact normalize(StructuredFact fact) {
        if (fact.getType() == FactType.RELATION && fact.getRelation() != null) {
            switch (fact.getRelation()) {
                case LOCATED_IN -> {
                    if (fact.getChild() == null && fact.getTarget() != null) {
                        fact.setChild(fact.getTarget());
                    }
                    if (fact.getParent() == null && fact.getPlace() != null) {
                        fact.setParent(fact.getPlace());
                    }
                }
                case AUTHOR_OF, CREATED_BY -> {
                    if (fact.getAuthor() == null && fact.getSource() != null) {
                        fact.setAuthor(fact.getSource());
                    }
                    if (fact.getTitle() == null && fact.getTarget() != null) {
                        fact.setTitle(fact.getTarget());
                    }
                }
                case NAMED_AFTER -> {
                    if (fact.getTarget() == null && fact.getTerm() != null) {
                        fact.setTarget(fact.getTerm());
                    }
                    if (fact.getSource() == null && fact.getEntity() != null) {
                        fact.setSource(fact.getEntity());
                    }
                }
                default -> {
                }
            }
        }
        return fact;
    }

    private List<Card> deduplicate(List<Card> cards) {
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

    private static RussianMorphology createDefaultMorphology() {
        MystemMorphology mystem = new MystemMorphology();
        return mystem.isAvailable() ? mystem : new SimpleMorphology();
    }
}
