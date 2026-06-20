# Product

## Register

product

## Users

Operators who maintain Nekro Agent fleets across several machines. They use the panel during live operations to route users to the right NA instance, inspect which server owns an instance, and avoid touching the wrong host.

## Product Purpose

Nekro User Panel is a headquarters gateway for constrained access to many Nekro Agent instances. It should make the hierarchy clear: one headquarters panel, multiple server nodes, and many NA instances under those nodes. Success means a login reaches the correct instance, administrators can maintain routing without editing JSON by hand, and offline nodes do not break unrelated users.

## Brand Personality

Calm, precise, operational.

## Anti-references

Avoid marketing-page styling, decorative dashboards, oversized hero layouts, and UI that hides operational facts behind pretty summaries. Avoid making nodes and instances look like the same action, because they represent different levels of the system.

## Design Principles

- Show the routing hierarchy directly: headquarters, node, instance.
- Keep actions scoped: node actions should not be mixed with instance actions.
- Prefer explicit routing over fallbacks that may hide a broken server.
- Preserve live-service safety: old instance configs must keep working while new nodes are added.
- Make failure states readable enough to act on.

## Accessibility & Inclusion

Target WCAG AA contrast for text and controls. Keep forms keyboard-accessible, use standard controls, avoid motion that is not tied to state, and respect reduced-motion preferences.
