# 🧠 BrainSpark — CoGAT Practice for K–8

**A free, ad-free, offline-capable CoGAT (Cognitive Abilities Test) practice app for students in Kindergarten through Grade 8.**

BrainSpark runs entirely in the browser — no installation, no accounts required. Students sign in with Google to sync progress across devices, or play in guest mode with everything stored locally.

---

## ✨ Highlights

- **2,500+ questions** across all 9 CoGAT question types and every grade from K–8
- **7 kid-friendly themes** — Space, Superhero, Royal Quest, Jungle, Unicorn, Magic Realm, Candy Kingdom
- **Offline-first** — works without internet after the first load; questions are cached in the browser
- **Google Sign-In sync** — scores, streaks, and settings follow you across any device
- **Daily streak system** with full-screen milestone celebrations
- **Insights dashboard** — accuracy trends, per-battery breakdowns, and error-category analysis
- **Question pipeline tool** — built-in AI generator (Claude API) with deduplication, validation, and export
- **Zero dependencies to deploy** — two static files, any host will do
- **Free and open** for educational use

---

## 📁 Repository Structure

```
brainspark/
├── getsmart.html              # Main student app — the only file users need
├── questions.json             # Full question bank (2,500+ questions, K–8)
├── refresh-questionairre.html # Question pipeline tool (generate · dedup · validate · merge)
├── gen_questions.py           # Python script to programmatically generate questions
├── pytest.ini                 # Test configuration
└── tests/
    ├── conftest.py                  # Shared fixtures
    ├── test_questions_integrity.py  # Data-integrity tests for questions.json
    ├── test_gen_questions.py        # Unit tests for the generator script
    └── test_e2e.py                  # End-to-end Playwright browser tests
```

---

## 🚀 Quick Start

### Local development

```bash
# Clone the repo
git clone https://github.com/yourname/brainspark.git
cd brainspark

# Start a local server (required — Google Sign-In needs an HTTP origin)
python3 -m http.server 8080

# Open in your browser
open http://localhost:8080/getsmart.html
```

> Opening `getsmart.html` directly as a `file://` URL will not work for Google Sign-In. Use the local server or deploy to a host.

### Guest mode (no Firebase required)

Click **Play as Guest** on the login screen. All data is stored in the browser's `localStorage`. No Firebase configuration is needed to use the app in guest mode.

---

## 🌐 Deployment

The entire app is two static files: `getsmart.html` and `questions.json`. Any static host works.

### Option 1 — Cloudflare Pages ⭐ Recommended

Free forever, global CDN, unlimited bandwidth.

1. Create a free account at [pages.cloudflare.com](https://pages.cloudflare.com)
2. Click **Create a project → Upload assets**
3. Upload both `getsmart.html` and `questions.json` into the same folder
4. Name your project (e.g. `brainspark`) → **Deploy**
5. Add your Pages domain to Firebase → **Authentication → Settings → Authorized domains**

### Option 2 — Netlify Drop

No account needed to try.

1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag a folder containing both files onto the page → instant HTTPS URL
3. Sign up for a free account to keep the URL permanent and redeploy

### Option 3 — GitHub Pages

1. Fork this repo (or push to a new public repo)
2. Go to **Settings → Pages → Source → Deploy from branch → main**
3. App is live at `https://yourusername.github.io/brainspark`
4. Update questions by editing `questions.json` in the GitHub editor — users get the new version on next open

### Option 4 — AWS S3 + CloudFront

For custom domains or higher traffic.

1. Create an S3 bucket with **Static Website Hosting** enabled and public read
2. Upload both files; add a CORS rule allowing GET from `*`
3. Optionally front with CloudFront for global CDN performance
4. Free tier: 5 GB storage + 20,000 GET requests/month

---

## 🔥 Firebase Setup (optional — required for cross-device sync)

BrainSpark works in guest mode without any Firebase setup. To enable Google Sign-In and cross-device sync:

### 1. Create a Firebase project

1. Go to [console.firebase.google.com](https://console.firebase.google.com) → **Add project**
2. Disable Google Analytics if not needed → **Create project**

### 2. Register the web app

1. Click the **`</>`** (web) icon on the project overview page
2. Give the app a nickname → **Register app**
3. Copy the `firebaseConfig` object and paste it into `getsmart.html`, replacing the `REPLACE_WITH_YOUR_...` placeholders near the top of the file

### 3. Enable Google Sign-In

1. **Build → Authentication → Get started → Sign-in method → Google → Enable**
2. Pick a support email → **Save**
3. Under **Settings → Authorized domains** → add your live domain (`localhost` is already included)

### 4. Create the Firestore database

1. **Build → Firestore Database → Create database → Start in production mode**
2. Choose a region → **Enable**
3. Click the **Rules** tab and replace the default rules with:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

4. Click **Publish**

> These rules ensure each user can only access their own data, even if someone reverse-engineers the public API key.

---

## 🎯 App Features

### For Students

| Feature | Detail |
|---|---|
| **Grade selector** | K–8, each grade has calibrated difficulty |
| **CoGAT batteries** | Verbal · Quantitative · Non-Verbal · Mixed |
| **Session length** | 9 questions · 15-minute timer · overtime allowed |
| **Themes** | 7 themes with unique color palettes and particle effects |
| **Personalization** | Enter your name for custom greetings and shoutouts |
| **Daily streak** | Tracked with full-screen milestone celebrations |
| **Session resume** | In-progress sessions saved; pick up where you left off |
| **Offline play** | Questions cached locally; works without internet |

### For Parents & Teachers

| Feature | Detail |
|---|---|
| **Insights dashboard** | Accuracy trends, battery breakdown, error categories, session history |
| **Cross-device sync** | Google Sign-In saves all data to Firestore |
| **Guest mode** | No account needed; data in browser `localStorage` |
| **No ads, no tracking** | Questions fetched from your host only; no third-party analytics |
| **Smart deduplication** | Questions from the last 4 sessions are avoided |

---

## 🔐 Authentication & Data Storage

| Mode | Sign-in | Storage | Cross-device |
|------|---------|---------|--------------|
| **Google account** | Google Sign-In popup | Firebase Firestore | ✅ Yes |
| **Guest** | None | Browser `localStorage` | ❌ This device only |

Users can switch from guest to signed-in at any time via the **Sign in** button. All guest data is preserved on sign-in.

### Firestore data model

```
users/{uid}/
  settings         { theme, playerName, lastGrade, welcomeSeen, shownMilestones }
  activeSession    { ...in-progress quiz state }
  sessions/{id}    { ...completed session data }
```

All Firestore writes also update `localStorage` immediately as an offline-first cache. If Firestore is unavailable the app continues working locally.

---

## 📐 Grade Level Guide

| Grade | Age | CoGAT Level | Difficulty | Focus |
|-------|-----|-------------|------------|-------|
| K | 5–6 | Primary | Easy | Colors, shapes, counting 1–10, simple patterns |
| 1 | 6–7 | Primary | Easy | Animals/objects, skip counting, simple equations |
| 2 | 7–8 | Primary | Easy/Medium | Analogies, skip counting by 5s, color-shape matrices |
| 3 | 8–9 | Level 7/8 | Easy/Medium | Antonyms, doubling sequences, 3×3 matrices |
| 4 | 9–10 | Level 9/10 | Medium | Multi-step analogies, Fibonacci, paper folding |
| 5 | 10–11 | Level 11/12 | Medium/Hard | Advanced vocabulary, algebra intro, dot-matrix patterns |
| 6 | 11–12 | Level 13/14 | Hard | Science vocabulary, perfect squares, linear equations |
| 7 | 12–13 | Level 15/16 | Hard | Literary devices, prime numbers, square roots |
| 8 | 13–14 | Level 17/18 | Hard | Advanced vocab, functions, complex spatial reasoning |

---

## 📦 Question Bank

### Stats

| Metric | Value |
|--------|-------|
| Total questions | **2,501** |
| Grades covered | K – 8 (all 9 grades) |
| Sessions possible without repeating | ~278 |
| Batteries | Verbal · Quantitative · Non-Verbal |

### Question types

| Battery | Type | Description |
|---------|------|-------------|
| Verbal | `verbal-analogies` | Word relationship pairs |
| Verbal | `verbal-classification` | Odd-one-out from a group |
| Verbal | `sentence-completion` | Fill in the missing word |
| Quantitative | `number-series` | Find the next number in a sequence |
| Quantitative | `number-analogies` | Numeric relationship pairs |
| Quantitative | `number-puzzles` | Equations, area, percentages, word problems |
| Non-Verbal | `figure-matrices` | 2×2 and 3×3 visual pattern completion |
| Non-Verbal | `paper-folding` | Predict holes after folding and punching |
| Non-Verbal | `figure-classification` | Which figure belongs to the group? |

### JSON schema

Every question follows this structure. All fields are required.

```json
{
  "id": "Q00001",
  "grade": "3",
  "battery": "quantitative",
  "type": "number-series",
  "difficulty": "medium",
  "text": "What comes next?  2, 4, 6, 8, ___",
  "svg": null,
  "options": [
    { "label": "A", "text": "9",  "svg": null },
    { "label": "B", "text": "10", "svg": null },
    { "label": "C", "text": "11", "svg": null },
    { "label": "D", "text": "12", "svg": null }
  ],
  "answer": 1,
  "explanation": "Add 2 each time. 8 + 2 = 10.",
  "tags": ["number-series", "3", "medium"]
}
```

#### Field reference

| Field | Type | Values | Notes |
|-------|------|--------|-------|
| `id` | string | unique | Never reuse — user history is keyed to IDs |
| `grade` | string | `"K"`, `"1"`–`"8"` | Maps to grade selector |
| `battery` | string | `verbal` · `quantitative` · `non-verbal` | CoGAT battery |
| `type` | string | See table above | Question sub-type |
| `difficulty` | string | `easy` · `medium` · `hard` | |
| `text` | string | — | Question text shown to student |
| `svg` | string \| null | inline SVG or `null` | Main question graphic |
| `options` | array | 4 items | Each has `label`, `text`, `svg` |
| `answer` | number | 0–3 | Zero-based index of correct option |
| `explanation` | string | — | Kid-friendly explanation shown after answering |
| `tags` | string[] | — | Used for analytics and filtering |

### Updating questions (zero-downtime)

1. Add questions to `questions.json`; bump the `"version"` string (e.g. `2026-05-01-v1`)
2. Upload **only `questions.json`** to your host
3. The app detects the new version on next open and re-fetches automatically
4. Users mid-session are not interrupted

---

## 🔬 Question Pipeline Tool

`refresh-questionairre.html` is a standalone 4-step tool for generating, deduplicating, validating, and merging questions into the bank. Open it directly in a browser — no server required.

### Step 1 — Load + Generate

**Load existing questions:**
- Drop your current `questions.json` onto the upload zone, or paste raw JSON

**Generate new questions with AI (Claude):**
- Enter your [Claude API key](https://console.anthropic.com/)
- Choose: **grade** (K–8) · **battery** · **question type** · **difficulty** · **count** (1–50)
- Click **✨ Generate questions** — Claude writes the questions and auto-loads them as the new batch
- The tool automatically passes all existing questions to Claude so it generates only novel content

### Step 2 — Compare & Deduplicate

- Detects duplicate question IDs vs. the existing bank
- Detects identical or near-identical question text (normalized comparison)
- Detects duplicates within the new batch itself
- Auto-assigns unique IDs to questions with missing or conflicting IDs
- Configure ID prefix and starting number

### Step 3 — Validate with AI

Each new question is reviewed by Claude against 7 checks:

1. Answer is unambiguously correct
2. Distractors are plausible but clearly wrong
3. Language is age-appropriate for the declared grade
4. No cultural bias or regionally specific content
5. Question tests the declared cognitive skill
6. Difficulty matches the declared level
7. No ambiguous wording

Configure concurrency (1–3 parallel requests) and a rejection threshold. Failed questions can be excluded, flagged, or included.

### Step 4 — Review & Export

- Preview the full merged question list with battery/difficulty/status filters
- Set the new `version` string
- Export a full `questions.json` (ready to upload) or a patch file (new questions only)
- Built-in hosting guide

---

## 🐍 Programmatic Question Generation

`gen_questions.py` creates questions entirely in Python — no AI API needed. It uses:

- **Arithmetic templates** for number series, analogies, and puzzles (guaranteeing mathematical correctness)
- **Hand-crafted template banks** for verbal and non-verbal questions

```bash
python3 gen_questions.py
```

The script deduplicates by question text before writing and prints a per-type summary.

---

## 🧪 Testing

```bash
# Install dependencies
pip install pytest pytest-playwright
playwright install chromium

# Run all unit tests (no browser required)
pytest -m unit -v

# Run data-integrity tests for questions.json
pytest tests/test_questions_integrity.py -v

# Run generator unit tests
pytest tests/test_gen_questions.py -v

# Run end-to-end Playwright tests
python3 -m http.server 8080 &
pytest -m e2e -v
```

### Test suite overview

| File | Marks | What it tests |
|------|-------|---------------|
| `test_questions_integrity.py` | `unit` | Schema, uniqueness, battery/type consistency, option validity for every question in `questions.json` |
| `test_gen_questions.py` | `unit`, `slow` | Generator output: volume, uniqueness, schema, grade/battery distribution |
| `test_e2e.py` | `e2e` | Full browser flow: login screen, guest mode, grade/battery selection, question rendering, answer submission, insights screen |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│               Static Host (Cloudflare / GitHub Pages)     │
│  ┌────────────────────┐    ┌───────────────────────────┐  │
│  │  getsmart.html     │    │   questions.json           │  │
│  │  (all-in-one app)  │    │   (versioned, cacheable)   │  │
│  └────────┬───────────┘    └─────────────┬─────────────┘  │
└───────────┼────────────────────────────  ┼───────────────┘
            │                              │
            ▼                              ▼
┌──────────────────────────────────────────────────────────┐
│                      User's Browser                       │
│                                                           │
│  ┌───────────────────┐    ┌─────────────────────────────┐ │
│  │  localStorage     │◄───┤  Offline-first write cache  │ │
│  │  (fast / offline) │    │  (written before Firestore) │ │
│  └────────┬──────────┘    └─────────────────────────────┘ │
│           │ sync (signed-in users only)                    │
│           ▼                                                │
│  ┌───────────────────┐    ┌─────────────────────────────┐ │
│  │  Firebase         │    │  Question version check     │ │
│  │  Auth + Firestore │    │  → fetch if new version     │ │
│  │  (per-user data)  │    │  → serve from cache if same │ │
│  └───────────────────┘    └─────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### Data flow

1. **App opens** → Firebase `onAuthStateChanged` resolves
2. **Signed in** → load settings + sessions from Firestore; fall back to `localStorage`
3. **Guest** → load entirely from `localStorage`
4. **Question cache** → `version` checked; fetched from host when new, served from cache otherwise
5. **Every write** → `localStorage` updated immediately, then Firestore synced in the background
6. **Questions update** → increment `version` in `questions.json` and re-upload the file

---

## 🎨 Themes

| Theme | CSS key | Special Effect |
|-------|---------|----------------|
| Space Explorer 🚀 | `space` | Floating star particles |
| Superhero ⚡ | `superhero` | Power-burst particles |
| Royal Quest 👑 | `princess` | Flower-petal particles |
| Jungle Adventure 🌿 | `jungle` | Falling leaf particles |
| Unicorn Dreams 🦄 | `unicorn` | Rainbow cursor trail |
| Magic Realm 🔮 | `magic` | Live star constellation canvas |
| Candy Kingdom 🍭 | `candyland` | Bouncing candy particles |

To add a new theme:

1. Add a CSS block to `getsmart.html`:
   ```css
   body.theme-mytheme {
     --bg: #...; --surface: #...; --accent: #...;
     /* mirror any existing theme block for the full variable list */
   }
   ```
2. Register it in the `THEMES` JS object:
   ```javascript
   mytheme: { icon: '🦋', word: 'Champion', logo: '🦋 BrainSpark' }
   ```
3. Add a theme card in the themes screen HTML
4. Add particle symbols to `createParticles()`

---

## 📊 Insights Dashboard

The **Progress** screen shows five charts powered by [Chart.js 4](https://www.chartjs.org/):

| Chart | What it shows |
|-------|---------------|
| Accuracy Trend | Score % per session (line) |
| Correct vs Wrong | Stacked bar per session |
| Battery Performance | Verbal / Quantitative / Non-Verbal accuracy over time (line) |
| Error Categories | Which question types need the most practice (horizontal bar) |
| Session History | Scrollable list: date · score · grade · battery · overtime flag |

Each chart includes a **?** tooltip written in kid-friendly language.

---

## 🔥 Streak Milestones

| Days | Badge | Color |
|------|-------|-------|
| 5 | 🔥 On Fire! | Orange |
| 10 | ⚡ Supercharged! | Gold |
| 15 | 🌈 Rainbow Streak! | Purple |
| 20 | 🌟 Star Streak! | Violet |
| 40 | 🚀 Blast Off! | Blue |
| 100 | 💎 Diamond Mind! | Cyan |
| 200 | 👑 Legend Status! | Amber |
| 500 | 🏆 Hall of Fame! | Green |

Milestones trigger a full-screen animation with expanding rings, confetti, and a personalized message using the student's name.

---

## 🛠️ Customization

### Change the question source URL

In `getsmart.html`:
```javascript
const DATA_SOURCE = 'questions.json'; // replace with a full URL if needed
```

### Change session length

```javascript
const SESSION_QUESTIONS = 9;   // questions per session
const SESSION_MINUTES   = 15;  // minutes before overtime starts
```

---

## ❓ FAQ

**Q: Does this send any data to a server?**
> Only if the user signs in with Google. In that case, session history, streaks, and settings are stored in Firebase Firestore (scoped strictly to their account). In guest mode, everything stays in the browser's `localStorage` — nothing is transmitted.

**Q: Is it safe to expose the Firebase API key in a public repo?**
> Yes — for Firebase web apps the API key is a project identifier, not a secret. Security is enforced by Firestore security rules and Firebase Authentication (users can only read and write their own data). Never commit service account keys or Admin SDK credentials.

**Q: What happens if a guest clears their browser cache?**
> Session history and streaks are reset. Signing in with Google prevents this — all data is in Firestore and restored on any device.

**Q: Can multiple students share one device?**
> Yes, with Google Sign-In — each student uses their own Google account and gets fully isolated data in Firestore. In guest mode, `localStorage` is shared per browser profile.

**Q: How many questions are needed for the app to work well?**
> The app works with as few as 9 (one full session). For good variety, aim for at least 5 questions per grade per battery type (~135 questions for full K–8 coverage). The current bank has 2,501 questions, enough for ~278 non-repeating sessions.

**Q: Why do I sometimes see questions from a different grade?**
> If there aren't enough questions for the selected grade and battery, the app falls back to the full question pool to guarantee a complete 9-question session. Adding more grade-specific questions resolves this.

**Q: Can I add image-based questions?**
> Yes — set `"svg"` to an inline SVG string on a question or option. The app renders SVGs natively for figure matrices, paper folding, and figure classification questions.

---

## 📄 License

Free to use, modify, and distribute for educational purposes.
