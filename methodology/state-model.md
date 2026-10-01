# Public state model

A public state is a bounded conclusion at a stated knowledge cutoff. It records what the accepted evidence supports, what it does not establish, and which evidence could change the state.

`NOT_ESTABLISHED` means the reviewed public record does not meet the stated threshold. It does not mean `DOES_NOT_EXIST`. `UNKNOWN` is preserved when the approved record cannot support a narrower conclusion.

State changes are append-only. A new state links to the prior state and triggering evidence; it does not erase the historical stop point.
