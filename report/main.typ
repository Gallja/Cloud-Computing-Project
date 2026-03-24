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
)

= Introduction
This project is about building and implementing a _*Cloud-Native*_ architecture for real-time weather telemetry using _Apache Kafka_. The system is designed to collect, process, and store real-time meteorological data from six different cities in Italy: Milan, Turin, Verona, Florence, Rome and Naples (the data is retrieved via _REST API_ available on #link("https://open-meteo.com/")[`open-meteo.com`]). In addition, a continuos stream of measurements (temperature, rainfall, wind speed...) is simulated by an external script and sent to the Kafka cluster. From there, the data is consumed in parallel by multiple microservices for specific purposes: real-time data visualization via a web dashboard, data storage in NoSQL database and alert generation for extreme weather conditions, forwarded to a smartphone via Telegram bot. The main focus is to garantee the system's scalability, reliability, criptographic security and fault-tolerance.


= Architectural overview
The entire infrastructure is based on an architectural pattern with deacupled microservices: the communication is not direct, but rather mediated by a message broker, in this case Apache Kafka. This design allows for greater flexibility and scalability, as each microservice can be developed, deployed and scaled independently, without affecting the others. The main components of the system are:



= Description of the system
== Components
The entire system is composed of the following components:
- *Weather-Poller*: Python script that periodically retrieves weather data from #link("https://open-meteo.com/")[`open-meteo.com`] for the six cities and sends it to the API-Producer.
- *API-Producer*: REST application that receives weather data in JSON format and sends it to the Kafka cluster. Thanks to _HTTP POST_ requests, the producer publishes the data to the main Kafka topic (`weather.telemetry`) instantly.
- *Dashboard*: Web application that consumes the data from the Kafka topic and visualizes it in real-time. The dashboard is built with *_Flask_*.
- *Storage*: Microservice responsible for consuming the data from the Kafka topic and storing it in a _*NoSQL database*_ (_MongoDB_).
- *Notifier*: Microservice that consumes the data from the Kafka topic and generates alerts for extreme weather conditions (e.g., high or low temperature, heavy rainfall, strong winds). If Notifier detects an extreme weather condition, it publishes an alert message to a specific Kafka topic (`weather.alerts`). Notifier is a Consumer, but also a Producer.
- *Telegram Forwarder*: Isolated microservice that only consumes alert messages from the `weather.alerts` topic and uses Telegram's API to forward notifications to the users' smartphones.

== Streaming processing and distributed coordination
The backbone of the architecture is rapresented by a distributed messaging cluster (it is the "_Single Source of Truth_") for alla the microservices:
- *Apache Kafka*: it manages data flow and divides it in *Topics* (`weather.telemetry` and `weather.alerts`). Kafka brokers push data to the Consumers, but they also act as immutable registers (with high performance) for microservices that pull data autonomously and at their own rithm.
- *ZooKeeper*: It is the distributed coordinator for the Kafka cluster. It manages and keep metadata in cluster, manage brokers' registration and leader election, and it also monitors the health of the cluster. Thanks to ZooKeeper, the system can automatically recover from failures and maintain high availability.

== Infrastructure as code and containerization
The entire architecture is based to be "Cloud-Ready", isolating processes in containers and making deployment universal and reproducible. The main tools used for this purpose are:
- *Docker*: each microservice is packeged in an isolated conainer, starting with a specific image (`python:3.11-slim`). This approach guaratees code portability and consistency across different environments.
- *Docker Compose*: used to orchestrate the deployment of all microservices (_Infrastructure as Code_). The `docker-compose.yml` file instances containers simultaneously, defines their dependencies and manages the network configuration. This allows for easy scaling and management of the entire system.

= Non-functional requirements
Industrial standards respected:
- *Fault Tolerance*: Kafka Cluster is configured with a replication factor of 3. Data is replicated accross phisically separated nodes, so, in case of a node failure, _Zookeeper_ automatically promotes a backup replice (_ISR_) to a new leader whithin few milliseconds, without any event loss or interruption of the service.
- *Security*: Internal communication between microservices and Kafka cluster is encrypted using _*mTLS* (Mutual Transport Layer Security)_ protocol. Each Kafka node and each Python microservice is equipped with a cryptographic certificate and a private key signed by an internal _*CA* (Certificate Authority)_. Without valid certificates mounted in the containers, access to the topics is mathematically imposssible.
- *Load Balancing*: this requirement is handled natively by Apache Kafka architecture, comining topic partitioning with the strategic use of consumer groups. Services like Notifier and Storage use static Group IDs: in case of horizontal scaling, Kafka ripartizes autonomatically topic's partitions among the replicas of the microservice, balancing the load perfectly. The only exception is the Dashboard, which uses a dynamic Group ID to allow multiple instances and to consume the same data in parallel, without load balancing, for real-time visualization (broadcasting pattern).

= Showcases
