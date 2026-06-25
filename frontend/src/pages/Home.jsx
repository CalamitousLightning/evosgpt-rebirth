export default function Home({ setPage, user }) {
  return (
    <div style={{ fontFamily: "Inter,sans-serif", background: "#070d1a", minHeight: "100vh", color: "#e2e8f0" }}>

      {/* NAV */}
      <nav style={{ maxWidth: 1100, margin: "0 auto", padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 24 }}>⚡</span>
          <span style={{ fontSize: 18, fontWeight: 900, background: "linear-gradient(135deg,#38bdf8,#a78bfa)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>EVOSGPT</span>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {user ? (
            <>
              <Btn ghost onClick={() => setPage("dashboard")}>Dashboard</Btn>
              <Btn onClick={() => setPage("chat")}>💬 Chat</Btn>
            </>
          ) : (
            <>
              <Btn ghost onClick={() => setPage("login")}>Login</Btn>
              <Btn onClick={() => setPage("register")}>Get Started</Btn>
            </>
          )}
        </div>
      </nav>

      {/* HERO */}
      <section style={{ maxWidth: 800, margin: "0 auto", textAlign: "center", padding: "60px 20px 50px" }}>
        <div style={{ display: "inline-block", padding: "5px 16px", borderRadius: 50, background: "rgba(56,189,248,0.1)", border: "1px solid rgba(56,189,248,0.25)", color: "#38bdf8", fontSize: 12, fontWeight: 700, marginBottom: 24 }}>
          🇬🇭 Part of the EVOS Business Hub Ecosystem
        </div>
        <h1 style={{ fontSize: "clamp(28px,6vw,58px)", fontWeight: 900, lineHeight: 1.1, marginBottom: 18, padding: "0 4px" }}>
          The AI That{" "}
          <span style={{ background: "linear-gradient(135deg,#38bdf8,#a78bfa,#22c55e)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Evolves With You</span>
        </h1>
        <p style={{ fontSize: "clamp(14px,2vw,17px)", color: "#94a3b8", lineHeight: 1.75, marginBottom: 32, maxWidth: 560, margin: "0 auto 32px" }}>
          EVOSGPT remembers your style, your goals, and your history — getting smarter every conversation. Built for developers, designers, writers and entrepreneurs.
        </p>
        <div style={{ display: "flex", justifyContent: "center", gap: 10, flexWrap: "wrap", padding: "0 8px" }}>
          <button onClick={() => setPage(user ? "chat" : "register")} style={{ padding: "14px 28px", borderRadius: 14, border: "none", background: "linear-gradient(135deg,#38bdf8,#0ea5e9)", color: "#000", fontWeight: 900, fontSize: 15, cursor: "pointer", boxShadow: "0 4px 28px rgba(56,189,248,0.3)", flex: "1 1 auto", maxWidth: 260 }}>
            💬 Start Chatting — Free
          </button>
          {!user && (
            <button onClick={() => setPage("login")} style={{ padding: "14px 28px", borderRadius: 14, border: "1px solid rgba(255,255,255,0.15)", background: "transparent", color: "#e2e8f0", fontWeight: 800, fontSize: 15, cursor: "pointer", flex: "1 1 auto", maxWidth: 200 }}>
              Sign In
            </button>
          )}
        </div>

        {/* STATS ROW */}
        <div style={{ display: "flex", justifyContent: "center", gap: 10, flexWrap: "wrap", marginTop: 40, padding: "0 4px" }}>
          {[["GPT-4o","Pro Engine"],["Memory","Evolves Per User"],["Clean Output","Code & Letters"],["24/7","Always On"]].map(([v, l]) => (
            <div key={v} style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 12, padding: "12px 18px", textAlign: "center", flex: "1 1 80px" }}>
              <div style={{ fontWeight: 900, fontSize: 14, color: "#38bdf8" }}>{v}</div>
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 3 }}>{l}</div>
            </div>
          ))}
        </div>
      </section>

      {/* WHO IT'S FOR */}
      <section style={{ maxWidth: 1100, margin: "0 auto", padding: "10px 20px 60px" }}>
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <Tag>Who It's For</Tag>
          <h2 style={{ fontSize: "clamp(20px,3vw,30px)", fontWeight: 900, color: "#f1f5f9", margin: "12px 0 0" }}>Built for every professional</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(160px,1fr))", gap: 12 }}>
          {[
            ["💻","Developers","Clean code, debugging, architecture — production-ready."],
            ["🎨","Designers","Flyer copy, design briefs, color ideas, creative concepts."],
            ["✍️","Writers","Polished letters, emails, CVs, blog posts — copy-paste ready."],
            ["📊","Entrepreneurs","Business plans, pitch decks, financial summaries."],
            ["🎓","Students","Essays, summaries, explanations, study guides."],
            ["📱","Creators","Captions, content calendars, hashtag strategies."],
          ].map(([icon, title, desc]) => (
            <div key={title} style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 18, padding: "20px 16px" }}>
              <div style={{ fontSize: 28, marginBottom: 10 }}>{icon}</div>
              <div style={{ fontWeight: 800, fontSize: 14, color: "#f1f5f9", marginBottom: 6 }}>{title}</div>
              <div style={{ fontSize: 12, color: "#64748b", lineHeight: 1.6 }}>{desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* SMART OUTPUT */}
      <section style={{ maxWidth: 1100, margin: "0 auto", padding: "0 20px 60px" }}>
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <Tag>Smart Output</Tag>
          <h2 style={{ fontSize: "clamp(20px,3vw,30px)", fontWeight: 900, color: "#f1f5f9", margin: "12px 0 0" }}>Formatted, clean, copy-paste ready</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 16 }}>
          <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 18, overflow: "hidden" }}>
            <div style={{ padding: "12px 16px", borderBottom: "1px solid rgba(255,255,255,0.06)", fontWeight: 800, fontSize: 13, color: "#f1f5f9" }}>💻 Code Output</div>
            <div style={{ background: "#020817" }}>
              <div style={{ background: "rgba(56,189,248,0.1)", color: "#38bdf8", fontSize: 11, fontWeight: 700, padding: "5px 14px" }}>python</div>
              <pre style={{ padding: "14px", fontSize: 12, color: "#e2e8f0", fontFamily: "monospace", lineHeight: 1.7, overflow: "auto", margin: 0 }}>{`def calculate_profit(revenue, cost):
    profit = revenue - cost
    margin = (profit / revenue) * 100
    return round(margin, 2)

print(calculate_profit(5000, 3200))
# Output: 36.0`}</pre>
            </div>
            <div style={{ padding: "8px 14px", fontSize: 12, color: "#38bdf8" }}>📋 Copy the above and paste directly.</div>
          </div>

          <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 18, padding: "18px 20px" }}>
            <div style={{ fontWeight: 800, fontSize: 13, color: "#f1f5f9", marginBottom: 14 }}>✍️ Letter Output</div>
            <p style={{ color: "#64748b", fontSize: 13, marginBottom: 8 }}>12th June, 2026</p>
            <p style={{ fontWeight: 700, color: "#f1f5f9", marginBottom: 8 }}>Dear Hiring Manager,</p>
            <p style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.7, marginBottom: 8 }}>I write to formally apply for the Software Engineer position. With three years of experience in full-stack development...</p>
            <p style={{ color: "#64748b", fontSize: 13 }}>Yours faithfully,<br /><strong style={{ color: "#f1f5f9" }}>Kwame Asante</strong></p>
            <div style={{ marginTop: 12, fontSize: 12, color: "#38bdf8" }}>📋 Copy the above and paste directly.</div>
          </div>
        </div>
      </section>

      {/* MEMORY SECTION */}
      <section style={{ maxWidth: 1100, margin: "0 auto", padding: "0 20px 60px" }}>
        <div style={{ background: "linear-gradient(135deg,rgba(56,189,248,0.07),rgba(167,139,250,0.07))", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 22, padding: "36px 28px", display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 32, alignItems: "center" }}>
          <div>
            <Tag>Evolving Memory</Tag>
            <h2 style={{ fontSize: "clamp(20px,3vw,28px)", fontWeight: 900, color: "#f1f5f9", margin: "12px 0 12px" }}>EVOSGPT gets smarter every session</h2>
            <p style={{ color: "#94a3b8", lineHeight: 1.75, fontSize: 14 }}>Unlike other AI tools, EVOSGPT builds a memory of who you are — your goals, your writing style, your projects. Each conversation makes it more tailored to you.</p>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[
              ["🧠","Short-term Memory","Remembers the full context of your current conversation"],
              ["📚","Long-term Memory","AI-generated summary of all your past sessions"],
              ["🎯","Persona Calibration","Adapts its tone and depth to match your tier and style"],
            ].map(([icon, title, desc]) => (
              <div key={title} style={{ display: "flex", gap: 12, alignItems: "flex-start", background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 12, padding: "12px 14px" }}>
                <span style={{ fontSize: 22, flexShrink: 0 }}>{icon}</span>
                <div>
                  <div style={{ fontWeight: 800, fontSize: 13, color: "#f1f5f9", marginBottom: 3 }}>{title}</div>
                  <div style={{ fontSize: 12, color: "#64748b" }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section style={{ maxWidth: 1100, margin: "0 auto", padding: "0 20px 60px" }}>
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <Tag>Pricing</Tag>
          <h2 style={{ fontSize: "clamp(20px,3vw,30px)", fontWeight: 900, color: "#f1f5f9", margin: "12px 0 0" }}>Simple, honest pricing</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 16, maxWidth: 820, margin: "0 auto" }}>
          {[
            { name:"Basic", icon:"🧊", price:"Free", color:"#64748b", rgb:"100,116,139", model:"GPT-4o-mini",
              perks:["10 chats per day","20 message memory","General AI assistant","Access to EVOS ecosystem"],
              cta:"Start Free", primary:false },
            { name:"Pro", icon:"⚡", price:"GH₵20/mo", color:"#38bdf8", rgb:"56,189,248", model:"GPT-4o",
              perks:["Unlimited chats","100 message memory","Code & dev expert","Design & flyer briefs","Letter & document writing","Evolving long-term memory"],
              cta:"Upgrade to Pro", primary:true },
            { name:"Core", icon:"🔥", price:"GH₵50/mo", color:"#a78bfa", rgb:"167,139,250", model:"GPT-4o (Max Power)",
              perks:["Unlimited chats","300 message memory","All Pro features","Deepest AI responses","Priority everything","Full persona calibration"],
              cta:"Go Core", primary:false },
          ].map(t => (
            <div key={t.name} style={{ background: `rgba(${t.rgb},0.07)`, border: `1px solid ${t.color}33`, borderRadius: 22, padding: "24px 20px", position: "relative" }}>
              {t.primary && (
                <div style={{ position: "absolute", top: -12, left: "50%", transform: "translateX(-50%)", background: "#38bdf8", color: "#000", fontWeight: 900, fontSize: 11, padding: "4px 14px", borderRadius: 50, whiteSpace: "nowrap" }}>
                  ⭐ MOST POPULAR
                </div>
              )}
              <div style={{ fontSize: 32, marginBottom: 8 }}>{t.icon}</div>
              <div style={{ fontSize: 20, fontWeight: 900, color: t.color, marginBottom: 3 }}>{t.name}</div>
              <div style={{ fontSize: 11, color: "#475569", marginBottom: 12 }}>{t.model}</div>
              <div style={{ fontSize: 24, fontWeight: 900, color: t.color, marginBottom: 18 }}>{t.price}</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 22 }}>
                {t.perks.map(p => (
                  <div key={p} style={{ fontSize: 13, color: "#94a3b8", display: "flex", gap: 8 }}>
                    <span style={{ color: t.color, fontWeight: 700 }}>✓</span> {p}
                  </div>
                ))}
              </div>
              <button
                onClick={() => setPage(user ? (t.name === "Basic" ? "chat" : "upgrade") : "register")}
                style={{ width: "100%", padding: "12px", borderRadius: 12, border: `1px solid ${t.color}`, background: t.primary ? t.color : "transparent", color: t.primary ? "#000" : t.color, fontWeight: 900, fontSize: 14, cursor: "pointer" }}>
                {t.cta}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* EVOSDATA CROSSELL */}
      <section style={{ maxWidth: 1100, margin: "0 auto", padding: "0 20px 60px" }}>
        <div style={{ background: "linear-gradient(135deg,rgba(34,197,94,0.08),rgba(16,185,129,0.05))", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 22, padding: "30px 24px", display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 20 }}>
          <div>
            <div style={{ fontSize: 12, color: "#22c55e", fontWeight: 700, marginBottom: 6 }}>🔗 EVOS Ecosystem</div>
            <h3 style={{ fontSize: "clamp(16px,2.5vw,20px)", fontWeight: 900, color: "#f1f5f9", marginBottom: 6 }}>Need data to keep chatting?</h3>
            <p style={{ color: "#64748b", fontSize: 13 }}>Buy affordable Ghana data bundles instantly on EvosData.</p>
          </div>
          <button onClick={() => window.open("https://evosdata.xyz", "_blank")} style={{ padding: "12px 24px", borderRadius: 12, border: "none", background: "linear-gradient(135deg,#22c55e,#16a34a)", color: "#fff", fontWeight: 900, fontSize: 14, cursor: "pointer", whiteSpace: "nowrap" }}>
            📶 Buy Data on EvosData
          </button>
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{ borderTop: "1px solid rgba(255,255,255,0.06)", padding: "28px 20px 20px", maxWidth: 1100, margin: "0 auto" }}>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 16, marginBottom: 16 }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 900, color: "#38bdf8", marginBottom: 4 }}>⚡ EVOSGPT</div>
            <div style={{ fontSize: 12, color: "#334155" }}>Part of the EVOS Business Hub</div>
          </div>
          <div style={{ display: "flex", gap: 20, flexWrap: "wrap", alignItems: "center" }}>
            {[["Login","login"],["Register","register"],["Chat","chat"]].map(([l,p]) => (
              <span key={p} onClick={() => setPage(p)} style={{ fontSize: 13, color: "#475569", cursor: "pointer", fontWeight: 600 }}>{l}</span>
            ))}
            <span onClick={() => window.open("https://evosdata.xyz","_blank")} style={{ fontSize: 13, color: "#475569", cursor: "pointer", fontWeight: 600 }}>EvosData</span>
          </div>
        </div>
        <div style={{ fontSize: 12, color: "#1e293b", textAlign: "center" }}>© 2026 EVOS Technologies · All rights reserved</div>
      </footer>
    </div>
  );
}

const Btn = ({ children, onClick, ghost }) => (
  <button onClick={onClick} style={{ padding: "8px 16px", borderRadius: 10, border: ghost ? "1px solid rgba(255,255,255,0.12)" : "none", background: ghost ? "transparent" : "linear-gradient(135deg,#38bdf8,#0ea5e9)", color: ghost ? "#e2e8f0" : "#000", fontWeight: 800, fontSize: 13, cursor: "pointer" }}>
    {children}
  </button>
);

const Tag = ({ children }) => (
  <span style={{ display: "inline-block", padding: "4px 14px", borderRadius: 50, background: "rgba(167,139,250,0.1)", border: "1px solid rgba(167,139,250,0.25)", color: "#a78bfa", fontSize: 12, fontWeight: 700 }}>{children}</span>
);
