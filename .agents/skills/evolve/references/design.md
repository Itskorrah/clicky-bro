# Product and interface improvement

## Investigate the real experience

Capture existing states and walk the important user flows with synthetic content.
Inspect navigation, information hierarchy, density, feedback, errors, recovery,
keyboard/focus behaviour and relevant viewport/platform sizes. Distinguish observed
friction from aesthetic preference. A static screenshot cannot establish interaction.

Use product goals and audience to choose changes. Research current primary platform
guidelines or relevant examples for unresolved decisions. Preserve useful capabilities
and familiar operations while improving clarity. Define observable success.

## Implement a coherent system

Use the existing tokens/components where viable. Align typography, spacing, colour
roles, contrast, icon language, surfaces and states. Document additions at the right
level; do not scatter one-off values through unrelated components.

Account for loading, empty, disabled, error, permission and long-content states.
Validate keyboard navigation, visible focus, labels, target size, screen-reader
semantics and contrast where applicable. Test localisation/zoom/resize when they
affect the changed flow. Check light/dark themes without making unsupported claims.

Animations should communicate state without delaying input. Respect reduced-motion
settings and platform conventions. Use original or properly licensed assets with
required attribution. A polished appearance cannot replace working behaviour.

## Customisation is a feature

For adjustable themes/toolbars/layouts/shortcuts, specify:

- Defaults and discoverability of core actions.
- Valid choices, conflicts, constraints and preview behaviour.
- Saved state across restart and workspaces if promised.
- Reset and recovery from invalid or old configurations.
- Migration/compatibility of existing preferences.
- Keyboard/accessibility behaviour under customised layouts.

Implement these through actual application state. A settings UI with no persisted
effect is incomplete. Avoid adding configuration for every internal option; expose
choices that support real user needs.

## Verify visually and interactively

Inspect before/after captures with comparable content, viewport and state. Check
the implemented flow and relevant failure states. Require actual interaction evidence
for focus, shortcuts, persistence and accessibility. Record what was inspected and
what could not be exercised. Do not claim a premium redesign from generated mockups.
