# Migrating from a PoC

Do not rewrite an engineering PoC repository into the final adapter product.

Recommended extraction sequence:

```text
freeze PoC evidence baseline
    -> analyze Target Applicable Surface
    -> declare adapter scope
    -> publish Integration Coverage Matrix
    -> create clean repository from this Template
    -> port product code only
    -> pass Template lifecycle gates
    -> run target-native compatibility controls
    -> define remaining roadmap
    -> decide version from actual product maturity
```

The original PoC remains historical engineering evidence and a reference or regression workspace.
