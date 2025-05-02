# 04 WAS Studio – Front-End Workbench

## 1. Tech Stack
* Vite + React + TypeScript
* Monaco Editor core (2 MB gzip)
* USWDS components for a11y (WCAG 2.1 AA)
* Yjs for realtime collaboration (WebRTC + WS fallback)

## 2. Feature Roadmap
| Phase | Feature | KPI |
|-------|---------|-----|
| 2 | Document viewer, metadata pane | LCP <2 s |
| 3 | Contributor upload panel (PR flow) | form error rate <1 % |
| 4 | Search bar (gateway via **authz-edge**) | results render <400 ms |
| 4 | Graph visualization tab (calls **studio-graph**) | zoom FPS >30 |

## 3. Bundling & Deployment
* Single-page app on Cloudflare Pages (`studio.was.tools`).
* API calls flow: `studio.was.tools` → **auth.was.foundation** (JWT) → authz-edge Worker → studio-graph (gRPC mesh) → backend services.
* Adopt **BFF pattern only for latency-critical paths**; otherwise direct REST/gRPC.
* Service Worker for offline cache of Monaco + wasm.
* Build size target: ≤150 kB critical JS.

## 4. A11y & i18n
* Axe-core CI fail if score <90.
* `lang` detection field drives UI locale switch.

## 5. Next Steps (Weeks 2-4)
1. Scaffold Vite project.
2. Integrate Monaco read-only.
3. Lighthouse & axe-core baseline audit.

---

## 6. Packaging & Cross-Platform Distribution

| Target | Strategy | Build Artifact | Store/Channel |
|--------|----------|---------------|---------------|
| **PWA (baseline)** | Web App Manifest + Service Worker; `vite-plugin-pwa` | `dist/` static files | Installable via browser, Add-to-Home-Screen |
| **Windows / macOS / Linux** | **Tauri** wrapper (Rust) – lightweight, auto-update | MSI (Win), DMG (mac), AppImage/DEB/RPM (Linux) | GitHub Releases, Winget, Snapcraft |
| **Android** | **Capacitor** bridge → native WebView; push notifications via FCM | `.aab` (Play Store) | Google Play (Internal → Production) |
| **iOS** | Capacitor bridge; Live Activities optional | `.ipa` (App Store) | TestFlight → App Store |

### Additional Build Pipeline Steps
1. GitHub Action matrix: `web`, `tauri-win`, `tauri-linux`, `tauri-mac`, `cap-android`, `cap-ios`.
2. Code-Signing:
   * Windows: SignTool + Azure Key Vault cert.
   * macOS: Apple Developer ID; notarize via altool.
   * iOS/Android: Apple / Google upload keys managed in GH Secrets.
3. Post-build scan with OWASP Dependency-Check.

### Store Compliance Checklist
* App Privacy labels → only collect auth token + opt-in analytics.
* Pass App Store Review guidelines (§2.3.1 Web Content).
* PlayConsole Data Safety form.

### Roadmap Slots
| Week | Milestone |
|------|-----------|
| 8 | PWA manifest & offline support |
| 10 | Tauri desktop alpha (Win) |
| 12 | Capacitor Android beta on Play Internal |
| 14 | iOS TestFlight build |
| 16 | GA across all stores |
