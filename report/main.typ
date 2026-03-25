#import "@preview/ilm:1.4.0": *

#set text(lang: "en")

#show: ilm.with(
  title: [Weather Flow],
  author: "Andrea Galliano 85641A",
  date: datetime(year: 2026, month: 03, day: 26),
  abstract: [
    Real-Time weather telemetry via Apache Kafka
  ],
  table-of-contents: none, 
  listing-index: (enabled: false),
  chapter-pagebreak: false,
)

= Introduction
This project is about building and implementing a _*Cloud-Native*_ architecture for Real-Time weather telemetry using _Apache Kafka_. The system is designed to collect, process, and store Real-Time meteorological data from six different cities in Italy: Milan, Turin, Verona, Florence, Rome and Naples (the data is retrieved via _REST API_ available on #link("https://open-meteo.com/")[`open-meteo.com`]). In addition, a continuos stream of measurements (temperature, rainfall, wind speed...) is simulated by an external script and sent to the Kafka cluster. From there, the data is consumed in parallel by multiple microservices for specific purposes: Real-Time data visualization via a web dashboard, data storage in _NoSQL_ database and alert generation for extreme weather conditions, forwarded to a smartphone via Telegram bot. The main focus is to garantee the system's scalability, reliability, criptographic security and fault-tolerance.


= Architectural overview
The entire infrastructure is based on an architectural pattern with deacupled microservices. The communication is not direct, but rather mediated by a message broker, in this case Apache Kafka. This is the architectural overview of the system:

#figure(
  image("/img/system_overview.png", width: 52%),
  caption: [Architectural overview of the system.]
) <fig:arch-overview>


= Description of the system
== Components
The entire system is composed of the following components:
- *Weather-Poller*: Python script that periodically retrieves weather data from #link("https://open-meteo.com/")[`open-meteo.com`] for the six cities and sends it to the API-Producer.
- *API-Producer*: REST application that receives weather data in JSON format and sends it to the Kafka cluster. Thanks to _HTTP POST_ requests, the producer publishes the data to the main Kafka topic (`weather.telemetry`) instantly.
- *Dashboard*: A Real-Time web application built with *_Flask_*. Besides visualizing data, its backend integrates a custom "*Stress Test*" to simulate massive data ingestion, effectively showcasing _Apache Kafka_'s ability to handle high-throughput event queues and dynamic load balancing without performance degradation.
- *Storage*: Microservice responsible for consuming the data from the Kafka topic and storing it in a _*NoSQL database*_ (_MongoDB_).
- *Notifier*: Microservice that consumes the data from the Kafka topic and generates alerts for extreme weather conditions (e.g., high or low temperature, heavy rainfall, strong winds). If Notifier detects an extreme weather condition, it publishes an alert message to a specific Kafka topic (`weather.alerts`). Notifier is a Consumer, but also a Producer.
- *Telegram Forwarder*: Isolated microservice that only consumes alert messages from the `weather.alerts` topic and uses Telegram's API to forward notifications to the users' smartphones.

== Streaming processing and distributed coordination
The backbone of the architecture is rapresented by a distributed messaging cluster (it is the "_Single Source of Truth_") for alla the microservices:
- *Apache Kafka*: it manages data flow and divides it in *Topics* (`weather.telemetry` and `weather.alerts`). Kafka brokers push data to the Consumers, but they also act as immutable registers (with high performance) for microservices that pull data autonomously and at their own rithm.
- *ZooKeeper*: It is the distributed coordinator for the Kafka cluster. It manages and keep metadata in cluster, manage brokers' registration and leader election, and it also monitors the health of the cluster. Thanks to _ZooKeeper_, the system can automatically recover from failures and maintain high availability.

== Infrastructure as code and containerization
The entire architecture is based to be "_Cloud-Ready_", isolating processes in containers and making deployment universal and reproducible. The main tools used for this purpose are:
- *Docker*: each microservice is packeged in an isolated conainer, starting with a specific image (`python:3.11-slim`). This approach guaratees code portability and consistency across different environments.
- *Docker Compose*: used to orchestrate the deployment of all microservices (_Infrastructure as Code_). The `docker-compose.yml` file instances containers simultaneously, defines their dependencies and manages the network configuration. This allows for easy scaling and management of the entire system.

= Non-functional requirements
Industrial standards respected:
- *Fault Tolerance*: Kafka cluster is configured with a replication factor of 3. Data is replicated accross phisically separated nodes, so, in case of a node failure, _Zookeeper_ automatically promotes a backup replice (_ISR_) to a new leader whithin few milliseconds, without any event loss or interruption of the service.
- *Security*: Internal communication between microservices and Kafka cluster is encrypted using _*mTLS* (Mutual Transport Layer Security)_. Each Kafka broker holds a *keystore* containing its own *RSA* certificate and private key, and a truststore containing the *CA* certificate used to authenticate incoming connections. Each _Python_ microservice is provided with a *PEM-encoded* certificate and private key, both signed by an internal _*CA* (Certificate Authority)_. During the TLS handshake, both parties present and mutually verify their certificates against the shared CA. Any connection attempt from a client not holding a valid CA-signed certificate is rejected at the transport layer, making unauthorized access to Kafka topics computationally infeasible.
- *Load Balancing*: this requirement is handled natively by Apache Kafka architecture, comining topic partitioning with the strategic use of consumer groups. Services like Notifier and Storage use static Group IDs: in case of horizontal scaling, Kafka ripartizes autonomatically topic's partitions among the replicas of the microservice, distributing the load evenly. The only exception is the *Dashboard*, which uses a randomly generated Group ID (backed by a sufficiently large keyspace) to ensure each instance is treated as an independent consumer group, allowing all instances to consume the same data in parallel without load balancing, implementing a _broadcasting pattern_ suited for real-time visualization.

= Showcases
#figure(
  image("/img/kafka-UI.png", width: 80%),
  caption: [Load Balancing on 6 partitions of `weather.telemetry` topic, viewable thanks to #link("https://github.com/provectus/kafka-ui")[Kafka-UI].]
) <fig:kafka-UI>

#figure(
  image("/img/dashboard.png", width: 80%),
  caption: [Frontend Dashboard with Real-Time data.]
) <fig:dashboard>

#figure(
  image("/img/forwarder.png", width: 80%),
  caption: [Telegram Forwarder chat with some weather alerts.]
) <fig:forwarder>