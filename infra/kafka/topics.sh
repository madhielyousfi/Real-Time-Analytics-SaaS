#!/bin/bash

KAFKA_BROKER="localhost:9092"

create_topic() {
    local topic_name=$1
    local partitions=${2:-4}
    local replication=${3:-1}

    kafka-topics --create \
        --bootstrap-server $KAFKA_BROKER \
        --replication-factor $replication \
        --partitions $partitions \
        --topic $topic_name \
        --if-not-exists

    echo "Topic $topic_name created"
}

echo "Creating Kafka topics..."

create_topic "raw_events" 4 1
create_topic "processed_events" 4 1

echo "All topics created successfully"