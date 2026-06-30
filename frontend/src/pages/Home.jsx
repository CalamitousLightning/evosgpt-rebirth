export default function Home({ setPage, user }) {
  return (
    <div style={{ fontFamily: "Inter,sans-serif", background: "#050816", minHeight: "100vh", color: "#e2e8f0" }}>

      <style>{`
        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
        }

        button {
          transition: all 0.25s ease;
        }

        button:hover {
          transform: translateY(-2px);
        }

        .glass-card {
          transition: all 0.25s ease;
        }

        .glass-card:hover {
          transform: translateY(-4px);
          border-color: rgba(56,189,248,0.35) !important;
        }

        @media (max-width:600px){

          .hero-btns {
            flex-direction:column !important;
          }

          .hero-btns button {
            max-width:100% !important;
          }

          .stats-row > div {
            flex:1 1 45% !important;
          }

          .who-grid {
            grid-template-columns:1fr !important;
          }

          .output-grid {
            grid-template-columns:1fr !important;
          }

          .memory-grid {
            grid-template-columns:1fr !important;
            padding:25px !important;
          }

          .pricing-grid {
            grid-template-columns:1fr !important;
          }

          .crossell-box {
            flex-direction:column !important;
          }

          .footer-inner {
            flex-direction:column !important;
          }

        }


        @media(min-width:900px){

          .who-grid {
            grid-template-columns:repeat(6,1fr) !important;
          }

          .pricing-grid {
            grid-template-columns:repeat(3,1fr) !important;
          }

        }

      `}</style>



      {/* NAV */}

      <nav
        className="nav-inner"
        style={{
          maxWidth:1100,
          margin:"auto",
          padding:"18px 24px",
          display:"flex",
          justifyContent:"space-between",
          alignItems:"center",
          borderBottom:"1px solid rgba(255,255,255,0.06)"
        }}
      >

        <div style={{display:"flex",alignItems:"center",gap:10}}>

          <div
            style={{
              width:36,
              height:36,
              borderRadius:12,
              background:"linear-gradient(135deg,#38bdf8,#a78bfa)",
              display:"flex",
              alignItems:"center",
              justifyContent:"center",
              color:"#000",
              fontWeight:900
            }}
          >
            ⚡
          </div>


          <span
            style={{
              fontSize:20,
              fontWeight:900,
              background:"linear-gradient(135deg,#38bdf8,#a78bfa)",
              WebkitBackgroundClip:"text",
              WebkitTextFillColor:"transparent"
            }}
          >
            EVOSGPT
          </span>

        </div>


        <div style={{display:"flex",gap:10}}>

          {
            user ?

            <>
              <Btn ghost onClick={()=>setPage("dashboard")}>
                Dashboard
              </Btn>

              <Btn onClick={()=>setPage("chat")}>
                💬 Chat
              </Btn>
            </>

            :

            <>
              <Btn ghost onClick={()=>setPage("login")}>
                Login
              </Btn>

              <Btn onClick={()=>setPage("register")}>
                Get Started
              </Btn>
            </>

          }

        </div>


      </nav>




      {/* HERO */}


      <section
        className="hero-section"
        style={{
          maxWidth:850,
          margin:"auto",
          textAlign:"center",
          padding:"90px 24px 70px"
        }}
      >


        <div
          style={{
            display:"inline-block",
            padding:"6px 18px",
            borderRadius:50,
            background:"rgba(56,189,248,0.1)",
            border:"1px solid rgba(56,189,248,0.25)",
            color:"#38bdf8",
            fontSize:12,
            fontWeight:800,
            marginBottom:25
          }}
        >
          🚀 Powered by EVOXERA TECHNOLOGY
        </div>



        <h1
          style={{
            fontSize:"clamp(34px,6vw,62px)",
            fontWeight:950,
            lineHeight:1.1,
            marginBottom:20
          }}
        >

          The AI That{" "}

          <span
            style={{
              background:"linear-gradient(135deg,#38bdf8,#a78bfa,#22c55e)",
              WebkitBackgroundClip:"text",
              WebkitTextFillColor:"transparent"
            }}
          >
            Evolves With You
          </span>


        </h1>




        <p
          style={{
            maxWidth:600,
            margin:"auto",
            color:"#94a3b8",
            fontSize:17,
            lineHeight:1.8
          }}
        >
          EVOSGPT is an evolving AI assistant built by EVOXERA TECHNOLOGY.
          It helps you code, create, write, plan and solve problems while adapting
          to your workflow.
        </p>



        <div
          className="hero-btns"
          style={{
            display:"flex",
            justifyContent:"center",
            gap:12,
            marginTop:35
          }}
        >


          <button
            onClick={()=>setPage(user?"chat":"register")}
            style={{
              padding:"15px 30px",
              borderRadius:15,
              border:"none",
              background:"linear-gradient(135deg,#38bdf8,#0ea5e9)",
              fontWeight:900,
              cursor:"pointer",
              color:"#000",
              boxShadow:"0 10px 30px rgba(56,189,248,.25)"
            }}
          >
            💬 Start Chatting
          </button>


          {
            !user &&

            <button
              onClick={()=>setPage("login")}
              style={{
                padding:"15px 30px",
                borderRadius:15,
                border:"1px solid rgba(255,255,255,.15)",
                background:"transparent",
                color:"#fff",
                fontWeight:800,
                cursor:"pointer"
              }}
            >
              Sign In
            </button>

          }


        </div>





        <div
          className="stats-row"
          style={{
            display:"flex",
            gap:12,
            marginTop:50,
            flexWrap:"wrap"
          }}
        >

          {
            [
              ["GPT Engine","Advanced AI"],
              ["Memory","Personalized"],
              ["Output","Clean Results"],
              ["24/7","Always Ready"]

            ].map(([a,b])=>(

              <div
                key={a}
                className="glass-card"
                style={{
                  flex:"1",
                  minWidth:130,
                  padding:18,
                  borderRadius:18,
                  background:"rgba(255,255,255,.04)",
                  border:"1px solid rgba(255,255,255,.07)"
                }}
              >

                <div
                  style={{
                    fontWeight:900,
                    color:"#38bdf8"
                  }}
                >
                  {a}
                </div>


                <div
                  style={{
                    fontSize:12,
                    color:"#64748b",
                    marginTop:5
                  }}
                >
                  {b}
                </div>


              </div>


            ))
          }


        </div>


      </section>

      {/* SMART OUTPUT */}
         {/* WHO IT'S FOR */}


      <section
        style={{
          maxWidth:1100,
          margin:"auto",
          padding:"0 24px 70px"
        }}
      >

        <div
          style={{
            textAlign:"center",
            marginBottom:40
          }}
        >

          <Tag>
            Who It's For
          </Tag>


          <h2
            style={{
              fontSize:"clamp(22px,3vw,32px)",
              fontWeight:900
            }}
          >
            Built for creators, builders and thinkers
          </h2>


        </div>



        <div
          className="who-grid"
          style={{
            display:"grid",
            gap:14
          }}
        >


        {[
          ["💻","Developers","Code, debugging, APIs and software architecture."],
          ["🎨","Designers","Creative ideas, layouts and design concepts."],
          ["✍️","Writers","Letters, documents, blogs and professional writing."],
          ["📊","Businesses","Planning, strategy and productivity support."],
          ["🎓","Students","Learning, summaries and explanations."],
          ["📱","Creators","Content ideas, captions and growth strategies"]

        ].map(([icon,title,desc])=>(


          <div
            key={title}
            className="glass-card"
            style={{
              background:"rgba(255,255,255,.035)",
              border:"1px solid rgba(255,255,255,.07)",
              borderRadius:20,
              padding:20
            }}
          >

            <div style={{fontSize:30}}>
              {icon}
            </div>


            <div
              style={{
                fontWeight:900,
                marginTop:12
              }}
            >
              {title}
            </div>


            <p
              style={{
                fontSize:12,
                color:"#64748b",
                lineHeight:1.7
              }}
            >
              {desc}
            </p>


          </div>


        ))}


        </div>


      </section>





      {/* SMART OUTPUT */}



      <section
        style={{
          maxWidth:1100,
          margin:"auto",
          padding:"0 24px 70px"
        }}
      >


        <div
          style={{
            textAlign:"center",
            marginBottom:40
          }}
        >

          <Tag>
            Smart Output
          </Tag>


          <h2
            style={{
              fontSize:"clamp(22px,3vw,32px)",
              fontWeight:900
            }}
          >
            Results made to be used instantly
          </h2>


        </div>




        <div
          className="output-grid"
          style={{
            display:"grid",
            gridTemplateColumns:"repeat(auto-fit,minmax(280px,1fr))",
            gap:18
          }}
        >


          <div
            className="glass-card"
            style={{
              background:"rgba(255,255,255,.035)",
              border:"1px solid rgba(255,255,255,.07)",
              borderRadius:20,
              overflow:"hidden"
            }}
          >

            <div
              style={{
                padding:15,
                fontWeight:900
              }}
            >
              💻 Code Assistant
            </div>


            <div
              style={{
                background:"#020617",
                padding:20
              }}
            >

<pre
style={{
color:"#38bdf8",
fontSize:13,
overflow:"auto"
}}
>
{`function greet(name){

 return "Hello " + name;

}

console.log(
 greet("EVOSGPT")
);`}
</pre>


            </div>


            <div
              style={{
                padding:12,
                color:"#38bdf8",
                fontSize:12
              }}
            >
              Ready to copy and use
            </div>


          </div>





          <div
            className="glass-card"
            style={{
              background:"rgba(255,255,255,.035)",
              border:"1px solid rgba(255,255,255,.07)",
              borderRadius:20,
              padding:22
            }}
          >


            <h3>
              ✍️ Professional Writing
            </h3>


            <p
              style={{
                color:"#94a3b8",
                lineHeight:1.8,
                fontSize:14
              }}
            >

              Create emails, proposals, CVs,
              reports and business documents
              with professional formatting.

            </p>


          </div>



        </div>



      </section>





      {/* MEMORY */}



      <section
        style={{
          maxWidth:1100,
          margin:"auto",
          padding:"0 24px 70px"
        }}
      >


        <div
          className="memory-grid"
          style={{
            display:"grid",
            gridTemplateColumns:"repeat(auto-fit,minmax(260px,1fr))",
            gap:30,
            padding:40,
            borderRadius:25,
            background:
            "linear-gradient(135deg,rgba(56,189,248,.08),rgba(167,139,250,.08))",
            border:"1px solid rgba(255,255,255,.08)"
          }}
        >


          <div>


            <Tag>
              Evolving Memory
            </Tag>


            <h2
              style={{
                fontWeight:900,
                fontSize:28
              }}
            >
              EVOSGPT learns your workflow
            </h2>


            <p
              style={{
                color:"#94a3b8",
                lineHeight:1.8
              }}
            >

              Your conversations become more personalized.
              EVOSGPT adapts to your style, projects and goals.

            </p>


          </div>





          <div
            style={{
              display:"flex",
              flexDirection:"column",
              gap:12
            }}
          >


          {
            [

["🧠","Context Memory","Keeps track of conversations"],

["📚","Long Memory","Stores useful preferences"],

["🎯","Personal AI","Adjusts responses to you"]

            ].map(([i,t,d])=>(


              <div
                key={t}
                style={{
                  display:"flex",
                  gap:12,
                  padding:15,
                  borderRadius:15,
                  background:"rgba(255,255,255,.04)"
                }}
              >

                <span>
                  {i}
                </span>


                <div>

                  <b>
                    {t}
                  </b>


                  <div
                    style={{
                      fontSize:12,
                      color:"#64748b"
                    }}
                  >
                    {d}
                  </div>


                </div>


              </div>


            ))
          }


          </div>


        </div>


      </section>





      {/* PRICING */



      <section
        style={{
          maxWidth:1100,
          margin:"auto",
          padding:"0 24px 70px"
        }}
      >


        <div style={{textAlign:"center"}}>


          <Tag>
            Pricing
          </Tag>


          <h2
          style={{
          fontWeight:900
          }}
          >
            Choose your AI level
          </h2>


        </div>



        <div
          className="pricing-grid"
          style={{
            display:"grid",
            gap:18,
            marginTop:40
          }}
        >



        {[
{
name:"Basic",
price:"Free",
icon:"🧊",
color:"#64748b",
features:[
"Daily AI chats",
"Basic memory",
"General assistant"
]
},

{
name:"Pro",
price:"GH₵20/mo",
icon:"⚡",
color:"#38bdf8",
features:[
"Unlimited chats",
"Advanced AI",
"Developer tools",
"Long memory"
]
},


{
name:"Core",
price:"GH₵70/mo",
icon:"🔥",
color:"#a78bfa",
features:[
"Maximum AI power",
"Priority access",
"Full personalization"
]
}

].map(plan=>(


<div
key={plan.name}
className="glass-card"
style={{
padding:25,
borderRadius:22,
background:"rgba(255,255,255,.04)",
border:`1px solid ${plan.color}55`
}}
>


<div style={{fontSize:35}}>
{plan.icon}
</div>


<h3 style={{color:plan.color}}>
{plan.name}
</h3>


<h2>
{plan.price}
</h2>



{
plan.features.map(x=>(

<div
key={x}
style={{
fontSize:13,
marginTop:10,
color:"#94a3b8"
}}
>
✓ {x}
</div>

))
}



<button
onClick={()=>setPage(user?"upgrade":"register")}
style={{
marginTop:20,
width:"100%",
padding:13,
borderRadius:12,
border:`1px solid ${plan.color}`,
background:"transparent",
color:plan.color,
fontWeight:900
}}
>
Choose Plan
</button>



</div>


))


        </div>



      </section>
      {/* EVOSDATA */}
           {/* EVOS DATA */}


      <section
        style={{
          maxWidth:1100,
          margin:"auto",
          padding:"0 24px 70px"
        }}
      >


        <div
          className="crossell-box"
          style={{
            display:"flex",
            justifyContent:"space-between",
            alignItems:"center",
            gap:25,
            padding:30,
            borderRadius:25,
            background:
            "linear-gradient(135deg,rgba(34,197,94,.1),rgba(16,185,129,.06))",
            border:"1px solid rgba(34,197,94,.25)"
          }}
        >



          <div>


            <div
              style={{
                color:"#22c55e",
                fontWeight:800,
                fontSize:13
              }}
            >
              🔗 EVOXERA ECOSYSTEM
            </div>



            <h3
              style={{
                fontWeight:900,
                fontSize:22
              }}
            >
              Need data to keep using EVOSGPT?
            </h3>



            <p
              style={{
                color:"#64748b"
              }}
            >
              Buy fast and affordable Ghana data bundles through EVOS Data Services.
            </p>



          </div>




          <button
            onClick={()=>
              window.open("https://evosdata.xyz","_blank")
            }
            style={{
              padding:"14px 25px",
              borderRadius:14,
              border:"none",
              background:
              "linear-gradient(135deg,#22c55e,#16a34a)",
              color:"#fff",
              fontWeight:900,
              cursor:"pointer"
            }}
          >

            📶 Buy Data

          </button>




        </div>


      </section>





      {/* FOOTER */}



      <footer
        style={{
          borderTop:
          "1px solid rgba(255,255,255,.07)",
          padding:"35px 24px",
          maxWidth:1100,
          margin:"auto"
        }}
      >



        <div
          className="footer-inner"
          style={{
            display:"flex",
            justifyContent:"space-between",
            flexWrap:"wrap",
            gap:25
          }}
        >




          <div>


            <div
              style={{
                fontSize:20,
                fontWeight:950,
                color:"#38bdf8"
              }}
            >
              ⚡ EVOSGPT
            </div>



            <div
              style={{
                color:"#475569",
                fontSize:13,
                marginTop:5
              }}
            >
              An AI platform by EVOXERA TECHNOLOGY
            </div>


          </div>






          <div
            className="footer-links"
            style={{
              display:"flex",
              gap:20,
              flexWrap:"wrap"
            }}
          >



          {
            [

["Login","login"],

["Register","register"],

["Chat","chat"]

            ].map(([name,page])=>(


              <span
              key={page}
              onClick={()=>setPage(page)}
              style={{
                cursor:"pointer",
                color:"#64748b",
                fontSize:13,
                fontWeight:700
              }}
              >

                {name}

              </span>


            ))
          }



            <span
            onClick={()=>
            window.open("https://evosdata.xyz","_blank")
            }
            style={{
              cursor:"pointer",
              color:"#22c55e",
              fontWeight:800,
              fontSize:13
            }}
            >

              EVOS Data

            </span>



          </div>




        </div>






        <div
          style={{
            textAlign:"center",
            marginTop:30,
            color:"#334155",
            fontSize:12
          }}
        >

          © 2026 EVOXERA TECHNOLOGY.
          All Rights Reserved.

          <br/>

          EVOSGPT • EVOS Data Services • Future Intelligence Systems

        </div>



      </footer>


    </div>

  );
}







const Btn = ({children,onClick,ghost}) => (

<button

onClick={onClick}

style={{

padding:"9px 18px",

borderRadius:12,

border:
ghost
?
"1px solid rgba(255,255,255,.15)"
:
"none",


background:

ghost
?
"transparent"
:
"linear-gradient(135deg,#38bdf8,#0ea5e9)",


color:

ghost
?
"#e2e8f0"
:
"#000",


fontWeight:900,

cursor:"pointer"

}}

>

{children}

</button>

);








const Tag = ({children}) => (

<span

style={{

display:"inline-block",

padding:"5px 15px",

borderRadius:50,

background:
"rgba(167,139,250,.12)",


border:
"1px solid rgba(167,139,250,.3)",


color:"#a78bfa",

fontSize:12,

fontWeight:800

}}

>

{children}

</span>

);
