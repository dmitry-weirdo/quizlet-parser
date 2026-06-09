package com.quizlet.parser.telegram;

import com.quizlet.parser.model.FactType;
import com.quizlet.parser.model.RelationType;
import com.quizlet.parser.model.StructuredFact;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class HeuristicFactParser {

    private static final Pattern AUTHOR_QUOTE = Pattern.compile("^([\\p{L}][\\p{L}\\s.'-]{0,60}):\\s*(.+)$");
    private static final Pattern LOCATED_IN = Pattern.compile("^(.+?)\\s+находится\\s+(?:в|на)\\s+(.+)$", Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE);
    private static final Pattern TERM_YEAR = Pattern.compile("^(.+?)\\s*[—–-]\\s*(\\d{4})\\s*год\\.?$");
    private static final Pattern EM_DASH_PAIR = Pattern.compile("^(.+?)\\s*[—–-]\\s*(.+)$");
    private static final Pattern LINK_COMMENT = Pattern.compile("^[\\s—–-]*[—–-]\\s*(.+)$");
    private static final Pattern YEAR_IN_TEXT = Pattern.compile("\\b(1[89]\\d{2}|20\\d{2})\\b");
    private static final Pattern TITLE_AUTHOR_TRAIL = Pattern.compile("^(.+?)\\s*[—–-]\\s*(.+?)\\s*[—–-]\\s*$");

    private final WikipediaSummaryClient wikiClient;
    private final ParseOptions options;

    public HeuristicFactParser() {
        this(ParseOptions.defaults());
    }

    public HeuristicFactParser(ParseOptions options) {
        this(options, new WikipediaSummaryClient());
    }

    HeuristicFactParser(ParseOptions options, WikipediaSummaryClient wikiClient) {
        this.options = options != null ? options : ParseOptions.defaults();
        this.wikiClient = wikiClient;
    }

    public ParseResult parseAll(List<RawMessage> messages) {
        ParseResult result = new ParseResult();
        for (RawMessage message : messages) {
            parseMessage(message, result);
        }
        return result;
    }

    public void parseMessage(RawMessage message, ParseResult result) {
        if (message.isBlank()) {
            result.incrementSkipped();
            return;
        }

        if (message.isLinkOnly()) {
            handleLinkOnly(message, result);
            return;
        }

        if (options.skipOrphan() && isOrphan(message.plainText(), message.links())) {
            result.incrementSkipped();
            return;
        }

        List<StructuredFact> facts = parseRichMessage(message);
        if (facts.isEmpty()) {
            result.incrementSkipped();
            result.addWarning("Could not parse message " + message.messageId() + ": " + message.plainText());
            return;
        }
        result.addFacts(facts);
    }

    private void handleLinkOnly(RawMessage message, ParseResult result) {
        if (options.skipLinkOnly()) {
            result.incrementSkipped();
            return;
        }
        String link = message.links().get(0);
        StructuredFact fact = factFromLink(link, null);
        applyHashtags(fact, message.hashtags());
        if (fact.getTerm() == null || fact.getTerm().isBlank()) {
            result.incrementSkipped();
            result.addWarning("Link-only message without title: " + message.messageId());
            return;
        }
        result.addFact(fact);
    }

    private List<StructuredFact> parseRichMessage(RawMessage message) {
        String text = message.plainText();
        List<String> links = message.links();

        if (!links.isEmpty() && LINK_COMMENT.matcher(text).matches()) {
            String comment = LINK_COMMENT.matcher(text).replaceFirst("$1").trim();
            StructuredFact fact = factFromLink(links.get(0), comment);
            applyHashtags(fact, message.hashtags());
            return List.of(fact);
        }

        Matcher titleAuthor = TITLE_AUTHOR_TRAIL.matcher(text);
        if (titleAuthor.matches() && !links.isEmpty()) {
            StructuredFact fact = new StructuredFact();
            fact.setType(FactType.ARTWORK);
            fact.setTitle(titleAuthor.group(1).trim());
            fact.setAuthor(titleAuthor.group(2).trim());
            enrichFromLink(fact, links.get(0));
            applyHashtags(fact, message.hashtags());
            return List.of(fact);
        }

        if (!links.isEmpty() && !text.isBlank() && !text.contains(" — ") && !text.startsWith("—")) {
            StructuredFact fact = new StructuredFact();
            fact.setType(FactType.ARTWORK);
            fact.setTitle(text.trim());
            enrichFromLink(fact, links.get(0));
            applyHashtags(fact, message.hashtags());
            return List.of(fact);
        }

        Matcher authorQuote = AUTHOR_QUOTE.matcher(text);
        if (authorQuote.matches() && !text.contains("http")) {
            StructuredFact fact = new StructuredFact();
            fact.setType(FactType.QUOTE);
            fact.setAuthor(authorQuote.group(1).trim());
            fact.setQuote(authorQuote.group(2).trim());
            applyHashtags(fact, message.hashtags());
            return List.of(fact);
        }

        Matcher located = LOCATED_IN.matcher(text);
        if (located.matches()) {
            StructuredFact fact = new StructuredFact();
            fact.setType(FactType.RELATION);
            fact.setRelation(RelationType.LOCATED_IN);
            fact.setChild(located.group(1).trim());
            fact.setParent(located.group(2).trim());
            applyHashtags(fact, message.hashtags());
            return List.of(fact);
        }

        Matcher termYear = TERM_YEAR.matcher(text);
        if (termYear.matches()) {
            List<StructuredFact> facts = new ArrayList<>();
            StructuredFact term = new StructuredFact();
            term.setType(FactType.TERM);
            term.setTerm(termYear.group(1).trim());
            term.setFact("Событие / объект, связанный с " + termYear.group(2).trim() + " годом");
            applyHashtags(term, message.hashtags());
            facts.add(term);

            StructuredFact year = new StructuredFact();
            year.setType(FactType.YEAR);
            year.setYear(Integer.parseInt(termYear.group(2)));
            year.setEvent(termYear.group(1).trim());
            applyHashtags(year, message.hashtags());
            facts.add(year);
            return facts;
        }

        Matcher dashPair = EM_DASH_PAIR.matcher(text);
        if (dashPair.matches() && links.isEmpty()) {
            String left = dashPair.group(1).trim();
            String right = dashPair.group(2).trim();

            if (isQuestionFragment(right) || text.trim().endsWith("?")) {
                StructuredFact fact = new StructuredFact();
                fact.setType(FactType.TERM);
                fact.setTerm(left);
                fact.setFact(text.trim());
                applyHashtags(fact, message.hashtags());
                return List.of(fact);
            }

            Matcher yearMatcher = YEAR_IN_TEXT.matcher(right);
            if (yearMatcher.find()) {
                StructuredFact year = new StructuredFact();
                year.setType(FactType.YEAR);
                year.setYear(Integer.parseInt(yearMatcher.group(1)));
                year.setEvent(left);
                applyHashtags(year, message.hashtags());
                return List.of(year);
            }

            if (looksLikePersonPair(left, right)) {
                StructuredFact person = new StructuredFact();
                person.setType(FactType.PERSON);
                person.setName(left);
                person.setFact("Связано с: " + right);
                applyHashtags(person, message.hashtags());
                return List.of(person);
            }

            StructuredFact term = new StructuredFact();
            term.setType(FactType.TERM);
            term.setTerm(left);
            term.setFact(right);
            applyHashtags(term, message.hashtags());
            return List.of(term);
        }

        if (text.endsWith("?")) {
            StructuredFact fact = new StructuredFact();
            fact.setType(FactType.TERM);
            fact.setTerm(extractQuestionSubject(text));
            fact.setFact(text.trim());
            applyHashtags(fact, message.hashtags());
            return List.of(fact);
        }

        if (!text.isBlank()) {
            if (options.skipOrphan() && isOrphan(text, links)) {
                return List.of();
            }
            StructuredFact fact = new StructuredFact();
            fact.setType(FactType.TERM);
            fact.setTerm(text.trim());
            fact.setFact(text.trim());
            applyHashtags(fact, message.hashtags());
            return List.of(fact);
        }

        return List.of();
    }

    private StructuredFact factFromLink(String link, String comment) {
        StructuredFact fact = new StructuredFact();
        fact.setType(FactType.TERM);
        fact.getExtra().put("link", link);

        if (WikipediaTitleExtractor.isWikipediaUrl(link)) {
            String title = WikipediaTitleExtractor.titleFromUrl(link);
            fact.setTerm(title);
            if (options.fetchWiki()) {
                wikiClient.fetchExtractFromUrl(link).ifPresent(extract -> fact.setFact(extract));
            }
            if (comment != null && !comment.isBlank()) {
                fact.getExtra().put("comment", comment);
                if (looksLikePersonName(comment)) {
                    fact.setType(FactType.PERSON);
                    fact.setName(comment);
                    fact.setWork(title);
                    fact.setFact("Автор «" + title + "»");
                } else if (fact.getFact() == null || fact.getFact().isBlank()) {
                    fact.setFact(comment);
                }
            } else if (fact.getFact() == null || fact.getFact().isBlank()) {
                fact.setFact(title);
            }
        } else {
            fact.setTerm(comment != null && !comment.isBlank() ? comment : link);
            fact.setFact(link);
        }
        return fact;
    }

    private void enrichFromLink(StructuredFact fact, String link) {
        fact.getExtra().put("link", link);
        if (WikipediaTitleExtractor.isWikipediaUrl(link)) {
            String title = WikipediaTitleExtractor.titleFromUrl(link);
            if (fact.getTitle() == null || fact.getTitle().isBlank()) {
                fact.setTitle(title);
            }
            if (options.fetchWiki()) {
                wikiClient.fetchExtractFromUrl(link).ifPresent(fact::setHint);
            }
            if (fact.getHint() == null || fact.getHint().isBlank()) {
                fact.setHint("Wikipedia: " + title);
            }
        } else {
            fact.setHint("Ссылка: " + link);
        }
    }

    private static void applyHashtags(StructuredFact fact, List<String> hashtags) {
        if (hashtags == null || hashtags.isEmpty()) {
            return;
        }
        fact.getExtra().put("category", String.join(", ", hashtags));
    }

    private static String extractQuestionSubject(String question) {
        String trimmed = question.trim();
        if (trimmed.length() <= 80) {
            return trimmed;
        }
        int space = trimmed.indexOf(' ', 40);
        return space > 0 ? trimmed.substring(0, space) + "..." : trimmed.substring(0, 80) + "...";
    }

    private static boolean looksLikePersonPair(String left, String right) {
        return left.split("\\s+").length >= 2 && looksLikePersonName(left) && right.length() <= 40;
    }

    private static boolean isQuestionFragment(String value) {
        if (value == null || value.isBlank()) {
            return false;
        }
        String lower = value.toLowerCase();
        return value.contains("?")
                || lower.startsWith("кто ")
                || lower.startsWith("что ")
                || lower.startsWith("где ")
                || lower.startsWith("когда ")
                || lower.startsWith("какой ")
                || lower.startsWith("какая ")
                || lower.startsWith("какое ");
    }

    private static boolean isOrphan(String text, List<String> links) {
        if (text == null || text.isBlank()) {
            return true;
        }
        if (!links.isEmpty()) {
            return false;
        }
        String normalized = text.trim();
        return !normalized.contains(" — ")
                && !normalized.contains(":")
                && !normalized.endsWith("?")
                && normalized.split("\\s+").length <= 3;
    }

    private static boolean looksLikePersonName(String value) {
        if (value == null || value.isBlank()) {
            return false;
        }
        return value.split("\\s+").length <= 4 && Character.isUpperCase(value.charAt(0));
    }
}
