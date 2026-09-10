# Timeline R1.1 Pre Audit

Base commit: `0f7762b31dcf85754468a81b884665e717050e79`

R1.1 separates structural condition Level from structural change Delta. Single snapshots default to `delta_state = NOT_ESTABLISHED` unless an explicit change event or valid comparable prior observation exists.
