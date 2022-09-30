# gRPC showcase

## Project structure

```mermaid
flowchart LR
    web-client <--->|REST API| main-server
    main-server <--->|gRPC| vault
    main-server <--->|gRPC| recommendation
```

* web-client - sends HTTP requests to the main-server
* main-server - hosts the REST API server and executes remote call procedures with gRPC clients
* vault - hosts a gRPC server for a Vault managing service
* recommendation - hosts a gRPC server for a recommendation engine

## How to run

```bash
docker compose up
```
