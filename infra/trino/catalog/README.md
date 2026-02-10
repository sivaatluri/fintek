# Trino Configuration

This directory contains Trino catalog configurations.

## Catalog Structure

Each catalog is defined in a separate properties file:

- `postgresql.properties` - PostgreSQL connector
- `hive.properties` - Hive connector (future)

## Adding a New Catalog

1. Create a new `.properties` file
2. Configure the connector
3. Restart Trino

Example PostgreSQL catalog:

```properties
connector.name=postgresql
connection-url=jdbc:postgresql://postgres:5432/fintek
connection-user=fintek
connection-password=fintek_dev
```
