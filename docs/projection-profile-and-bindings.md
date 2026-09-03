# Projection Profile and Bindings

The Projection Profile binds OrbitFabric source entities to OpenC3 COSMOS target names without modifying the OrbitFabric Mission Model.

Initial supported binding domains are:

```text
commands
telemetry
```

Command bindings resolve an OrbitFabric command to a COSMOS command name. Telemetry bindings resolve an OrbitFabric telemetry item to a COSMOS packet/item pair and may define target value encoding.

The first schema supports `identity` and `boolean_01` telemetry value encodings. Command arguments remain fail-closed until an explicit target encoder is defined.

A binding may use `do_not_project` with an explicit reason. Missing required mappings block projection instead of silently dropping intent.
