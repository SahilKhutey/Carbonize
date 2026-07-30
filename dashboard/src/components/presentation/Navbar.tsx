import { useState } from 'react';

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const links = [
    { href: '#problem', label: 'Problem' },
    { href: '#solution', label: 'Solution' },
    { href: '#solv-237', label: 'SOLV-0237' },
    { href: '#roi', label: 'ROI' },
    { href: '#validation', label: 'Validation' },
    { href: '#architecture', label: 'Architecture' },
    { href: '#team', label: 'Team' },
    { href: '#ask', label: 'Ask' },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800/50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#" className="flex items-center gap-2.5 font-extrabold text-lg">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-lg flex items-center justify-center text-white font-black">
            C
          </div>
          <span>Carbonize</span>
        </a>

        <div className="hidden md:flex items-center gap-8">
          {links.map((link) => (
            <a key={link.href} href={link.href} className="text-slate-300 hover:text-white text-sm font-medium transition-colors">
              {link.label}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <a href="#contact" className="btn btn-secondary hidden sm:inline-flex">
            Contact
          </a>
          <a href="#roi" className="btn btn-primary">
            Try Demo
          </a>
        </div>
      </div>
    </nav>
  );
}
