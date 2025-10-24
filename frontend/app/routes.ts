import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [index("routes/home.tsx"),
    route("/Hero", "components/hero.tsx"),
    route("/Description", "components/description.tsx"),
    route("/Dashboard", "pages/dashboard.tsx"),
    route("/Notebook", "pages/notebook.tsx"),
    route("/Upload", "components/upload.tsx"),
    route("/Header", "components/header.tsx"),
    route("/Chat", "components/chat.tsx"),
] satisfies RouteConfig;
