export default function Footer() {
  return (
    <footer>
      <div className="footer-grid">
        <div>
          <h3 className="text-xl font-extrabold mb-2">Carbonize</h3>
          <p className="text-sm text-slate-400">
            AI-designed chemistry for industrial carbon capture. Founded 2023. Backed by industry leaders.
          </p>
        </div>
        <div className="footer-col">
          <h4>Product</h4>
          <a href="#solution">Solution</a>
          <a href="#solv-237">SOLV-0237</a>
          <a href="#roi">ROI Calculator</a>
          <a href="#architecture">Architecture</a>
        </div>
        <div className="footer-col">
          <h4>Resources</h4>
          <a href="#validation">Validation</a>
          <a href="#team">Team</a>
          <a href="#roadmap">Roadmap</a>
          <a href="#ask">Investing</a>
        </div>
        <div className="footer-col">
          <h4>Contact</h4>
          <a href="mailto:hello@carbonize.io">hello@carbonize.io</a>
          <a href="mailto:investors@carbonize.io">investors@carbonize.io</a>
          <a href="mailto:partnerships@carbonize.io">partnerships@carbonize.io</a>
        </div>
      </div>
      <div className="footer-bottom">
        <div>© 2025 Carbonize, Inc. All rights reserved.</div>
        <div>Made with 🌱 for the planet</div>
      </div>
    </footer>
  );
}
