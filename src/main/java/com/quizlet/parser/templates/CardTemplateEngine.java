package com.quizlet.parser.templates;

import com.quizlet.parser.morph.GrammaticalCase;
import com.quizlet.parser.morph.RussianMorphology;
import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.RelationType;
import com.quizlet.parser.model.StructuredFact;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class CardTemplateEngine {

    private static final Pattern PLACEHOLDER = Pattern.compile("\\{([^}]+)}");

    private final Map<String, List<CardTemplate>> templatesByTypeName;
    private final RussianMorphology morphology;

    public CardTemplateEngine(Map<com.quizlet.parser.model.FactType, List<CardTemplate>> templates,
                              RussianMorphology morphology) {
        this.templatesByTypeName = new LinkedHashMap<>();
        for (var entry : templates.entrySet()) {
            this.templatesByTypeName.put(entry.getKey().name(), entry.getValue());
        }
        this.morphology = morphology;
    }

    public List<Card> generate(StructuredFact fact) {
        List<CardTemplate> templates = templatesByTypeName.getOrDefault(fact.getType().name(), List.of());
        Map<String, String> context = buildContext(fact);
        List<Card> cards = new ArrayList<>();

        for (CardTemplate template : templates) {
            if (!matchesRelation(template, fact.getRelation())) {
                continue;
            }
            if (!hasRequiredFields(template, context)) {
                continue;
            }
            String question = render(template.question(), context);
            String answer = render(template.answer(), context);
            if (isValidCard(question, answer)) {
                cards.add(new Card(question, answer));
            }
        }
        return cards;
    }

    private boolean matchesRelation(CardTemplate template, RelationType relation) {
        if (template.relations().isEmpty()) {
            return true;
        }
        if (relation == null) {
            return false;
        }
        return template.relations().contains(relation.name());
    }

    private boolean hasRequiredFields(CardTemplate template, Map<String, String> context) {
        for (String field : template.required()) {
            String baseField = field.contains(":") ? field.substring(0, field.indexOf(':')) : field;
            if (!context.containsKey(baseField) || context.get(baseField).isBlank()) {
                return false;
            }
        }
        return true;
    }

    private Map<String, String> buildContext(StructuredFact fact) {
        Map<String, String> context = new LinkedHashMap<>(fact.asFieldMap());

        if (fact.getYear() != null) {
            context.put("year_suffix", ", " + fact.getYear());
        } else {
            context.put("year_suffix", "");
        }

        if (fact.getAuthor() != null && fact.getTitle() != null && !context.containsKey("author")) {
            context.put("author", fact.getAuthor());
        }
        if (fact.getChild() != null && !context.containsKey("child")) {
            context.put("child", fact.getChild());
        }
        if (fact.getParent() != null && !context.containsKey("parent")) {
            context.put("parent", fact.getParent());
        }
        if (fact.getSource() != null && !context.containsKey("source")) {
            context.put("source", fact.getSource());
        }
        if (fact.getTarget() != null && !context.containsKey("target")) {
            context.put("target", fact.getTarget());
        }

        return context;
    }

    private String render(String template, Map<String, String> context) {
        Matcher matcher = PLACEHOLDER.matcher(template);
        StringBuffer buffer = new StringBuffer();
        while (matcher.find()) {
            String token = matcher.group(1);
            String replacement = resolveToken(token, context);
            matcher.appendReplacement(buffer, Matcher.quoteReplacement(replacement));
        }
        matcher.appendTail(buffer);
        return buffer.toString().replaceAll("\\s+", " ").trim();
    }

    private String resolveToken(String token, Map<String, String> context) {
        int colon = token.indexOf(':');
        if (colon < 0) {
            return context.getOrDefault(token, "");
        }

        String field = token.substring(0, colon);
        String modifier = token.substring(colon + 1);
        String value = context.getOrDefault(field, "");
        if (value.isBlank()) {
            return "";
        }

        return switch (modifier) {
            case "genitive" -> morphology.inflect(value, GrammaticalCase.GENITIVE);
            case "accusative" -> morphology.inflect(value, GrammaticalCase.ACCUSATIVE);
            case "prepositional" -> morphology.inflect(value, GrammaticalCase.PREPOSITIONAL);
            case "prepositional_phrase" -> morphology.prepositionalPhrase(value);
            case "pronoun_nominative" -> morphology.pronounNominative(value);
            case "pronoun_prepositional" -> morphology.pronounPrepositional(value);
            case "pronoun_genitive" -> morphology.pronounGenitive(value);
            default -> value;
        };
    }

    private boolean isValidCard(String question, String answer) {
        if (question == null || question.isBlank()
                || answer == null || answer.isBlank()
                || question.contains("{") || answer.contains("{")) {
            return false;
        }
        return !question.trim().equalsIgnoreCase(answer.trim());
    }
}
