# Project Plan

## Decisions and constraints

- Keep the existing frontend visual design and behavior unless integration requires a change.
- Use Next.js for the frontend and FastAPI for the backend.
- Build and serve the frontend statically from FastAPI at `/`.
- Package the application in one local Docker container.
- Use `uv` for Python dependencies and SQLite for local persistence.
- Use the hardcoded MVP credentials `user` / `password`; authentication lasts only for the browser session.
- Support one board per user in the MVP while keeping the data model extensible to multiple users.
- Use OpenRouter with `z-ai/glm-5.2:free` and the `OPENROUTER_API_KEY` from the project-root `.env` file. The connectivity check must make a real request.
- Preserve the specified color scheme and keep documentation in `docs/` concise.
- Do not add unrelated features or refactor existing frontend code without a requirement.
- Target roughly 80% test coverage when it is sensible, but prioritize valuable behavior and risk coverage over reaching a numeric threshold. Missing 80% is acceptable when additional tests would be redundant.

## Part 1: Detailed plan and frontend documentation

Checklist:

- [x] Expand this document into phase checklists, tests, and success criteria.
- [x] Inspect the existing frontend entry point, board model, components, styling, and test commands.
- [x] Create `frontend/AGENTS.md` describing the current frontend architecture and conventions.
- [ ] Get user approval for this plan before starting Part 2.

Tests and checks:

- Confirm the existing frontend test and lint commands are identified in the documentation.
- Confirm the documented component and state boundaries match the current source.

Success criteria:

- The plan is approved by the user.
- A future agent can execute each phase without guessing its deliverables or validation.

## Part 2: Scaffolding

Checklist:

- [x] Add the FastAPI backend structure and Python dependency configuration managed by `uv`.
- [x] Add a Dockerfile and supporting ignore/configuration files for the combined application.
- [x] Add Linux, macOS, and Windows start/stop scripts under `scripts/`.
- [x] Add a minimal health or hello-world API route.
- [x] Serve a minimal static HTML response while the frontend is not yet integrated.
- [x] Document local prerequisites, environment variables, and startup commands.

Tests and checks:

- [x] Run backend unit tests for the health/API route.
- [x] Build the Docker image successfully.
- [x] Start the container and verify the static hello-world response.
- [x] Make an HTTP API request from the running container and verify its response.
- [x] Run and validate the Linux start/stop scripts. macOS and Windows scripts are intentionally skipped by decision.

Current validation: backend tests, local Uvicorn HTTP checks, Docker image build, and container HTTP checks pass.

Success criteria:

- One documented command starts the local container and one stops it.
- The running container serves HTML at `/` and returns a successful API response.
- Secrets are supplied through environment configuration and are not baked into the image.

## Part 3: Add in the existing frontend

Checklist:

- [x] Configure Next.js for a static export compatible with FastAPI static-file serving.
- [x] Build the existing demo board without changing its intended appearance or interactions.
- [x] Mount the generated frontend assets at `/` and preserve client-side asset loading.
- [x] Add integration coverage for the built app being served by the backend.

Tests and checks:

- Run frontend unit tests, lint, and the production build.
- Run browser tests against the container, checking that five columns render and core board interactions remain available.
- Verify a production build has no runtime asset 404s.

Current validation: Docker static build, backend tests, frontend unit tests, lint, and container HTML/API smoke checks pass. Local Node.js `18.19.0` cannot run Next.js `16.1.6`; the supported Node 22 build was validated in Docker.

Success criteria:

- Visiting `/` in the container displays the existing Kanban demo.
- The board can rename columns, add/delete cards, and move cards as before.
- The frontend is served from the backend without a separate frontend server.

## Part 4: Fake user sign-in

Checklist:

- [x] Add a login view shown when no browser-session authentication exists.
- [x] Validate exactly `user` / `password` for the MVP.
- [x] Store the authenticated state only in browser session storage or an equivalent session-only mechanism.
- [x] Protect the board view and add a logout action that clears the session.
- [x] Keep the existing board design intact outside the authentication flow.

Tests and checks:

- [x] Test successful and unsuccessful login attempts.
- [x] Test that unauthenticated users cannot see the board.
- [x] Test logout and session restoration within the same browser session.
- [x] Test that a new browser context is unauthenticated.
- [x] Run valuable frontend unit, integration, lint, and live browser checks; do not add redundant tests solely to reach 80% coverage.

Current validation: authentication unit tests, frontend unit tests (`9` total), lint, Docker production build, and live browser login/logout checks pass. The repository Playwright command remains pending because the host Node.js version is `18.19.0`, while the project requires Node.js `>=20.9.0`.

Success criteria:

- `/` requires login before the board is visible.
- Correct credentials reveal the board; incorrect credentials do not.
- Logout hides the board, and authentication does not persist across browser contexts or browser restarts.

## Part 5: Database modeling and approval

Checklist:

- [x] Define the proposed user, board, column, card, and ordering relationships.
- [x] Define identifiers, required fields, ownership rules, and timestamps where useful.
- [x] Define how the normalized frontend board JSON maps to SQLite records and API payloads.
- [x] Define initialization and seed behavior for a new database.
- [x] Save the proposal as `docs/kanban-schema.json`.
- [x] Document the database approach and tradeoffs in `docs/DATABASE.md`.
- [ ] Get explicit user sign-off before implementing the schema.

Tests and checks:

- [x] Validate the proposal as JSON.
- [x] Check that every field needed by the current board model is represented.
- [x] Review persistence, ordering, ownership, and migration assumptions against the MVP requirements.

Success criteria:

- The JSON proposal is valid, complete for the MVP, and approved before coding begins.
- The design supports multiple users later while enforcing one board per user now.

## Part 6: Backend board API

Checklist:

- [x] Create the SQLite database automatically when it does not exist.
- [x] Implement initialization/seed logic for the approved schema.
- [x] Add authenticated API routes to read a user board.
- [x] Add routes to rename columns and create, edit, delete, and move cards.
- [x] Validate request and response payloads with typed FastAPI models.
- [x] Enforce user ownership and the one-board-per-user MVP rule.
- [x] Return clear errors for missing boards, cards, columns, and invalid moves.

Tests and checks:

- [x] Run backend unit tests for database creation, seeding, reads, and each mutation.
- [x] Test invalid payloads, missing resources, ordering, and ownership boundaries.
- [x] Test repeated initialization does not duplicate seed data.
- [x] Run the backend test suite against a temporary SQLite database.

Current validation: `7` backend tests pass, Docker build passes, and live container checks cover health, seeded board projection, and authenticated column mutation.

Success criteria:

- A fresh database is created automatically and produces a usable board.
- All supported board mutations persist and are returned consistently as board JSON.
- A user cannot read or modify another user's board.

## Part 7: Frontend plus backend persistence

Checklist:

- [ ] Replace demo-only board state with API loading after authentication.
- [ ] Send each supported board mutation to the backend.
- [ ] Handle loading, save failure, and retry states without losing the visible board unexpectedly.
- [ ] Refresh or reconcile board state after successful mutations.
- [ ] Keep drag-and-drop, editing, and existing visual conventions usable.
- [ ] Add test fixtures and documented local API configuration.

Tests and checks:

- Test initial board loading from the API.
- Test every UI mutation sends the expected request and displays persisted state.
- Test reload persistence and API error handling.
- Run frontend unit, integration, browser, backend, and container tests.

Success criteria:

- Board changes survive page reloads and container restarts when the SQLite volume is retained.
- The UI and API agree on column and card ordering.
- Network failures are visible and do not silently report unsaved changes as complete.

## Part 8: OpenRouter connectivity

Checklist:

- [ ] Load `OPENROUTER_API_KEY` from the project-root `.env` configuration.
- [ ] Add a backend service for OpenRouter using `z-ai/glm-5.2:free`.
- [ ] Add a minimal connectivity route or diagnostic operation that asks `2+2`.
- [ ] Keep the key server-side and exclude it from frontend bundles and logs.
- [ ] Document the required key and the real connectivity test.

Tests and checks:

- Run a real request using the configured `OPENROUTER_API_KEY` and verify a successful answer to `2+2`.
- Test configuration errors and upstream failure responses.
- Verify the key is not present in API responses, browser assets, or application logs.

Success criteria:

- The backend can make and parse a real OpenRouter response using the required model.
- Missing or failed upstream configuration produces a clear server-side error without exposing secrets.

## Part 9: Structured AI board operations

Checklist:

- [ ] Define the chat request containing the user's question, board JSON, and conversation history.
- [ ] Define the structured response containing the assistant reply and an optional validated board update.
- [ ] Send the complete current board JSON with every AI request.
- [ ] Require updates to use the approved board shape and preserve board invariants.
- [ ] Validate and persist an AI-proposed update only when it is valid and authorized.
- [ ] Return the assistant response and the resulting board state consistently.
- [ ] Define handling for malformed output, refusal, timeout, and upstream errors.

Tests and checks:

- Test request construction includes board JSON, question, and conversation history.
- Test parsing of response-only and response-plus-update outputs.
- Test invalid structured output cannot corrupt the database.
- Test AI-created, edited, deleted, and moved cards through the backend contract.
- Test conversation history ordering and bounded error handling.

Success criteria:

- Every AI call receives the complete current board context.
- The backend accepts only schema-valid, ownership-safe updates.
- A response without an update leaves the board unchanged.

## Part 10: AI chat sidebar

Checklist:

- [ ] Add a responsive sidebar chat widget consistent with the existing frontend design.
- [ ] Display conversation history, pending state, errors, and the send interaction.
- [ ] Send authenticated questions to the backend with the current conversation history.
- [ ] Apply returned board updates and refresh the board automatically.
- [ ] Keep direct board editing and drag-and-drop usable while chat is present.
- [ ] Add accessible labels, keyboard interaction, and responsive behavior.

Tests and checks:

- Test sending a question and rendering the assistant response.
- Test loading and error states, including retry behavior.
- Test an AI response that changes the board refreshes the visible columns/cards.
- Test a response without a board update leaves the board unchanged.
- Run the complete frontend, backend, browser, and container test suites.

Success criteria:

- An authenticated user can hold a multi-turn chat from the sidebar.
- AI-created, edited, deleted, or moved cards appear without a manual page reload.
- The final Dockerized application works locally with the documented environment setup.