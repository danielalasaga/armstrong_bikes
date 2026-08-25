# Bike Manufacturer Sourcing System — Complete Skills Package

## What Was Generated

Four complete agent **Skills** (markdown instruction files) that teach Claude how to source all 35 parts for a multi-model bike production run:

### The Four Skills

1. **`bom-structure.md`** (11 KB, ~350 lines)
   - Defines three bike models: Commuter (60% volume), Mountain (25%), Road (15%)
   - Complete parts catalog: frames, wheels, drivetrain, brakes, handlebars, seats, cables, accessories
   - Criticality matrix: which parts are on the critical path (delay = assembly stops)
   - Substitutability rules: which parts can swap, which cannot
   - MOQ implications: volume discounts at 6K units for frame, etc.
   - Assembly constraints: 45–60 minutes per bike, lead time buffers by part
   - **Specialist used by:** Coordinator (understands what a bike is)

2. **`cost-optimizer.md`** (9.9 KB, ~280 lines)
   - Landed cost formula: unit price + freight + duty + insurance + MOQ surcharge
   - Incoterm handling: FOB vs. CIF vs. DDP (different cost structures)
   - Exchange rates: fixed rates for CNY, EUR, VND, JPY
   - Duty rates: 0–2.5% by part category
   - Complete worked example: Commuter frame costs, wheel costs, BOM aggregation
   - Cost optimization strategies: greedy (cheapest per part) vs. consolidation (volume discounts)
   - Output format: JSON with total BOM cost, cost per bike, tokens used
   - **Specialist used by:** Coordinator (finds lowest-cost sourcing plan)

3. **`lead-time-critical-path.md`** (11 KB, ~330 lines)
   - Critical path algorithm: identify which part arrives latest
   - Assembly start date: when all critical parts are available
   - On-time analysis: assembly deadline vs. actual assembly start
   - Bottleneck identification: which part gates everything
   - Late scenario mitigation: express freight cost, faster supplier cost, split sourcing options
   - Buffer strategy: frame +3 days, wheels +2 days (account for port delays, inspection)
   - Output format: JSON with bottleneck part, on-time? yes/no, days late/early
   - **Specialist used by:** Coordinator (checks if cost plan meets deadline)

4. **`sourcing-recommendation.md`** (15 KB, ~420 lines)
   - Professional memo structure: header, executive summary, analysis, decisions, scenarios
   - Cost analysis section: detailed table of parts, suppliers, prices, landed costs
   - Lead-time analysis section: timeline table, critical path summary, risk assessment
   - Decision rationale section: WHY each supplier was chosen, alternatives rejected
   - Sensitivity scenarios section: what-if (deadline moves, supplier fails, lead time slips)
   - JSON output format: structured for rendering as a branded .docx memo
   - **Specialist used by:** Coordinator (formats final output)

---

## Architecture: How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                     COORDINATOR AGENT                             │
│                     (Claude Instance)                             │
│                                                                   │
│  1. Load bom-structure.md (understand bikes & parts)             │
│  2. Call COST Specialist (find cheapest sourcing plan)           │
│  3. Call LEAD-TIME Specialist (check if plan is on-time)         │
│  4. DECISION: Accept plan or ask cost spec for faster suppliers  │
│  5. Format output using sourcing-recommendation.md               │
└──────────────────────────────────────────────────────────────────┘
       │                                    │
       ▼                                    ▼
┌────────────────────────┐    ┌──────────────────────────────┐
│  COST SPECIALIST       │    │  LEAD-TIME SPECIALIST        │
│                        │    │                              │
│  Input:                │    │  Input:                      │
│  - Parts list          │    │  - Sourcing plan (from cost) │
│  - Suppliers & quotes  │    │  - Lead times by supplier    │
│  - Volume per model    │    │  - Assembly deadline         │
│                        │    │                              │
│  Uses: cost-optim.md   │    │  Uses: lead-time-cp.md       │
│                        │    │                              │
│  Output:               │    │  Output:                     │
│  - Supplier for each   │    │  - Bottleneck part          │
│    part                │    │  - On-time? yes/no          │
│  - Total BOM cost      │    │  - Days late (if applicable)│
│  - Tokens used         │    │  - Fastest alternative cost │
└────────────────────────┘    └──────────────────────────────┘
```

---

## What Needs to Happen Next (You Have to Build This)

### 1. Generate Synthetic Data
```
suppliers.csv or JSON:
- Supplier name, country, lead time by part, prices by part
- MOQ, incoterm, part specialization
- Example: "Shanghai Steel: frame, 28 days, $18 FOB, MOQ 2000"

eval_scenarios.jsonl:
- 12–15 bike sourcing scenarios (one line per scenario)
- Each scenario: bike model, volume, deadline, supplier quotes
- Ground truth: "cheapest plan costs $X, bottleneck is frame, on time? yes"
- Example: RFQ001: Commuter 6,000 units, deadline day 30
  Suppliers: Shanghai (frame 28d), Taiwan (wheels 24d), Vietnam (drivetrain 26d), etc.
  Ground truth: Use Shanghai + Taiwan + Vietnam, total $822,180, ON TIME
```

### 2. Build the Coordinator Agent
```python
The agent that orchestrates everything:

def coordinator_agent(bike_order):
    """
    Input: bike_order = {
        model: "Commuter",
        volume: 6000,
        deadline_day: 30,
        supplier_quotes: [
            {part: "Frame", supplier: "Shanghai", price: 18, ...},
            {part: "Wheels", supplier: "Taiwan", price: 13.5, ...},
            ...
        ]
    }
    
    Process:
    1. Load bom-structure.md → understand parts and criticality
    2. Call Claude with bom-structure.md context:
       "Find the cheapest sourcing plan for Commuter using cost-optimizer.md"
       → returns: supplier picks, total BOM cost
    3. Call Claude with lead-time-critical-path.md context:
       "Check if this plan meets deadline day 30"
       → returns: bottleneck part, on-time yes/no, days late
    4. Decision logic:
       if on_time: use the cost plan
       else: ask cost specialist for cost delta of faster suppliers
    5. Format output:
       Call Claude with sourcing-recommendation.md context to format memo
    6. Return: professional sourcing memo in JSON (renderable as .docx)
    """
```

### 3. Wire It All Together
```
Your 90-minute build in this order:
- 0–15 min: Write the coordinator logic (decision tree)
- 15–45 min: Wire the two specialist calls to Claude (cost + lead-time)
- 45–60 min: Add token counting and logging
- 60–75 min: Test on one eval scenario (verify output format)
- 75–90 min: Demo script + backup recording
```

---

## The Differentiator

Most multi-agent systems have specialists that operate in isolation. Yours **makes a real decision** that resolves a conflict:

**Scenario:** Cost specialist says "Cheapest frame is Shanghai at $17.26, 28 days."
Lead-time specialist says "Deadline is 30 days. Shanghai arrives Day 28. **We're tight.** Fastest frame is Taiwan at $19.50, 18 days."

**Coordinator decides:** "Pay the extra $2.24/unit ($13,440 total) to use Taiwan because we have no buffer. Cost is secondary to hitting the deadline."

**Output memo explains:** "Chose Taiwan frame over cheaper Shanghai alternative because Shanghai's 28-day lead time leaves zero margin for port delays. Taiwan adds $13.4K but guarantees on-time delivery, which is worth the cost given our deadline."

This is **conflict resolution**, not parallel execution. That's what judges will recognize.

---

## Key Insight from the Skills

### BOM Structure
- **Frame is the bottleneck** on 99% of sourcing plans (always the longest lead time)
- **Wheels and drivetrain are secondary** (arrive 2–4 days earlier)
- **Brakes and handlebars are flexible** (can arrive later if needed)
- **Cables and accessories don't matter** (non-critical path)

### Cost Optimizer
- **DDP quotes are best** (supplier pays everything, lowest total cost, no surprises)
- **CIF quotes are good** (freight + insurance included, but duty can vary)
- **FOB quotes need careful calculation** (easy to miss freight, duty, insurance)
- **Volume discounts are real** (at 6,000 units, frame drops from $18 to $16.50)
- **Consolidation with one supplier can save 3–5%** (but adds single-source risk)

### Lead-Time Critical Path
- **Buffer is essential** (frame should have +3 day buffer for port delays)
- **Express freight is expensive** (adds $1.25/unit) but sometimes necessary
- **If supplier is 5+ days late, you're late** (no other part can catch up because frame gates everything)
- **Fastest alternative is always more expensive** but sometimes worth it

### Sourcing Recommendation
- **Be explicit about tradeoffs** (we chose expensive over cheap, here's why)
- **Show scenarios** (what if Shanghai is 5 days late? Cost $7,500 for express)
- **One-paragraph summary at top** (CFO can approve in 30 seconds)
- **Full details in tables** (CFO can drill down if needed)

---

## Demo Script (90 Seconds)

**Slide: Problem statement**
"A bike manufacturer sources 35 parts from 12 suppliers for three models. One supplier running late breaks the assembly line. We need the cheapest sourcing plan that hits the deadline."

**Slide: Sample data**
"Here's one order: 6,000 Commuter bikes, deadline is Day 30. Suppliers quote different currencies, different incoterms, different lead times."

**Live run (40 seconds):**
1. Call coordinator: "Find the best sourcing plan"
2. Cost specialist: "Cheapest plan is $137/bike. Frame from Shanghai ($17.26), wheels from Taiwan ($13.50×2), drivetrain from Vietnam ($44.99)."
3. Lead-time specialist: "Frame arrives Day 28, that's our critical path. Wheels and drivetrain arrive earlier. Assembly starts Day 28, on time ✓."
4. Coordinator: "Accept the cost plan, no faster suppliers needed. Format the memo."

**Slide: Output**
"Professional sourcing memo with parts table, cost breakdown, lead-time analysis, and decision rationale. Cost: $822K. On time. Ready to send to suppliers."

**Close:**
"One working sourcing plan in 90 seconds. The coordinator made a real decision: cost specialist found the cheapest option, lead-time specialist confirmed it's on time, no conflict to resolve. But if the deadline was tighter, you'd see the coordinator override the cost specialist and pick a more expensive (but faster) frame supplier. That's the value: it's not just cost optimization, it's **time-aware cost optimization**."

---

## The Skills Solve This Problem

- **bom-structure.md** → tells you what a bike is, what parts matter
- **cost-optimizer.md** → finds the cheapest sourcing plan for those parts
- **lead-time-critical-path.md** → checks if that plan actually arrives on time
- **sourcing-recommendation.md** → formats the decision as a professional memo

No data files needed for the Skills. No external APIs. Just context for Claude.

---

## Success Metrics

Your system works if it can:

1. ✓ Take a messy set of supplier quotes (different currencies, incoterms, lead times)
2. ✓ Normalize them to landed cost per unit
3. ✓ Identify the critical path (frame is late, everything else is early)
4. ✓ Compare cost (cheapest plan) vs. deadline (on time? yes/no)
5. ✓ Resolve conflicts (if late, what's the cost to pick a faster supplier?)
6. ✓ Output a professional memo that explains the tradeoff

All five skills are already in the box. You just need to wire them together.

---

## Files Included

```
bom-structure.md                 11 KB    ← Bike models, parts, criticality
cost-optimizer.md                 9.9 KB  ← Cost calculation, BOM economics  
lead-time-critical-path.md       11 KB    ← Timeline analysis, bottleneck detect
sourcing-recommendation.md       15 KB    ← Output memo format
SKILLS_README.md                 ~8 KB    ← How the skills work together
```

**Total: ~1,300 lines of detailed instruction** for Claude.

No generated synthetic data yet (you'll create that when you're ready to build the coordinator).

---

## Next: Coordinate or Stand Alone?

**Option 1 (Recommended):** Build a coordinator agent that uses all four skills
- More powerful, makes real decisions
- Resolves cost vs. time conflicts
- Better demo story

**Option 2:** Use skills individually
- Cost specialist alone: "Find cheapest sourcing plan"
- Lead-time specialist alone: "Check if we're on time"
- Output formatter alone: "Format memo"
- Simpler, but less impressive

Pick Option 1. The magic is in the coordinator.

---

**Ready to build?** Start with the coordinator skeleton (decision tree), wire the two specialists, test on one scenario. You've got 90 minutes.

Good luck.
