# Compatibility, persistence and data integrity

Identify contracts before changing them: file formats, storage schemas, APIs,
configuration, identifiers, CLI behaviour, integrations and import/export fidelity.
The user's existing data is part of the product.

## A useful fixture corpus

Use synthetic or redistributable fixtures representing ordinary, large, malformed,
legacy and partially supported inputs. Record provenance and expected behaviour.
Keep private customer files local. Public standards/documentation guide semantics;
third-party behaviour is a comparison source only when legitimately observable.

For each important format/workflow, test open → inspect → edit → save → reopen.
Assert semantic preservation, including unchanged information and unsupported fields
when the product promises to retain them. Byte equality alone may be inappropriate;
normalisation alone can conceal lost information. Rendering comparisons need an
inspected reference, stable fonts/settings and stated tolerances.

## Failure and hostile inputs

Exercise truncated input, oversized values, unexpected nesting, duplicate records,
encoding boundaries, cancellation and partial writes. Bound allocation/recursion
where untrusted input can exhaust resources. Check error messages and recovery.
Use fuzzing/property tests when justified by parser risk and invariants.

Protect writes: validate before replacing good data, use appropriate atomicity and
durability, handle interrupted saves, and verify recovery. Saving an unsupported
feature must not silently discard it while reporting full success.

## Migrations and contract changes

Define old/new schema versions, compatibility policy, migration preconditions,
rollback/recovery and verification. Test with realistic old data and failed steps.
Never run a destructive migration against production just because implementation
was authorised. Prefer an isolated fixture/local environment until the relevant
production action is explicitly authorised.

For rebranding, changing visible names need not break package IDs, persisted paths,
command IDs or public integrations. Rename internal identifiers when the benefit
justifies the compatibility work. Preserve notices and original attribution.

Report supported, partially supported, preserved-but-not-editable and unsupported
cases separately. A format extension or menu command is not proof of full parity.
