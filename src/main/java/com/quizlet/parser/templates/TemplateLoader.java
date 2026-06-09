package com.quizlet.parser.templates;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.quizlet.parser.model.FactType;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public final class TemplateLoader {

    private static final ObjectMapper YAML = new ObjectMapper(new YAMLFactory());

    private TemplateLoader() {
    }

    @SuppressWarnings("unchecked")
    public static Map<FactType, List<CardTemplate>> loadFromClasspath() throws IOException {
        try (InputStream input = TemplateLoader.class.getClassLoader().getResourceAsStream("templates.yaml")) {
            if (input == null) {
                throw new IOException("templates.yaml not found on classpath");
            }
            Map<String, Object> root = YAML.readValue(input, Map.class);
            Map<String, List<Map<String, Object>>> rawTemplates =
                    (Map<String, List<Map<String, Object>>>) root.get("templates");

            Map<FactType, List<CardTemplate>> result = new EnumMap<>(FactType.class);
            for (Map.Entry<String, List<Map<String, Object>>> entry : rawTemplates.entrySet()) {
                FactType type = FactType.valueOf(entry.getKey());
                List<CardTemplate> templates = new ArrayList<>();
                for (Map<String, Object> item : entry.getValue()) {
                    templates.add(parseTemplate(item));
                }
                result.put(type, templates);
            }
            return result;
        }
    }

    @SuppressWarnings("unchecked")
    private static CardTemplate parseTemplate(Map<String, Object> item) {
        String id = (String) item.get("id");
        String question = (String) item.get("question");
        String answer = (String) item.get("answer");
        List<String> required = (List<String>) item.get("required");
        List<String> relations = (List<String>) item.get("relations");
        return new CardTemplate(id, required, question, answer, relations);
    }
}
