export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="border-b border-slate-100">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#1e3a5f] rounded-lg flex items-center justify-center">
              <span className="text-white text-sm font-bold">E</span>
            </div>
            <span className="text-lg font-bold text-[#1e3a5f]">EduScope</span>
          </div>
          <div className="flex items-center gap-4">
            <a href="/login" className="text-sm text-slate-600 hover:text-slate-900 transition">Sign In</a>
            <a href="/login" className="px-4 py-2 text-sm font-medium bg-[#1e3a5f] text-white rounded-lg hover:bg-[#2d5a8e] transition">
              Get Started
            </a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-block px-3 py-1 bg-blue-50 text-[#0ea5e9] text-xs font-medium rounded-full mb-6">
            Higher Education Intelligence Platform
          </div>
          <h1 className="text-5xl font-bold text-slate-900 leading-tight">
            Data-Driven Decisions for<br />
            <span className="text-[#0ea5e9]">Education in Azerbaijan</span>
          </h1>
          <p className="mt-6 text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Help your university or course provider analyze student performance,
            detect dropout risk early, and align programs with labour market demand
            — all through automated, near-real-time analytics.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <a href="/login" className="px-8 py-3 text-base font-medium bg-[#1e3a5f] text-white rounded-lg hover:bg-[#2d5a8e] transition shadow-lg shadow-blue-900/20">
              Start Free Demo
            </a>
            <a href="#features" className="px-8 py-3 text-base font-medium text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 transition">
              Learn More
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-slate-50 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-slate-900 mb-4">
            Everything You Need to Transform Education
          </h2>
          <p className="text-center text-slate-500 mb-14 max-w-2xl mx-auto">
            From automatic data synchronization to AI-powered recommendations, our platform provides
            the complete analytics toolkit for educational institutions.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Feature
              icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              title="Real-Time Dashboard"
              desc="Monitor KPIs, enrollment trends, and institutional health with near-real-time data that syncs automatically from your systems."
            />
            <Feature
              icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              title="Dropout Early Warning"
              desc="Identify at-risk students before they drop out using attendance, GPA, and engagement signals. Intervene early, save more students."
            />
            <Feature
              icon="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"
              title="Program Analytics"
              desc="Compare program performance, completion rates, and student outcomes. Identify your strongest and weakest programs at a glance."
            />
            <Feature
              icon="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
              title="Labour Market Alignment"
              desc="Match your curriculum to current and future skill demands. Get alerts when programs fall out of alignment with the job market."
            />
            <Feature
              icon="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              title="AI Recommendations"
              desc="Receive actionable, evidence-based suggestions for curriculum updates, student interventions, and new program launches."
            />
            <Feature
              icon="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              title="Automatic Sync"
              desc="Connect once, sync forever. The platform pulls new data automatically at scheduled intervals — no manual uploads needed."
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-slate-900 mb-14">How It Works</h2>
          <div className="space-y-8">
            <Step num={1} title="Connect Your Systems" desc="Securely link your student information system or learning management system. We use read-only access with permission-based integration." />
            <Step num={2} title="Automatic Data Sync" desc="The platform performs an initial full sync, then automatically pulls only new and changed data at scheduled intervals." />
            <Step num={3} title="Analytics & Insights" desc="View your dashboard with real-time KPIs, risk scores, program analytics, and labour market alignment — all computed automatically." />
            <Step num={4} title="Act on Recommendations" desc="Review AI-powered recommendations tailored to your institution. Accept, adapt, or dismiss — you are always in control." />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-[#1e3a5f] px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Transform Your Institution?</h2>
          <p className="text-blue-200 mb-8">
            Join universities and course providers across Azerbaijan who are making data-driven decisions.
          </p>
          <a href="/login" className="inline-block px-8 py-3 text-base font-medium bg-white text-[#1e3a5f] rounded-lg hover:bg-slate-100 transition shadow-lg">
            Request Demo
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between text-sm text-slate-400">
          <span>EduScope — Azerbaijan Higher Education Intelligence</span>
          <span>Built for the future of education</span>
        </div>
      </footer>
    </div>
  );
}

function Feature({ icon, title, desc }: { icon: string; title: string; desc: string }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
      <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
        <svg className="w-5 h-5 text-[#0ea5e9]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
        </svg>
      </div>
      <h3 className="text-base font-semibold text-slate-800 mb-2">{title}</h3>
      <p className="text-sm text-slate-500 leading-relaxed">{desc}</p>
    </div>
  );
}

function Step({ num, title, desc }: { num: number; title: string; desc: string }) {
  return (
    <div className="flex gap-5">
      <div className="shrink-0 w-10 h-10 bg-[#1e3a5f] text-white rounded-full flex items-center justify-center text-sm font-bold">
        {num}
      </div>
      <div>
        <h3 className="text-lg font-semibold text-slate-800">{title}</h3>
        <p className="text-sm text-slate-500 mt-1">{desc}</p>
      </div>
    </div>
  );
}
