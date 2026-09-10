# Timeline R1.1 Pre Audit

Base commit: `9abfb37392f921e499915358ff0700173240cef6`

R1.1 separates structural condition Level from structural change Delta. Single snapshots default to `delta_state = NOT_ESTABLISHED` unless an explicit change event or valid comparable prior observation exists.
