git add .github/ docs/ manuscript/ business/ cla/ data/ hardware/ scripts/ .editorconfig .env.example .gitattributes .gitignore .markdownlint.yaml .pre-commit-config.yaml .secrets.baseline CHANGELOG.md CITATION.cff COMMERCIAL-LICENSING.md LICENSE Makefile SECURITY.md TRADEMARKS.md README.md
git commit -m "docs: Update README, GitHub workflows, templates, and project documentation"

git rm "Stochastic Modeling of Industrial Emission Control - Google Gemini--2.pdf" "Stochastic Modeling of Industrial Emission Control - Google Gemini--3.pdf" "Stochastic Modeling of Industrial Emission Control - Google Gemini--cost breakdowns.pdf" "Stochastic Modeling of Industrial Emission Control - Google Gemini.pdf" "carbonlattice_decarbonization_pitch (1).html" "carbonlattice_decarbonization_pitch.html" "system_digital_twin.html" "technical_document_portal.html" "technical_manual.html"
git commit -m "chore: Remove outdated PDFs and HTML files"

git add deployment/ deploy/
git commit -m "deploy: Update Terraform configurations and deployment scripts"

git add packages/shared/ packages/workers/
git commit -m "feat(workers): Implement status machine, observability, and storage tasks"

git add packages/sim-core/
git commit -m "feat(sim-core): Enhance kinetic engine, UQ monte carlo/sobol, and parameters"

git add packages/api/
git commit -m "feat(api): Add dependencies, new routes, schemas, and websocket support"

git add packages/web/ package.json pnpm-lock.yaml pnpm-workspace.yaml pyproject.toml poetry.lock numerical_validation_report.html
git commit -m "feat(web): Update web UI components, hooks, and project dependencies"

git add .
git commit -m "chore: Catch-all for any remaining modified or untracked files"

git push origin main
