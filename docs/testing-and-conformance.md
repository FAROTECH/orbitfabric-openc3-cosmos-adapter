# Testing and Conformance

Validation is separated by layer:

```text
unit and negative tests
    -> adapter implementation behavior

Core conformance
    -> Integration Package and Integration Result validity

installed lifecycle
    -> wheel install / verify / execute / remove through Adapter Manager

target compatibility
    -> generated COSMOS artifacts against the validated downstream baseline

release proof
    -> exact release identity and Project Lock lifecycle
```

A green Core conformance check does not prove that OpenC3 COSMOS accepts a generated artifact. Target compatibility remains an independent control.
