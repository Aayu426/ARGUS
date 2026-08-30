import Link from 'next/link';
import { Shield, LayoutDashboard, Database, Activity, Map, FileStack, Settings, Menu } from 'lucide-react';
import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import "./globals.css";
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });
const mono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });

export const metadata: Metadata = {
  title: "Project ARGUS | Forensic Intelligence",
  description: "Advanced Social Media Forensics Platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body suppressHydrationWarning className={`${inter.variable} ${mono.variable} font-sans bg-background text-foreground antialiased selection:bg-primary/20`}>
        <Providers>
          <div className="flex h-screen w-full bg-background overflow-hidden text-foreground">
            {/* Sidebar - Intelligence Style */}
            <aside className="hidden w-64 flex-col border-r border-slate-800 bg-slate-900/50 backdrop-blur-xl md:flex">
              <div className="flex h-16 items-center px-6 border-b border-slate-800 bg-slate-900/80">
                <Shield className="h-6 w-6 text-primary mr-2" />
                <span className="text-lg font-bold tracking-wider text-primary font-mono">ARGUS SYSTEM</span>
              </div>

              <nav className="flex-1 space-y-2 p-4">
                <NavItem href="/" icon={<LayoutDashboard />} label="Command Center" />
                <div className="pt-4 pb-2 px-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest font-mono">Modules</div>
                <NavItem href="/evidence" icon={<Database />} label="Evidence Vault" />
                <NavItem href="/nlp" icon={<FileStack />} label="NLP Analysis" />
                <NavItem href="/vision" icon={<Activity />} label="Visual Lab" />
                <NavItem href="/graph" icon={<Map />} label="Network Graph" />

                <div className="mt-auto pt-10">
                  <NavItem href="/settings" icon={<Settings />} label="System Config" />
                </div>
              </nav>

              <div className="p-4 border-t border-slate-800 text-[10px] text-slate-500 font-mono bg-slate-950/30">
                <div className="flex justify-between">
                  <span>VER: 2.0.0-ELITE</span>
                  <span className="text-emerald-500 animate-pulse">SECURE</span>
                </div>
                <div className="mt-1">NIST-800-53 COMPLIANT</div>
              </div>
            </aside>

            {/* Main Content */}
            <div className="flex flex-1 flex-col overflow-hidden relative">
              {/* Background Grid Effect - Improved */}
              <div className="absolute inset-0 z-0 opacity-[0.05] pointer-events-none"
                style={{
                  backgroundImage: 'linear-gradient(rgba(14, 165, 233, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(14, 165, 233, 0.1) 1px, transparent 1px)',
                  backgroundSize: '40px 40px',
                  maskImage: 'radial-gradient(circle at center, black, transparent 80%)'
                }}>
              </div>

              <header className="flex h-16 items-center border-b border-slate-800 bg-slate-900/30 px-6 z-10 backdrop-blur-md">
                <div className="md:hidden">
                  <Menu className="h-6 w-6 text-slate-400" />
                </div>
                <div className="ml-auto flex items-center space-x-6">
                  {/* Status Indicators */}
                  <div className="flex items-center space-x-4 text-xs font-mono text-slate-500">
                    <div className="flex items-center space-x-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-[pulse_2s_infinite]"></div>
                      <span className="text-emerald-500">SYSTEM ONLINE</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="h-1.5 w-1.5 rounded-full bg-sky-500"></div>
                      <span>LATENCY: 12ms</span>
                    </div>
                  </div>

                  <div className="h-8 w-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-300">
                    OP
                  </div>
                </div>
              </header>

              <main className="flex-1 overflow-auto p-6 z-10 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
                {children}
              </main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}

function NavItem({ href, icon, label, active = false }: { href: string, icon: any, label: string, active?: boolean }) {
  return (
    <Link href={href} className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 group relative overflow-hidden ${active ? 'bg-primary/10 text-primary border border-primary/20' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'}`}>
      {active && <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary"></div>}
      <div className={`h-5 w-5 ${active ? 'text-primary' : 'text-slate-500 group-hover:text-white'}`}>{icon}</div>
      <span className="font-medium text-sm">{label}</span>
    </Link>
  )
}
