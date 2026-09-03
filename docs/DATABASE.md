# Database Approach

## Proposal

The schema proposal is in [kanban-schema.json](kanban-schema.json). It models users, boards, columns, cards, and ordered card membership as normalized SQLite tables.

The API will project those rows into the frontend's existing `BoardData` shape:

- `columns` are ordered by `columns.position`.
- Each column's `cardIds` are ordered by `board_cards.position`.
- `cards` is keyed by `cards.id`.

This keeps the UI contract simple while making ownership, ordering, and persistence explicit in the database.

## MVP behavior

A database file is created on startup if it does not exist. Initialization creates tables and seeds the hardcoded `user` account and its one board only when they are absent. The MVP enforces one board per user with a unique constraint on `boards.user_id`; that constraint can be removed or revised when multiple boards are introduced.

All board mutations should run in transactions. The backend must verify that the user owns the board, column, and cards involved before changing them. Card moves update membership and normalize positions in the affected columns. Deletes rely on foreign-key cascades after the ownership check.

For the MVP API, board routes use the username in the URL and require a matching `X-Username` request header. This is a small server-side ownership check for the current hardcoded user; Part 7 will have the authenticated frontend send it. It is not intended to replace real authentication in a later production system.

Timestamps use ISO-8601 UTC text, which is portable in SQLite and easy to return through the API. Stable text IDs match the current frontend data and avoid coupling the API to database-generated integer IDs.

## Tradeoffs and boundaries

- Normalized rows avoid duplicating card content across columns and make edits consistent.
- A separate `board_cards` table makes ordering and future board views explicit, at the cost of extra joins and position maintenance.
- SQLite is appropriate for this local single-container MVP, but concurrent multi-instance deployment would require a migration to a server database and a migration strategy.
- The MVP password is intentionally not part of this schema because authentication is currently a hardcoded application rule. A future real-auth implementation should add a password hash field or separate credentials table and never store plaintext passwords.
- Schema migrations are out of scope for the first database creation. Future changes should use versioned migrations rather than silently changing existing tables.

## Approval gate

This is a proposal only. Part 6 must not implement the database until the user approves `docs/kanban-schema.json` and this approach.
