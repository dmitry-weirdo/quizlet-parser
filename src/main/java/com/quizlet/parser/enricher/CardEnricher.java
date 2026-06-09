package com.quizlet.parser.enricher;

import com.quizlet.parser.model.Card;
import com.quizlet.parser.model.StructuredFact;

import java.util.List;

public interface CardEnricher {

    List<Card> enrich(StructuredFact fact);
}
