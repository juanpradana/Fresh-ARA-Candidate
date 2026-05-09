import React from "react";
import ReactDOM from "react-dom/client";
import { ScreenerPage } from "./features/screener/ScreenerPage";
import "./styles/tailwind.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ScreenerPage />
  </React.StrictMode>
);
