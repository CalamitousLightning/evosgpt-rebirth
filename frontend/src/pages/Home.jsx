      {/* EVOSDATA */}
      <section style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px 60px" }}>
        <div className="crossell-box" style={{ background: "linear-gradient(135deg,rgba(34,197,94,0.08),rgba(16,185,129,0.05))", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 22, padding: "30px 28px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 20 }}>
          <div>
            <div style={{ fontSize: 12, color: "#22c55e", fontWeight: 700, marginBottom: 6 }}>
              🔗 EVOS Ecosystem
            </div>

            <h3 style={{ fontSize: "clamp(16px,2.5vw,20px)", fontWeight: 900, color: "#f1f5f9", marginBottom: 6 }}>
              Need data to keep chatting?
            </h3>

            <p style={{ color: "#64748b", fontSize: 13, margin: 0 }}>
              Buy affordable Ghana data bundles instantly on EvosData.
            </p>
          </div>

          <button 
            onClick={() => window.open("https://evosdata.xyz","_blank")}
            style={{ padding: "12px 24px", borderRadius: 12, border: "none", background: "linear-gradient(135deg,#22c55e,#16a34a)", color:"#fff", fontWeight:900, fontSize:14, cursor:"pointer", whiteSpace:"nowrap" }}
          >
            📶 Buy Data on EvosData
          </button>

        </div>
      </section>


      {/* FOOTER */}
      <footer style={{ borderTop:"1px solid rgba(255,255,255,0.06)", padding:"28px 24px 20px", maxWidth:1100, margin:"0 auto" }}>

        <div className="footer-inner" style={{ display:"flex", justifyContent:"space-between", flexWrap:"wrap", gap:16, marginBottom:16 }}>

          <div>
            <div style={{ fontSize:16, fontWeight:900, color:"#38bdf8" }}>
              ⚡ EVOSGPT
            </div>

            <div style={{ fontSize:12, color:"#334155" }}>
              Powered by Evoxera Technology
            </div>
          </div>


          <div className="footer-links" style={{ display:"flex", gap:20, flexWrap:"wrap" }}>

            {[["Login","login"],["Register","register"],["Chat","chat"]].map(([l,p]) => (

              <span 
                key={p}
                onClick={() => setPage(p)}
                style={{ fontSize:13, color:"#475569", cursor:"pointer", fontWeight:600 }}
              >
                {l}
              </span>

            ))}


            <span 
              onClick={() => window.open("https://evosdata.xyz","_blank")}
              style={{ fontSize:13, color:"#475569", cursor:"pointer", fontWeight:600 }}
            >
              EvosData
            </span>


          </div>

        </div>


        <div style={{ fontSize:12, color:"#334155", textAlign:"center" }}>
          © 2026 Evoxera Technology · All Rights Reserved
        </div>


      </footer>

    </div>
  );
}


const Btn = ({ children, onClick, ghost }) => (

  <button
    onClick={onClick}
    style={{
      padding:"8px 16px",
      borderRadius:10,
      border:ghost ? "1px solid rgba(255,255,255,0.12)" : "none",
      background:ghost ? "transparent" : "linear-gradient(135deg,#38bdf8,#0ea5e9)",
      color:ghost ? "#e2e8f0" : "#000",
      fontWeight:800,
      fontSize:13,
      cursor:"pointer"
    }}
  >

    {children}

  </button>

);


const Tag = ({ children }) => (

  <span
    style={{
      display:"inline-block",
      padding:"4px 14px",
      borderRadius:50,
      background:"rgba(167,139,250,0.1)",
      border:"1px solid rgba(167,139,250,0.25)",
      color:"#a78bfa",
      fontSize:12,
      fontWeight:700
    }}
  >

    {children}

  </span>

);
