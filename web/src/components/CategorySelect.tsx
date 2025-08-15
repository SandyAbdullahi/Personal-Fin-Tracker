// src/components/CategorySelect.tsx
import { useEffect, useMemo, useState } from "react";
import { useCategories, useCreateCategory } from "../features/categories/hooks";

type Props = {
  label?: string;
  value: number | null | undefined;
  onChange: (id: number | null) => void;
  allowCreate?: boolean;
  disabled?: boolean;
  placeholder?: string;
};

export default function CategorySelect({
  label = "Category",
  value,
  onChange,
  allowCreate = true,
  disabled,
  placeholder = "Select a category…",
}: Props) {
  const { data: categories, isLoading } = useCategories();
  const createMut = useCreateCategory();
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");

  const sorted = useMemo(
    () => (categories ?? []).slice().sort((a, b) => a.name.localeCompare(b.name)),
    [categories]
  );

  useEffect(() => {
    if (!creating) setNewName("");
  }, [creating]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      const created = await createMut.mutateAsync(newName.trim());
      onChange(created.id);
      setCreating(false);
    } catch (err) {
      alert((err as Error).message);
    }
  };

  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium">{label}</label>

      {creating ? (
        <form className="flex gap-2" onSubmit={handleCreate}>
          <input
            className="border rounded px-2 py-1 flex-1"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="New category name"
            disabled={createMut.isPending}
          />
          <button className="btn" type="submit" disabled={createMut.isPending}>
            {createMut.isPending ? "Saving…" : "Save"}
          </button>
          <button className="btn-secondary" type="button" onClick={() => setCreating(false)}>
            Cancel
          </button>
        </form>
      ) : (
        <div className="flex gap-2">
          <select
            className="border rounded px-2 py-1 flex-1"
            value={value ?? ""}
            onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
            disabled={disabled || isLoading}
          >
            <option value="">{placeholder}</option>
            {sorted.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>

          {allowCreate && (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setCreating(true)}
              disabled={isLoading}
              title="Create a new category"
            >
              + New
            </button>
          )}
        </div>
      )}
    </div>
  );
}
