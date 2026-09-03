import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData, type BoardData } from "@/lib/kanban";

let testBoard: BoardData;

beforeEach(() => {
  testBoard = structuredClone(initialData);
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, options?: RequestInit) => {
      const body = options?.body ? JSON.parse(options.body as string) : null;
      if (url.includes("/columns/") && body) {
        const columnId = url.split("/columns/")[1];
        testBoard.columns = testBoard.columns.map((column) =>
          column.id === columnId ? { ...column, title: body.title } : column
        );
      }
      if (url.endsWith("/cards") && body) {
        testBoard.cards[body.id] = {
          id: body.id,
          title: body.title,
          details: body.details,
        };
        testBoard.columns = testBoard.columns.map((column) =>
          column.id === body.column_id
            ? { ...column, cardIds: [...column.cardIds, body.id] }
            : column
        );
      }
      if (url.includes("/cards/") && options?.method === "DELETE") {
        const cardId = url.split("/cards/")[1];
        delete testBoard.cards[cardId];
        testBoard.columns = testBoard.columns.map((column) => ({
          ...column,
          cardIds: column.cardIds.filter((id) => id !== cardId),
        }));
      }
      return { ok: true, json: async () => structuredClone(testBoard) };
    })
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

const getFirstColumn = async () => (await screen.findAllByTestId(/column-/i))[0];

describe("KanbanBoard", () => {
  it("renders five columns", async () => {
    render(<KanbanBoard />);
    expect(await screen.findAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    const column = await getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    expect(input).toHaveValue("New Name");
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    const column = await getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(within(column).getByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });
});
