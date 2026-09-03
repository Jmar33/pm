# Frontend Guidance

## Purpose

`frontend/` contains the existing Next.js Kanban board demo. It is currently a frontend-only application with in-memory state and no backend or authentication integration.

## Structure

- `src/app/page.tsx` is the home page and renders `KanbanBoard`.
- `src/app/globals.css` defines Tailwind imports, the project color variables, surfaces, typography hooks, and global layout rules.
- `src/components/KanbanBoard.tsx` is the client-side state owner. It renders the board, handles column renaming, card creation/deletion, drag state, and card movement.
- `src/components/KanbanColumn.tsx` renders a droppable column, its sortable cards, the card count, title input, and new-card form.
- `src/components/KanbanCard.tsx` renders an individual sortable card.
- `src/components/KanbanCardPreview.tsx` renders the drag overlay card.
- `src/components/NewCardForm.tsx` renders the add-card form.
- `src/lib/kanban.ts` contains the `BoardData`, `Column`, and `Card` types, demo data, card ID creation, and pure movement logic.
- `src/**/*.test.ts` and `src/**/*.test.tsx` contain Vitest and Testing Library tests.
- `tests/` contains Playwright browser tests.

## Existing conventions

- Use TypeScript and React function components.
- Keep browser-interactive components marked with `"use client"` where required.
- Use `@dnd-kit` for drag-and-drop behavior and preserve its sortable/droppable model.
- Keep board data normalized as columns containing ordered card IDs plus a cards record keyed by ID.
- Prefer existing Tailwind utility classes and CSS variables over introducing a separate styling system.
- Preserve the established color variables: yellow accent, blue primary, purple secondary, dark navy text, and gray supporting text.
- Keep public component APIs typed and use the existing `@/` import alias.
- Add or update focused tests with behavior changes.

## Commands

Run from `frontend/`:

- `npm run dev` starts the development server.
- `npm run build` creates the production build.
- `npm run lint` runs ESLint.
- `npm run test:unit` runs Vitest tests.
- `npm run test:e2e` runs Playwright tests.
- `npm run test:all` runs unit tests followed by browser tests.

## Integration direction

The project plan will progressively add static export, session-only authentication, backend API persistence, and an AI chat sidebar. Keep the current board interactions and visual language intact while moving persistence and authorization to their owning layers. Never expose the OpenRouter API key in browser code.
