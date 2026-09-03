import type { BoardData } from "@/lib/kanban";

const USERNAME = "user";

const request = async (url: string, options: RequestInit = {}): Promise<BoardData> => {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Username": USERNAME,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json() as Promise<BoardData>;
};

export const boardApi = {
  get: () => request(`/api/boards/${USERNAME}`),
  renameColumn: (columnId: string, title: string) =>
    request(`/api/boards/${USERNAME}/columns/${columnId}`, {
      method: "PATCH",
      body: JSON.stringify({ title }),
    }),
  createCard: (columnId: string, title: string, details: string, id: string) =>
    request(`/api/boards/${USERNAME}/cards`, {
      method: "POST",
      body: JSON.stringify({ id, title, details, column_id: columnId }),
    }),
  updateCard: (cardId: string, title: string, details: string) =>
    request(`/api/boards/${USERNAME}/cards/${cardId}`, {
      method: "PATCH",
      body: JSON.stringify({ title, details }),
    }),
  deleteCard: (cardId: string) =>
    request(`/api/boards/${USERNAME}/cards/${cardId}`, { method: "DELETE" }),
  moveCard: (cardId: string, columnId: string, position: number) =>
    request(`/api/boards/${USERNAME}/cards/${cardId}/move`, {
      method: "POST",
      body: JSON.stringify({ column_id: columnId, position }),
    }),
};
