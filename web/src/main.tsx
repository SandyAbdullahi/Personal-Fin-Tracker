import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import router from "./app/router";
import { AuthProvider } from "./context/AuthContext"; // ← use THIS one

import "./index.css";   // ← global (Tailwind goes here if you're using it)
import "./App.css";     // ← optional: only if you actually use styles from App.css


ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </React.StrictMode>
);
