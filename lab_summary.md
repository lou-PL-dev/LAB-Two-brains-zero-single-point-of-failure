# Lab Summary

This lab involved building a multi-provider news summarizer combining NewsAPI, OpenAI, and Cohere into a single pipeline with fallback logic and cost tracking. 

 
I learned how fallback logic keeps the app resilient when a provider fails, how cost tracking differs slightly across providers with different pricing and usage response formats, and how async processing (using each provider's native async client instead of aiohttp) can speed up multi-article runs at no extra cost. 

For future improvements, I'd add a configurable cost ceiling that stops processing once the daily budget is reached.
