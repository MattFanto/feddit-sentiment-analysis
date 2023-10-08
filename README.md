
# Feddit Sentiment Analysis

A web API predicting if comments on a given subfeddit or category are positive or negative.
The project is implemented with FastAPI and Docker.

## How-to-run

The webapp sentiment analysis model relies on external API for the classification.
By default, a simple mocked model is enabled, if you don't care about the model just run:
```
docker-compose up -d --build
```

If you want to use the external API you have 2 options:
- [AWS Comprehend](https://aws.amazon.com/comprehend/pricing/) (recommended)
- [OpenAI ChatGPT](https://openai.com/blog/openai-api) (not recommended)

The OpenAI approach is an alternative if you don't work with AWS.
Please keep in mind the following limitation for the OpenAI approach:
* I didn't implement input sanitization
* I didn't optimize the prompt
* is much more expensive
* is 2 times slower

Depending on your preferences and possibility (e.g. you may not have AWS account available),
you can choose one model or the other via ENV configuration.

* OpenAI approach:
```shell
SENTIMENT_MODEL=openai OPENAI_API_KEY=<your-openai-key> docker-compose up --build
```

* AWS Comprehend approach:
```shell
PREDICTIONS_MODEL=aws_comprehend \
AWS_ACCESS_KEY_ID=<your-aws-access-key-id> \
AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key> \
docker-compose up --build
```

## API
Check [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) for OpenAPI documentation.

## Monitoring

To monitor the application I provided 2 tools:
* JSON logger, printing to stdout and eventually collected by a log collector
* Prometheus' metrics, exposed at `http://localhost:8000/metrics` and accessible at `http://localhost:9090`

Prometheus is more a proof of concept, I didn't implement any alerting or dashboard.
In general if available there are better tools than Prometheus covering better distributed tracing aspect like NewRelic, Sentry, DataDog, Elastic APM, etc.


## Tests

For the sake of simplicity and time saving I created only 2 tests:
* Sample smoke test running against a live service
* Simple unit test for the AWS model
