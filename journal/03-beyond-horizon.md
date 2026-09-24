# Spiral 03 — Repos beyond the horizon

**Date:** 2026-09-24T08:41:11.431998

**Source:** Gemini (9695ms)

Here are 5 new repositories designed to fill the most important gaps in the Quilt fleet, focusing on the substrate walker pattern:

---

**quilt-orchestrator**: Coordinates the execution and monitoring of complex, multi-stage substrate walker workflows.
-   **wrapper**: Composes a DAG-based engine for scheduling, dependency management, and state tracking of substrate walker tasks.
-   **tests**: Verifies correct task sequencing, error handling, retry mechanisms, and state transitions within a workflow.
-   **demo**: Shows a multi-walker data processing pipeline, from ingestion to transformation and output, driven by defined workflow stages.

---

**quilt-bus**: Provides a pub-sub message bus for real-time data exchange and event coordination among substrate walkers.
-   **wrapper**: Composes message queues and topic subscribers to facilitate asynchronous, loosely coupled communication between walkers.
-   **tests**: Verifies message delivery, topic subscription, payload integrity, and concurrent message handling across multiple walkers.
-   **demo**: Demonstrates a producer walker publishing events consumed by multiple subscriber walkers performing reactive processing.

---

**quilt-query-engine**: Enables efficient querying, aggregation, and analysis of substrate cell data and walker states.
-   **wrapper**: Composes an indexing and query layer over cell witness logs and walker state snapshots, supporting structured and temporal queries.
-   **tests**: Verifies query accuracy, performance on large datasets, correct aggregation functions, and filtering capabilities across various cell attributes.
-   **demo**: Illustrates querying specific cell patterns, aggregating walker activity metrics, and analyzing temporal trends in substrate evolution.

---

**quilt-schema-registry**: Manages the definition, versioning, and evolution of schemas for `quilt-cell` 14-tuples and overall substrate structures.
-   **wrapper**: Composes a metadata store and validation engine for cell schemas, ensuring data consistency and enabling schema evolution across walkers.
-   **tests**: Verifies schema validation, version compatibility checks, schema migration logic, and proper registration/retrieval of schema definitions.
-   **demo**: Shows how to register a new cell schema, validate cell data against it, and perform a schema update with backward compatibility checks.

---

**quilt-linker**: Establishes and manages relationships and traversal capabilities across federated, distinct Quilt substrates.
-   **wrapper**: Composes a graph-based linking mechanism to define inter-substrate connections and provides APIs for cross-substrate navigation and data resolution.
-   **tests**: Verifies link integrity, traversal paths between different substrates, conflict resolution in federated queries, and access control for linked data.
-   **demo**: Demonstrates linking entities from one substrate to another, traversing these links to retrieve associated data, and resolving queries across federated instances.
