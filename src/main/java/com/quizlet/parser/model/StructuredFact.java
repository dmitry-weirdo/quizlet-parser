package com.quizlet.parser.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.LinkedHashMap;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class StructuredFact {

    private FactType type;
    private RelationType relation;
    private String name;
    private String title;
    private String author;
    private Integer year;
    private String value;
    private String domain;
    private String event;
    private String alias;
    private String entity;
    private String term;
    private String meaning;
    private String place;
    private String fact;
    private String hint;
    private String role;
    private String quote;
    private String work;
    private String source;
    private String target;
    private String child;
    private String parent;
    private String answerHint;
    private Map<String, String> extra = new LinkedHashMap<>();

    public FactType getType() {
        return type;
    }

    public void setType(FactType type) {
        this.type = type;
    }

    public RelationType getRelation() {
        return relation;
    }

    public void setRelation(RelationType relation) {
        this.relation = relation;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public Integer getYear() {
        return year;
    }

    public void setYear(Integer year) {
        this.year = year;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public String getDomain() {
        return domain;
    }

    public void setDomain(String domain) {
        this.domain = domain;
    }

    public String getEvent() {
        return event;
    }

    public void setEvent(String event) {
        this.event = event;
    }

    public String getAlias() {
        return alias;
    }

    public void setAlias(String alias) {
        this.alias = alias;
    }

    public String getEntity() {
        return entity;
    }

    public void setEntity(String entity) {
        this.entity = entity;
    }

    public String getTerm() {
        return term;
    }

    public void setTerm(String term) {
        this.term = term;
    }

    public String getMeaning() {
        return meaning;
    }

    public void setMeaning(String meaning) {
        this.meaning = meaning;
    }

    public String getPlace() {
        return place;
    }

    public void setPlace(String place) {
        this.place = place;
    }

    public String getFact() {
        return fact;
    }

    public void setFact(String fact) {
        this.fact = fact;
    }

    public String getHint() {
        return hint;
    }

    public void setHint(String hint) {
        this.hint = hint;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getQuote() {
        return quote;
    }

    public void setQuote(String quote) {
        this.quote = quote;
    }

    public String getWork() {
        return work;
    }

    public void setWork(String work) {
        this.work = work;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public String getTarget() {
        return target;
    }

    public void setTarget(String target) {
        this.target = target;
    }

    public String getChild() {
        return child;
    }

    public void setChild(String child) {
        this.child = child;
    }

    public String getParent() {
        return parent;
    }

    public void setParent(String parent) {
        this.parent = parent;
    }

    public String getAnswerHint() {
        return answerHint;
    }

    public void setAnswerHint(String answerHint) {
        this.answerHint = answerHint;
    }

    public Map<String, String> getExtra() {
        return extra;
    }

    public void setExtra(Map<String, String> extra) {
        this.extra = extra != null ? extra : new LinkedHashMap<>();
    }

    public Map<String, String> asFieldMap() {
        Map<String, String> fields = new LinkedHashMap<>();
        putIfPresent(fields, "name", name);
        putIfPresent(fields, "title", title);
        putIfPresent(fields, "author", author);
        putIfPresent(fields, "year", year != null ? String.valueOf(year) : null);
        putIfPresent(fields, "value", value);
        putIfPresent(fields, "domain", domain);
        putIfPresent(fields, "event", event);
        putIfPresent(fields, "alias", alias);
        putIfPresent(fields, "entity", entity);
        putIfPresent(fields, "term", term);
        putIfPresent(fields, "meaning", meaning);
        putIfPresent(fields, "place", place);
        putIfPresent(fields, "fact", fact);
        putIfPresent(fields, "hint", hint);
        putIfPresent(fields, "role", role);
        putIfPresent(fields, "quote", quote);
        putIfPresent(fields, "work", work);
        putIfPresent(fields, "source", source);
        putIfPresent(fields, "target", target);
        putIfPresent(fields, "child", child);
        putIfPresent(fields, "parent", parent);
        putIfPresent(fields, "answerHint", answerHint);
        fields.putAll(extra);
        return fields;
    }

    private static void putIfPresent(Map<String, String> map, String key, String value) {
        if (value != null && !value.isBlank()) {
            map.put(key, value);
        }
    }
}
