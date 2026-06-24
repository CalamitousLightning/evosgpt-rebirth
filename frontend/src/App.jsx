import { useState, useEffect } from "react";
import Home      from "./pages/Home";
import Login     from "./pages/Login";
import Register  from "./pages/Register";
import Chat      from "./pages/Chat";
import Dashboard from "./pages/Dashboard";
import Upgrade   from "./pages/Upgrade";

export default function App() {
  const [page, setPage] = useState("home");
  const [user, setUser] = useState(null);

  useEffect(() => {
    try {
      const s = localStorage.getItem("evosgpt_user");
      if (s) setUser(JSON.parse(s));
    } catch { localStorage.removeItem("evosgpt_user"); }
  }, []);

  const handleSetUser = (u) => {
    setUser(u);
    if (u) localStorage.setItem("evosgpt_user", JSON.stringify(u));
    else   localStorage.removeItem("evosgpt_user");
  };

  const handleLogout = () => { handleSetUser(null); setPage("home"); };

  const go = (p) => {
    if (["chat","dashboard","upgrade"].includes(p) && !user) { setPage("login"); return; }
    setPage(p);
  };

  const pages = {
    home:      <Home      setPage={go} user={user} />,
    login:     <Login     setPage={go} setUser={handleSetUser} />,
    register:  <Register  setPage={go} setUser={handleSetUser} />,
    chat:      <Chat      setPage={go} user={user} setUser={handleSetUser} />,
    dashboard: <Dashboard setPage={go} user={user} onLogout={handleLogout} />,
    upgrade:   <Upgrade   setPage={go} user={user} setUser={handleSetUser} />,
  };

  return <div style={{ minHeight: "100vh", background: "#070d1a" }}>{pages[page] ?? pages.home}</div>;
}
