"use client";

import { startTransition, useEffect, useMemo, useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCenter,
  pointerWithin,
  type DragEndEvent,
  type DragOverEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { boardApi } from "@/lib/api";
import { createId, moveCard, type BoardData } from "@/lib/kanban";

export const KanbanBoard = ({ onLogout }: { onLogout?: () => void }) => {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [overId, setOverId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    boardApi
      .get()
      .then((nextBoard) => startTransition(() => setBoard(nextBoard)))
      .catch(() => setError("Could not load the board. Please try again."));
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  const cardsById = useMemo(() => board?.cards ?? {}, [board?.cards]);

  if (!board) {
    return <main className="flex min-h-screen items-center justify-center text-sm text-[var(--gray-text)]">Loading board...</main>;
  }

  const handleDragStart = (event: DragStartEvent) => {
    if (isSaving) return;
    setActiveCardId(event.active.id as string);
    setOverId(null);
  };

  const handleDragOver = (event: DragOverEvent) => {
    setOverId(event.over?.id as string | null);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);
    setOverId(null);

    if (!over || active.id === over.id) {
      return;
    }

    if (isSaving) return;

    const nextColumns = moveCard(board.columns, active.id as string, over.id as string);
    const targetColumn = nextColumns.find((column) => column.cardIds.includes(active.id as string));
    if (!targetColumn) return;
    const previousBoard = board;
    setBoard({ ...board, columns: nextColumns });
    setIsSaving(true);
    try {
      const nextBoard = await boardApi.moveCard(
        active.id as string,
        targetColumn.id,
        targetColumn.cardIds.indexOf(active.id as string)
      );
      setBoard(nextBoard);
      setError(null);
    } catch {
      setBoard(previousBoard);
      setError("Could not move the card. Your board was not changed.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleRenameColumn = async (columnId: string, title: string) => {
    setIsSaving(true);
    try {
      const nextBoard = await boardApi.renameColumn(columnId, title);
      setBoard(nextBoard);
      setError(null);
    } catch {
      setError("Could not save the column name.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddCard = async (columnId: string, title: string, details: string) => {
    const id = createId("card");
    setIsSaving(true);
    try {
      const nextBoard = await boardApi.createCard(columnId, title, details || "No details yet.", id);
      setBoard(nextBoard);
      setError(null);
    } catch {
      setError("Could not add the card. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteCard = async (_columnId: string, cardId: string) => {
    setIsSaving(true);
    try {
      const nextBoard = await boardApi.deleteCard(cardId);
      setBoard(nextBoard);
      setError(null);
    } catch {
      setError("Could not delete the card. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const activeCard = activeCardId ? cardsById[activeCardId] : null;
  const collisionDetection = (args: Parameters<typeof pointerWithin>[0]) => {
    const collisionArgs = {
      ...args,
      droppableContainers: args.droppableContainers.filter(
        (container) => container.id !== args.active.id
      ),
    };
    const pointerCollisions = pointerWithin(collisionArgs);
    return pointerCollisions.length > 0
      ? pointerCollisions
      : closestCenter(collisionArgs);
  };

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
            </div>
            <div className="flex items-start gap-4 rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
              {onLogout && (
                <button
                  type="button"
                  onClick={onLogout}
                  className="order-2 rounded-lg border border-[var(--stroke)] px-3 py-2 text-xs font-semibold text-[var(--navy-dark)] hover:border-[var(--primary-blue)]"
                >
                  Log out
                </button>
              )}
              <div>
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                Focus
              </p>
              <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                One board. Five columns. Zero clutter.
              </p>
              </div>
            </div>
          </div>
          {(error || isSaving) && (
            <p role="status" className="text-sm text-[var(--secondary-purple)]">
              {isSaving ? "Saving changes..." : error}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        <DndContext
          sensors={sensors}
          collisionDetection={collisionDetection}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        >
          <section className="grid gap-6 lg:grid-cols-5">
            {board.columns.map((column) => (
              <KanbanColumn
                key={column.id}
                column={column}
                cards={column.cardIds.map((cardId) => board.cards[cardId])}
                isHighlighted={
                  overId === column.id || column.cardIds.includes(overId ?? "")
                }
                onRename={handleRenameColumn}
                onAddCard={handleAddCard}
                onDeleteCard={handleDeleteCard}
              />
            ))}
          </section>
          <DragOverlay>
            {activeCard ? (
              <div className="w-[260px]">
                <KanbanCardPreview card={activeCard} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </main>
    </div>
  );
};
