# 🧠 BrainSpark — CoGAT Practice for K–8

**Live at [brainspark.stacklets.app](https://brainspark.stacklets.app)**

**A free, ad-free, offline-capable CoGAT (Cognitive Abilities Test) practice app for students in Kindergarten through Grade 8.**

BrainSpark runs entirely in the browser — no installation, no accounts required. Students sign in with Google to sync progress across devices, or play as a guest with everything stored locally.

---

## ✨ Highlights

- **2,550+ questions** across all 9 CoGAT question types and every grade from K–8, including visual SVG figure-matrices
- **15 kid-friendly themes** — Clean Light, Clean Dark, Space, Superhero, Royal Quest, Jungle, Unicorn, Magic Realm, Candy Kingdom, Zen Garden, Science Lab, Math World, Deep Ocean, Scholar's Nook, Pirate's Cove
- **Offline-first** — works without internet after the first load; questions are cached in the browser
- **Google Sign-In sync** — scores, streaks, and settings follow you across any device
- **Daily streak system** with full-screen milestone celebrations
- **Insights dashboard** — accuracy trends, per-battery breakdowns, and weak-area analysis
- **Exam Simulation Mode** — 20-question timed exam with battery breakdown results
- **Mistake Review Mode** — re-practice questions you got wrong in past sessions
- **Achievement badges** — 12 unlockable badges tied to practice milestones
- **Parent Dashboard** — weekly activity chart, battery accuracy, weak question types, session history
- **Audio feedback** — ambient soundscapes per theme (jungle crickets, space drone, pirate shanty, and more) plus sound cues for correct/wrong answers and badge unlocks (toggleable)
- **Free and open** for educational use

---

## 🎯 What's in the App

### Practice Modes

| Mode | Description |
|------|-------------|
| **Standard Session** | 9 questions · 15-minute timer · adaptive difficulty · hints after each answer |
| **Exam Simulation** | 20 questions · 25-minute timer · no hints during the quiz · battery breakdown at end |
| **Review Mistakes** | Re-practice up to 9 questions you got wrong in past sessions |

### CoGAT Batteries & Question Types

| Battery | Question Types |
|---------|---------------|
| **Verbal** | Word analogies · Odd-one-out classification · Sentence completion |
| **Quantitative** | Number series · Number analogies · Number puzzles & equations |
| **Non-Verbal** | Figure matrices (including SVG visual patterns) · Paper folding · Figure classification |

### Adaptive Difficulty

BrainSpark uses a Flow Path Algorithm (ELO-style skill tracking per battery type) to automatically adjust difficulty. Students who answer correctly more often get harder questions; those who struggle get easier ones.

### Insights Dashboard

After completing sessions, the Progress screen shows:
- Accuracy trend over time (line chart)
- Correct vs wrong per session (bar chart)
- Battery performance — Verbal / Quantitative / Non-Verbal accuracy (line chart)
- Error categories — which question types need the most practice (bar chart)
- Full session history with date, score, grade, battery, and mode tags

### Parent Dashboard

Accessible from the Insights screen, the Parent View shows:
- Total sessions, overall accuracy, total time practiced, current streak
- Weekly activity bar chart
- Per-battery accuracy breakdown
- Weakest question types
- Recent session history

### Achievement Badges

12 badges unlock automatically as students hit milestones:

| Badge | How to earn |
|-------|-------------|
| 🌱 First Steps | Complete your first session |
| 🔢 Number Ninja | 50 quantitative correct answers |
| 📚 Word Wizard | 50 verbal correct answers |
| 🔷 Pattern Pro | 50 non-verbal correct answers |
| ⚡ Speed Demon | Complete a session on time |
| 🏆 Perfect Score | Get all questions right in a session |
| 🔥 On Fire | Reach a 5-day daily streak |
| 🌟 Dedicated | Complete 10 sessions |
| 🎯 Sharpshooter | 80%+ accuracy over 20+ questions |
| 🌐 Well-Rounded | Try all 3 battery types |
| 📝 Exam Ace | Score 85%+ in Exam Simulation |
| 🔄 Mistake Master | Complete a Review Mistakes session |

Badge unlocks trigger an animated toast notification with a fanfare sound.

### Daily Streak Milestones

| Days | Celebration |
|------|-------------|
| 5 | 🔥 On Fire! |
| 10 | ⚡ Supercharged! |
| 15 | 🌈 Rainbow Streak! |
| 20 | 🌟 Star Streak! |
| 40 | 🚀 Blast Off! |
| 100 | 💎 Diamond Mind! |
| 200 | 👑 Legend Status! |
| 500 | 🏆 Hall of Fame! |

Milestones trigger a full-screen animation with expanding rings, confetti, and a personalized message.

### Themes

15 themes, each with unique colors, particle effects, and an ambient soundscape:

| Theme | Particles | Ambient Audio |
|-------|-----------|---------------|
| ☀️ Clean Light | Stars & sparkles | Silent |
| 🌑 Clean Dark | Stars & sparkles | Silent |
| 🚀 Space Explorer | Floating star particles | Cosmic drone + radio blips |
| ⚡ Superhero | Power-burst particles | Power thrum + energy pulses |
| 👑 Royal Quest | Flower-petal particles | Harp arpeggios |
| 🌿 Jungle Adventure | Falling leaf particles | Crickets, frogs & wind |
| 🦄 Unicorn Dreams | Rainbow cursor trail | Dreamy shimmer + sparkle arpeggios |
| 🔮 Magic Realm | Live star constellation canvas | Deep drone + descending spell shimmer |
| 🍭 Candy Kingdom | Bouncing candy particles | Glockenspiel melody |
| 🧘 Zen Garden | Calm gradient | Singing bowl tones |
| 🔬 Science Lab | Circuit-board aesthetic | Lab hum + electronic beeps |
| ➕ Math World | Number-grid aesthetic | Mathematical frequency ratios |
| 🌊 Deep Ocean | Wave particles | Rolling wave noise + seagull calls |
| 📚 Scholar's Nook | Book & pen particles | Soft rain on glass + piano |
| ☠️ Pirate's Cove | Skull & anchor particles | Hull drone + wind + shanty melody |

### ✨ SparkCoins & Character Shop

Every correct answer earns **1 SparkCoin**, shown in the top-right badge. Spend **15 SparkCoins** in the Character Shop to unlock one of 25 animated companion characters (Luna, Zippy, Bubbles, Sunny, and more). Unlocked characters cheer for you after correct answers.

- Coins persist across sessions (synced to Firebase when signed in)
- Coins are earned only for newly answered questions, not replays
- Characters each have a unique CSS animation (moonwalk, floss, cartwheel, spin, …)

### Audio Feedback

- **Ambient soundscapes** — each theme plays a unique background audio (see Themes table above)
- Ascending chime on correct answers
- Descending buzz on wrong answers
- Fanfare on badge unlocks
- Toggle on/off with the **🔊 Sound** button in the top bar

---

## 📐 Grade Level Guide

| Grade | Age | CoGAT Level | Focus |
|-------|-----|-------------|-------|
| K | 5–6 | Primary | Colors, shapes, counting 1–10, simple patterns |
| 1 | 6–7 | Primary | Animals/objects, skip counting, simple equations |
| 2 | 7–8 | Primary | Analogies, skip counting by 5s, color-shape matrices |
| 3 | 8–9 | Level 7/8 | Antonyms, doubling sequences, 3×3 matrices |
| 4 | 9–10 | Level 9/10 | Multi-step analogies, Fibonacci, paper folding |
| 5 | 10–11 | Level 11/12 | Advanced vocabulary, algebra intro, dot-matrix patterns |
| 6 | 11–12 | Level 13/14 | Science vocabulary, perfect squares, linear equations |
| 7 | 12–13 | Level 15/16 | Literary devices, prime numbers, square roots |
| 8 | 13–14 | Level 17/18 | Advanced vocab, functions, complex spatial reasoning |

---

## 🔐 Sign-In & Data Storage

| Mode | Sign-in | Storage | Cross-device |
|------|---------|---------|--------------|
| **Google account** | Google Sign-In | Firebase Firestore | ✅ Yes |
| **Guest** | None | Browser `localStorage` | This device only |

Students can switch from guest to a signed-in account at any time — all guest progress is preserved.

---

## ❓ FAQ

**Q: Does this send any data to a server?**
> Only if the student signs in with Google. In that case, session history, streaks, and settings are stored in their Firebase account. In guest mode, everything stays in the browser — nothing is transmitted.

**Q: What happens if a guest clears their browser cache?**
> Session history and streaks are reset. Signing in with Google prevents this.

**Q: Can multiple students share one device?**
> Yes — each student signs in with their own Google account and gets fully isolated data. In guest mode, data is shared per browser profile.

**Q: Why do I sometimes see questions from a different grade?**
> If there aren't enough questions for the selected grade and battery, the app falls back to the full question pool to guarantee a complete session.

---

## 📄 License

Free to use, modify, and distribute for educational purposes.
