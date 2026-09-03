# Runtime Dependencies

Runtime dependencies belong to the adapter package when its implemented operations require them.

Do not assume that OrbitFabric Core is present inside the adapter managed environment merely because Adapter Manager launched the installation.

The dummy adapter deliberately does not import the OrbitFabric Python package at runtime. It consumes only public machine-readable files and therefore declares only its actual Python runtime dependencies.

A real adapter that intentionally uses an OrbitFabric runtime API must declare a compatible OrbitFabric dependency and document why that API dependency is required.
