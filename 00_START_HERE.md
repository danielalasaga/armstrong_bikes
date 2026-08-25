# Sourcing Swarm — Track 03 Hackathon Pack

Everything you need to build and demo the Sourcing Swarm agent in 90 minutes.

## What You Have

### 1. Presentation (7 slides, ready to present)
**`sourcing-swarm-track03.pptx`**
- Track 03 branded, forest green theme
- Slide 1: Title
- Slide 2: The use case (quotes don't line up, cheapest ≠ best, review kills decisions)
- Slide 3: Architecture (coordinator + 2 specialists + 3 Skills)
- Slide 4: The differentiator (specialists disagree, that's intentional)
- Slide 5: Live demo run (watch folder → two specialists → coordinator → .docx)
- Slide 6: Proof (fill in YOUR numbers after your run)
- Slide 7: What it takes to ship (Connect, Constrain, Extend)

**Note:** Slide 6 has blanks. Fill in after your eval run:
- `__%` → your accuracy (e.g., 92%)
- `$0.0_` → cost per decision (e.g., $0.043)
- `~$__` → analyst loaded cost (reference: ~$12 for 0.25 hrs)

### 2. Synthetic Dataset (40 eval RFQs + demo packet)
**Reference tables** (use in your Skills):
- `duty_rates.csv` — import duty by HS code and origin
- `freight_rates.csv` — shipping costs by route and mode
- `incoterm_rules.md` — cost allocation rules (FOB, CIF, DDP, EXW, FCA)
- `fx_rates.csv` — fixed exchange rates (Aug 22, 2026)
- `supplier_master.csv` — 8 suppliers with risk profiles

**Eval set** (ground truth for scoring):
- `eval_dataset.jsonl` — 40 RFQs (one per line), each with 4 supplier quotes
  - 28 aligned (cost & risk agree) — easy cases
  - 9 conflicts (risk should win) — hard cases
  - 3 conflicts (cost should win) — harder cases
- `eval_labels.csv` — same RFQs as readable CSV

**Demo & test**:
- `demo_packet.json` — one real conflict case (RFQ005) ready to run live
- `held_out_test.jsonl` — 2 additional RFQs never seen before

**Composition:**
- ✓ Realistic supplier diversity (China, Vietnam, Taiwan, Mexico, India)
- ✓ Multiple quote formats (different incoterms, currencies, lead times)
- ✓ Real tradeoffs (cost vs. supply chain risk, lead time buffer)
- ✓ Ground truth labels (known-good awards for each RFQ)

### 3. Guides & Checklists
**`SYNTHETIC_DATA_README.md`**
- How to use each reference table in your Skills
- Code pseudocode for landed-cost and supply-risk specialists
- Interpretation guide for the eval set
- Debugging tips

**`HACKATHON_CHECKLIST.md`**
- Tonight prep (Skill files, end-to-end test)
- Minute-by-minute build schedule (0–10, 10–20, ... 75–90)
- Key lines to memorize
- What to cut if you fall behind

## What You Need to Build (You Have 90 Minutes)

### The Three Skill Files
Write these as `.md` files so your agent can reference them:

1. **landed-cost.md** (~100 lines)
   - Takes a supplier quote (price, currency, incoterm, freight mode)
   - Normalizes to USD landed cost per unit using reference tables
   - Returns: ranking of suppliers by cost + tokens used
   - Uses: `duty_rates.csv`, `freight_rates.csv`, `incoterm_rules.md`, `fx_rates.csv`

2. **supply-risk.md** (~80 lines)
   - Scores each supplier on risk (0–100 scale)
   - Flags: China concentration, cert expiry, lead time buffer, on-time history
   - Returns: risk scores + recommendation + tokens used
   - Uses: `supplier_master.csv`, supplier on-time record, cert validity

3. **sourcing-memo.md** (~60 lines)
   - Defines the output format for the branded .docx
   - Sections: summary, cost analysis, risk analysis, coordinator decision, sensitivity table
   - Makes the .docx read like a deliverable, not a script

### The Coordinator Agent
Puts the specialists together:
```
Input: 4 supplier quotes (PDF, email, xlsx, scan)
↓
Specialist 1: Landed-cost specialist (reads quotes → normalizes → returns cost ranking)
Specialist 2: Supply-risk specialist (reads supplier master → returns risk scores)
↓
Coordinator: Compares outputs
  - If cost is obviously better: award to cost specialist's pick
  - If risk outweighs cost savings: split the award or pick risk specialist's choice
  - Write the reasoning into the memo
↓
Output: Branded .docx memo with award + rationale + sensitivity table
```

### Token Measurement
Log tokens per specialist per RFQ, convert to cost per decision:
```
Cost specialist: 850 tokens → $0.0255
Risk specialist: 620 tokens → $0.0186
Coordinator: 400 tokens → $0.0120
Total: $0.0561 per decision

vs. Analyst: ~$12 per decision (0.25 hours @ $48/hr loaded)
Payoff: 214× cheaper
```

This is your slide 6 story.

## The Demo (4 Minutes)

1. **45 seconds — Problem**
   - Show one of the four messy quotes (PDF, email body, scan, xlsx)
   - "Four formats, four incoterms, four currencies. Before anyone can compare them, a senior analyst spends a day normalizing."

2. **90 seconds — Live run**
   - Drop `demo_packet.json` in the watch folder
   - Watch the terminal: cost specialist runs (8.5K tokens), risk specialist runs (6.2K tokens)
   - Coordinator decides: "Cost says supplier A, risk says supplier D. Split 80/20 with a risk premium."
   - Show the output memo on screen (logo, sections, reasoning visible)

3. **60 seconds — The numbers**
   - "Cost per decision: $0.056 tokens. Analyst equivalent: $12. 214× cheaper."
   - "We also logged which specialist burned the most, so we can tell you what to optimize next."

4. **45 seconds — Production roadmap**
   - Connect: "Swap the watch folder for your actual sourcing inbox."
   - Constrain: "Add a human approval gate for awards above $100K."
   - Extend: "Add a third specialist for compliance and cert validity. Same pattern, one more Skill file."

**Total: ~4 minutes. Record a backup run beforehand.**

## Your Build Sequence (Use the Checklist)

| Time | What | Checkpoint |
|------|------|------------|
| 0–10 | Write three Skill files | All prose, no crashes |
| 10–20 | Token wrapper + memory plumbing | Logging works |
| 20–30 | Stubbed specialists end-to-end | Full loop closes |
| 30–50 | Real specialists call Claude | Both specialists run, token counts print |
| 50–60 | Coordinator logic + reasoning | Output memo reads like English |
| 60–75 | Eval set run + numbers | You have accuracy %, cost per decision |
| 75–90 | Demo script + backup recording | Live demo < 2 min, backup ready |

## Key Numbers to Hit

**Slide 6 template:**
- Accuracy: ___% (target: 85%+)
- Cost per decision: $0.0___ (target: < $0.10)
- Analyst equivalent: ~$12 (fixed reference)
- Ratio: 100–200× cheaper (computed)

## If You Finish Early

1. Run sensitivity analysis: re-run decisions at +15% tariff and +2-week lead time slip
2. Add memory: log past awards and retrieval before deciding (shows institutional knowledge)
3. Add a third specialist for compliance (cert validity, financial tier)
4. Build the template `sourcing-memo.md` so it renders real Word docs with logo and formatting

## If You Fall Behind

- **30 min left:** Drop memory and sensitivity. Just specialists + coordinator + evals.
- **20 min left:** Drop supply-risk specialist. Just cost specialist + dummy + coordinator.
- **10 min left:** Drop live demo. Show code + pre-recorded run + the output artifact.

## Files at a Glance

```
sourcing-swarm-track03.pptx           ← Present this (fill in slide 6)
eval_dataset.jsonl                    ← Run your agent on this (40 RFQs)
demo_packet.json                      ← Live demo from this (1 conflict case)
held_out_test.jsonl                   ← Optional: test on this too
duty_rates.csv                        ← Reference: import duty
freight_rates.csv                     ← Reference: shipping cost
incoterm_rules.md                     ← Reference: cost allocation rules
fx_rates.csv                          ← Reference: exchange rates
supplier_master.csv                   ← Reference: supplier risk profiles
eval_labels.csv                       ← Read this to understand ground truth
HACKATHON_CHECKLIST.md                ← Follow this minute by minute
SYNTHETIC_DATA_README.md              ← Deep dive on how to use the data
```

## One More Thing

**Read the problem statement out loud.**

"A buyer sends one RFQ. Four suppliers answer in four formats. Before anyone can compare them, a senior analyst normalizes, and the sourcing manager asks 'but what if tariffs move?' No one re-ran the numbers, so the decision stalls. This demo is that decision in 90 seconds."

That's the truth of the use case. Keep that sentence with you. It's what makes the audience nod.

---

**Start with the checklist. Follow the sequence. You've got this.**

Questions? Read `SYNTHETIC_DATA_README.md` (data reference) or `HACKATHON_CHECKLIST.md` (build sequence).
