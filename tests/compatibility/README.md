# Target Compatibility Tests

This directory is reserved for downstream-native compatibility controls in a concrete adapter.

The included Dummy target is synthetic and has no independent downstream implementation, compiler, parser or validator. The Template therefore does not pretend to provide target-native acceptance evidence for it.

When creating a real adapter, replace this note with the strongest meaningful target control, for example:

```text
compile generated project
run target schema validator
import generated database
load generated configuration in simulator
run native parser
execute target runtime smoke test
```

Keep this layer separate from OrbitFabric Core conformance.

A Core-conformant Integration Result proves that the adapter reports its work correctly. A target compatibility test proves that the downstream accepts the projected artifact. A mature adapter normally needs both when the target exposes a validation path.
