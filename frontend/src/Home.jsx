import "./App.css";

function GitHubIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2.15c-3.2.7-3.88-1.36-3.88-1.36-.53-1.34-1.3-1.7-1.3-1.7-1.07-.73.08-.72.08-.72 1.18.08 1.8 1.21 1.8 1.21 1.05 1.8 2.75 1.28 3.42.98.1-.76.41-1.28.75-1.57-2.55-.29-5.23-1.28-5.23-5.68 0-1.25.45-2.28 1.2-3.08-.12-.3-.52-1.46.11-3.04 0 0 .98-.31 3.2 1.18a11.1 11.1 0 0 1 5.82 0c2.22-1.49 3.2-1.18 3.2-1.18.63 1.58.23 2.74.11 3.04.75.8 1.2 1.83 1.2 3.08 0 4.41-2.69 5.38-5.25 5.67.42.36.8 1.06.8 2.14v3.18c0 .31.21.68.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
    </svg>
  );
}

function FolderIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true">
      <path d="M2.5 5.75A1.75 1.75 0 0 1 4.25 4h3.1l1.7 1.8h6.7A1.75 1.75 0 0 1 17.5 7.55v6.7A1.75 1.75 0 0 1 15.75 16h-11A2.25 2.25 0 0 1 2.5 13.75v-8Z" />
      <path d="M2.75 8h14.5" />
    </svg>
  );
}

function FileIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true">
      <path d="M5 2.75h6l4 4v10.5H5a1.5 1.5 0 0 1-1.5-1.5v-11A2 2 0 0 1 5.5 2.75Z" />
      <path d="M11 3v4h4M6.5 11h7M6.5 14h7" />
    </svg>
  );
}

function FeatureIcon({ kind }) {
  const Icon = kind === "folder" ? FolderIcon : kind === "file" ? FileIcon : GitHubIcon;
  return (
    <span className={`feature-icon feature-icon-${kind}`} aria-hidden="true">
      <Icon />
    </span>
  );
}

function Home() {
  return (
    <main className="intro-page">
      <nav className="intro-nav">
        <a className="brand-lockup" href="/" aria-label="CodeLense AI home">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32">
              <path d="M13.5 5.5a8 8 0 1 0 0 16 8 8 0 0 0 0-16Z" />
              <path d="m19.5 19.5 7 7M10.5 13.5h6M13.5 10.5v6" />
            </svg>
          </span>
          <span>CodeLense <strong>AI</strong></span>
        </a>
        <a className="intro-nav-button" href="/workspace">
          Open workspace <span aria-hidden="true">↗</span>
        </a>
      </nav>

      <section className="intro-hero">
        <div className="intro-copy">
          <span className="intro-eyebrow">
            <span className="intro-eyebrow-dot" />
            CODEBASE INTELLIGENCE, AT A GLANCE
          </span>
          <h1>Get to know any codebase, <span>faster.</span></h1>
          <p className="intro-description">
            Turn a GitHub repository into a clear map of its architecture,
            files, and technologies—and get answers grounded in the code.
          </p>
          <a className="intro-cta" href="/workspace">
            Explore your repository <span aria-hidden="true">→</span>
          </a>
          <p className="intro-note">
            Start with a public GitHub repository URL. No setup required.
          </p>
        </div>

        <div className="intro-preview" aria-label="Codebase analysis preview">
          <div className="preview-window">
            <div className="preview-topbar">
              <div className="preview-dots" aria-hidden="true">
                <span />
                <span />
                <span />
              </div>
              <span className="preview-github-icon" aria-hidden="true">
                <GitHubIcon />
              </span>
              <span className="preview-repository">octo / sample-project</span>
              <span className="preview-ready">ANALYZED</span>
            </div>
            <div className="preview-content">
              <div className="preview-sidebar">
                <span className="preview-sidebar-label">REPOSITORY MAP</span>
                <span className="preview-tree-item">
                  <span className="preview-tree-chevron">⌄</span>
                  <FolderIcon />
                  src
                </span>
                <span className="preview-tree-item nested">
                  <span className="preview-tree-chevron">⌄</span>
                  <FolderIcon />
                  services
                </span>
                <span className="preview-tree-item nested deeper">
                  <FileIcon />
                  AuthService.ts
                </span>
                <span className="preview-tree-item nested deeper">
                  <FileIcon />
                  UserService.ts
                </span>
                <span className="preview-tree-item">
                  <span className="preview-tree-chevron">›</span>
                  <FolderIcon />
                  tests
                </span>
              </div>
              <div className="preview-main">
                <span className="preview-sidebar-label">QUICK OVERVIEW</span>
                <div className="preview-stat-row">
                  <div className="preview-stat">
                    <strong>TypeScript</strong>
                    <span>Primary language</span>
                  </div>
                  <div className="preview-stat">
                    <strong>Node.js</strong>
                    <span>Backend</span>
                  </div>
                </div>
                <div className="preview-insight">
                  <span className="preview-insight-icon">✦</span>
                  <div>
                    <strong>Ask your codebase</strong>
                    <p>Find answers with relevant files and line references.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="preview-prompt">
              <span>⌕</span>
              Where is authentication handled?
              <b>↗</b>
            </div>
          </div>
          <span className="preview-orbit orbit-one" />
          <span className="preview-orbit orbit-two" />
        </div>
      </section>

      <section className="intro-features" aria-label="What you can do">
        <article className="intro-feature">
          <FeatureIcon kind="github" />
          <div>
            <span className="feature-number">01 · REPOSITORY</span>
            <h2>See the structure</h2>
            <p>Explore technologies, architecture, and files in one place.</p>
          </div>
        </article>
        <article className="intro-feature">
          <FeatureIcon kind="folder" />
          <div>
            <span className="feature-number">02 · INSIGHTS</span>
            <h2>Ask better questions</h2>
            <p>Understand how features work using answers grounded in source code.</p>
          </div>
        </article>
        <article className="intro-feature">
          <FeatureIcon kind="file" />
          <div>
            <span className="feature-number">03 · SOURCE FILES</span>
            <h2>Go straight to the code</h2>
            <p>Follow answer sources into the relevant file and lines.</p>
          </div>
        </article>
      </section>

      <footer className="intro-footer">
        <span>CodeLense AI</span>
        <span>Understand the code. Move forward with confidence.</span>
      </footer>
    </main>
  );
}

export default Home;
