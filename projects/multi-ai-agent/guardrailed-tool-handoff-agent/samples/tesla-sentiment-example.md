# Tesla Sentiment Example

Example prompt:

`What is the current market sentiment about Tesla?`

Intended workflow:

1. `Planner` receives the prompt and passes through the input guardrail.
2. `Planner` creates a scoped `SearchPlan`.
3. `Planner` hands off to `Writer`.
4. `Writer` decides sentiment analysis is needed and calls `SentimentAgent` as a tool.
5. `SentimentAgent` uses `SearchAgent` as its nested specialist search tool.
6. `SearchAgent` calls Tavily and returns a grounded summary.
7. `SentimentAgent` classifies overall sentiment as positive, negative, or neutral.
8. `Writer` produces the final report.

Expected trace hierarchy on the OpenAI platform:

- `Planner`
- `Writer`
- `SentimentAgent`
- `SearchAgent`
- `tavily_search`
