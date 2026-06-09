package com.quizlet.parser.telegram;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public final class TelegramJsonReader {

    private final ObjectMapper mapper = new ObjectMapper();

    public TelegramExport readExport(Path path) throws IOException {
        return mapper.readValue(path.toFile(), TelegramExport.class);
    }

    public List<RawMessage> readMessages(Path path) throws IOException {
        TelegramExport export = readExport(path);
        List<RawMessage> result = new ArrayList<>();
        for (TelegramMessage message : export.getMessages()) {
            if (!"message".equals(message.getType())) {
                continue;
            }
            RawMessage raw = MessageTextNormalizer.normalize(message.getId(), message.getText());
            if (!raw.isBlank()) {
                result.add(raw);
            }
        }
        return result;
    }
}
