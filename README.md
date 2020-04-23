# openfaas-demo

This project provides a set of three OpenFaaS functions that demonstrate three methods of OpenFaaS function I/O.

- emitter: A function that is triggered via HTTP requests or as a cron job, and writes a RabbitMQ message each time it runs.

- batcher: A long-running microservice that continuously reads messages from a RabbitMQ queue, consolidates them into batches, and writes those batches to a new queue.

- decoder: A function that is triggered by RabbitMQ messages (using the 3rd party RabbitMQ connector) and writes output to stderr.

### emitter

The emitter function produces a JSON message containing the current datetime and submits it to a RabbitMQ server. It is set up to run every minute.

Sample output:
```buildoutcfg
[
  "VGhlIGN1cnJlbnQgdGltZSBpczogMjAyMC0wNC0yM1QwNDowMjo0MS45NDgyODUg"
]
```
The above value decodes to:
```
"The current time is: 2020-04-23T04:02:41.948285"
``` 

### batcher

The batcher function is actually a microservice. This service continuously reads messages from a RabbitMQ queue, batching them together. It writes a batch of messages to a new queue (as a single RabbitMQ message) once the batch reaches a predefined size or a predefined time threshold has elapsed.

Sample output:

```
[
  "VGhlIGN1cnJlbnQgdGltZSBpczogMjAyMC0wNC0yM1QwNDowMjo0MS45NDgyODUg",
  "VGhlIGN1cnJlbnQgdGltZSBpczogMjAyMC0wNC0yM1QwNDoxMDoxNi4xODE2NDQg",
  "VGhlIGN1cnJlbnQgdGltZSBpczogMjAyMC0wNC0yM1QwNDoxMDoyNi45MjQwNTIg"
]
```

HTTP requests to the batcher function return a status update.

```commandline
Processed 34 messages in 8 batches since 2020-04-23 03:51:02.674371.
```

### decoder

The decoder function takes input of the form produced by the batcher, and decodes and logs each line. It is designed to be configured for use with the OpenFaaS RabbitMQ connector, so that it is triggered for each message produced by the batcher.

Sample output:
```commandline
2020-04-23T04:12:00Z 2020-04-23 04:12:00,513 - function.handler - INFO - The current time is: 2020-04-23T04:10:26.924052
2020-04-23T04:12:00Z 2020-04-23 04:12:00,513 - function.handler - INFO - The current time is: 2020-04-23T04:11:00.294420
2020-04-23T04:12:00Z 2020-04-23 04:12:00,513 - function.handler - INFO - The current time is: 2020-04-23T04:12:00.297718
```
