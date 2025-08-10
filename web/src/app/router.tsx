import { createBrowserRouter } from "react-router-dom";
import { Layout } from "./layout";
import Protected from "../auth/Protected";
import SummaryPage from "../features/summary/SummaryPage";
import TransactionsPage from "../features/transactions/TransactionsPage";
import LoginPage from "../features/auth/LoginPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    element: <Protected />, // everything below requires auth
    children: [
      {
        path: "/",
        element: <Layout />,
        children: [
          { index: true, element: <SummaryPage /> },
          { path: "transactions", element: <TransactionsPage /> },
        ],
      },
    ],
  },
]);
