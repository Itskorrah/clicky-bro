# clicky-bro source and tooling provenance

- `app/`: adopted from [Prasanth OpenClicky](https://github.com/prasanthsasikumar/openclicky)
  commit `1ff98e4e0f3c9af94ee3a80f81b2a20cb087aee9`. Its root MIT license
  remains at `app/LICENSE`; the macOS MIT attribution to Farza and other existing
  notices remain in their original locations. Internal class/namespace names
  are retained where renaming them would add no user-facing value.
- `.agents/skills/evolve`, `evolve-build`, `evolve-verify`: copied from the
  evaluated Itskorrah/evolve snapshot
  `89e0b5d39746cfc0503436d1335497a6a2e84d0f`, MIT. The associated license
  is retained in `.agents/skills/EVOLVE-LICENSE`.
- Context Mode and REA remain development tools in the user's existing local
  setup. They are not copied into the shipped application runtime.

Application code adoption does not grant rights to every optional model,
downloadable engine, asset or external service. Keep component notices and
verify actual packaging contents before distribution. No customer distribution or commercial release
has been performed in this work. The user authorized source delivery to their
private Itskorrah/clicky-bro repository.

Project-specific modifications are recorded in FOUNDATION_DECISION.md and
BUILD_STATUS.md, with raw local verification evidence under ignored `.local/`.
