// src/features/categories/CategoriesPage.tsx
import React, { useMemo, useState } from "react";
import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import {
  fetchCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  type CategoryDTO,
} from "./api";
import { useAuth } from "../../lib/auth/AuthContext";

export default function CategoriesPage() {
  const { hydrated, isAuthenticated } = useAuth();
  const qc = useQueryClient();

  // UI state
  const [search, setSearch] = useState("");
  const [newName, setNewName] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState("");

  // Load categories (wait until tokens are ready)
  const { data, isLoading, error } = useQuery({
    queryKey: ["categories"],
    queryFn: fetchCategories,
    enabled: hydrated && isAuthenticated,
    staleTime: 5 * 60 * 1000,
  });

  // Normalize to array to avoid `.map` crashes
  const categories: CategoryDTO[] = useMemo(
    () => (Array.isArray(data) ? data : []),
    [data]
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return categories;
    return categories.filter((c) => c.name.toLowerCase().includes(q));
  }, [categories, search]);

  // Mutations
  const createMut = useMutation({
    mutationFn: (name: string) => createCategory({ name }),
    onSuccess: () => {
      setNewName("");
      qc.invalidateQueries({ queryKey: ["categories"] });
    },
  });

  const updateMut = useMutation({
    mutationFn: (payload: { id: number; name: string }) =>
      updateCategory(payload.id, { name: payload.name }),
    onSuccess: () => {
      setEditingId(null);
      setEditingName("");
      qc.invalidateQueries({ queryKey: ["categories"] });
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteCategory(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
    },
  });

  // Handlers
  function startEdit(cat: CategoryDTO) {
    setEditingId(cat.id);
    setEditingName(cat.name);
  }
  function cancelEdit() {
    setEditingId(null);
    setEditingName("");
  }
  function saveEdit() {
    const name = editingName.trim();
    if (!editingId || !name) return;
    updateMut.mutate({ id: editingId, name });
  }
  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const name = newName.trim();
    if (!name) return;
    createMut.mutate(name);
  }
  function handleDelete(id: number) {
    if (confirm("Delete this category?")) {
      deleteMut.mutate(id);
    }
  }

  // Render
  if (!hydrated) return null; // or a small spinner

  if (isLoading) {
    return <div className="p-4">Loading categories…</div>;
  }

  if (error) {
    return (
      <div className="p-4 text-red-600">
        Failed to load categories.
      </div>
    );
  }

  return (
    <div className="p-4 space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Categories</h1>

        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border rounded px-3 py-2"
          />
        </div>
      </header>

      {/* Create new category */}
      <form onSubmit={handleCreate} className="flex gap-2 items-center">
        <input
          type="text"
          placeholder="New category name…"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <button
          type="submit"
          disabled={createMut.isPending}
          className="bg-blue-600 text-white px-3 py-2 rounded disabled:opacity-60"
        >
          {createMut.isPending ? "Adding…" : "Add"}
        </button>
        {createMut.isError && (
          <span className="text-red-600 text-sm">
            {(createMut.error as Error)?.message ?? "Create failed"}
          </span>
        )}
      </form>

      {/* Categories table */}
      <div className="overflow-x-auto">
        <table className="min-w-[480px] w-full border">
          <thead className="bg-black-50">
            <tr>
              <th className="text-left p-2 border-b">ID</th>
              <th className="text-left p-2 border-b">Name</th>
              <th className="text-left p-2 border-b w-48">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={3} className="p-4 text-gray-500">
                  No categories yet.
                </td>
              </tr>
            ) : (
              filtered.map((cat) => (
                <tr key={cat.id} className="border-b">
                  <td className="p-2 align-middle text-gray-600">{cat.id}</td>
                  <td className="p-2">
                    {editingId === cat.id ? (
                      <input
                        className="border rounded px-2 py-1 w-full"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        autoFocus
                      />
                    ) : (
                      <span>{cat.name}</span>
                    )}
                  </td>
                  <td className="p-2">
                    {editingId === cat.id ? (
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={saveEdit}
                          disabled={updateMut.isPending || !editingName.trim()}
                          className="bg-green-600 text-white px-2 py-1 rounded disabled:opacity-60"
                        >
                          {updateMut.isPending ? "Saving…" : "Save"}
                        </button>
                        <button
                          type="button"
                          onClick={cancelEdit}
                          className="px-2 py-1 rounded border"
                        >
                          Cancel
                        </button>
                        {updateMut.isError && (
                          <span className="text-red-600 text-sm">
                            {(updateMut.error as Error)?.message ??
                              "Update failed"}
                          </span>
                        )}
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => startEdit(cat)}
                          className="px-2 py-1 rounded border"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(cat.id)}
                          disabled={deleteMut.isPending}
                          className="px-2 py-1 rounded border text-red-600 disabled:opacity-60"
                        >
                          {deleteMut.isPending ? "Deleting…" : "Delete"}
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
