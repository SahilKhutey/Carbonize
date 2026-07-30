import { useEffect } from 'react';
import Navbar from '../components/presentation/Navbar';
import Hero from '../components/presentation/Hero';
import Problem from '../components/presentation/Problem';
import Solution from '../components/presentation/Solution';
import Solv237 from '../components/presentation/Solv237';
import ROICalculator from '../components/presentation/ROICalculator';
import Validation from '../components/presentation/Validation';
import Market from '../components/presentation/Market';
import Architecture from '../components/presentation/Architecture';
import Team from '../components/presentation/Team';
import Roadmap from '../components/presentation/Roadmap';
import Ask from '../components/presentation/Ask';
import CTA from '../components/presentation/CTA';
import Footer from '../components/presentation/Footer';

export default function PresentationLanding() {
  useEffect(() => {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const targetStr = (anchor as HTMLAnchorElement).getAttribute('href');
        if (targetStr && targetStr !== '#') {
          const target = document.querySelector(targetStr);
          if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    });

    const handleScroll = () => {
      const nav = document.querySelector('nav');
      if (nav) {
        if (window.scrollY > 100) {
          nav.classList.add('scrolled');
        } else {
          nav.classList.remove('scrolled');
        }
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased overflow-x-hidden">
      <Navbar />
      <Hero />
      <Problem />
      <Solution />
      <Solv237 />
      <ROICalculator />
      <Validation />
      <Market />
      <Architecture />
      <Team />
      <Roadmap />
      <Ask />
      <CTA />
      <Footer />
    </div>
  );
}
