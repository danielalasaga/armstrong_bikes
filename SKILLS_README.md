# Bike Manufacturer Sourcing — Skills Documentation

## What You Have

Four complete Skill files (markdown files) that define how the sourcing agent makes decisions:

### 1. `bom-structure.md` (11 KB)
**The bike encyclopedia** — defines all the parts, models, criticality, and constraints.

**Contains:**
- Three bike models (Commuter, Mountain, Road) with specs
- Complete parts list for all models:
  - Frame (CRITICAL)
  - Wheels front + rear (CRITICAL)
  - Drivetrain: derailleur, chain, crankset, cassette, bottom bracket (CRITICAL)
  - Braking: v-brakes or disc brakes, pads, cables (CRITICAL)
  - Handlebars & stem (CRITICAL)
  - Seat & seatpost (CRITICAL)
  - Cables & accessories (NON-CRITICAL)
- Critical path definition (which parts gate assembly)
- Assembly time per model (45–60 minutes)
- MOQ and pricing implications
- Substitutability rules (which parts can swap, which can't)
- Lead time buffers by part type

**Used by:** Coordinator agent to understand the bike structure and constraints.

---

### 2. `cost-optimizer.md` (9.9 KB)
**The cost calculator** — normalizes quotes and finds the lowest-cost sourcing plan.

**Contains:**
- Landed cost formula:
  - Unit price (convert currency to USD)
  - Freight (based on incoterm: FOB, CIF, DDP, EXW)
  - Import duty (by part type, 0–2.5%)
  - Insurance (0.5% if not included in quote)
  - MOQ surcharge (if volume < MOQ)
- Exchange rates (fixed, Aug 2026)
- Duty rates by part category
- Freight rates (sea, air, land by route/mode)
- Complete worked example (Commuter frame, wheels, drivetrain)
- BOM aggregation (total cost per bike × volume)
- Cost optimization strategies:
  - Option 1: Greedy (cheapest per part)
  - Option 2: Volume consolidation (fewer suppliers, discounts)
  - Option 3: Cost + lead-time balance
- JSON output format (structured, machine-readable)

**Used by:** Coordinator agent to evaluate cost of different sourcing plans.

**Returns:** Lowest-cost sourcing plan, total BOM cost, cost per bike, tokens.

---

### 3. `lead-time-critical-path.md` (11 KB)
**The schedule analyzer** — identifies bottlenecks and determines if you meet the deadline.

**Contains:**
- Critical path calculation:
  - Map part arrival dates (order date + lead time)
  - Identify latest arrival (the bottleneck)
  - Assembly can only start when all critical parts arrive
- Critical path vs. non-critical parts (cables can arrive later)
- Buffer strategy (frame +3 days, wheels +2 days, etc.)
- Late scenario detection:
  - If frame is 35 days and deadline is 30 days, you're 5 days late
  - Mitigation options: express freight, faster supplier, split sourcing, pre-order
- Lead time risks:
  - Port delays
  - Customs holds
  - Quality inspection delays
- JSON output format (bottleneck identification, on-time yes/no, days late/early)

**Used by:** Coordinator agent to check if cost specialist's plan meets the deadline.

**Returns:** Bottleneck part, arrival date, on-time? yes/no, days late/early, fastest alternative cost.

---

### 4. `sourcing-recommendation.md` (15 KB)
**The output template** — formats the final sourcing memo that goes to stakeholders.

**Contains:**
- Memo header (TO/FROM/RE/DATE)
- Executive summary (one paragraph with key decisions)
- Part A: Cost Analysis (30% of memo)
  - Table: part name, supplier, price, incoterm, freight, duty, landed cost, total
  - Narrative explaining cost decisions
- Part B: Lead Time Analysis (40% of memo)
  - Timeline table (part, lead time, arrival date, critical?, margin)
  - Critical path summary (bottleneck identification, assembly schedule, shipping window)
  - Risk assessment for critical path
- Part C: Decision Rationale (20% of memo)
  - Why each supplier was chosen
  - Alternatives considered and rejected
  - Tradeoffs explained
- Part D: Sensitivity Scenarios (10% of memo)
  - What-if scenarios (deadline moves, supplier fails, lead time slips)
  - Cost impact of each scenario
- Footer (approval required, next steps)
- JSON output format (structured for .docx rendering)

**Used by:** Coordinator agent to format the final output.

**Produces:** Professional sourcing memo that looks like a procurement analyst wrote it.

---

## How They Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                    COORDINATOR AGENT                             │
└────────────────┬──────────────────────────┬──────────────────────┘
                 │                          │
        ┌────────▼─────────┐        ┌──────▼──────────┐
        │ COST SPECIALIST  │        │ LEAD-TIME SPEC  │
        │ cost-optimizer.md│        │ lead-time-cp.md │
        └────────┬─────────┘        └──────┬──────────┘
                 │                          │
            Call 1:              Call 1:
            Input: Parts +       Input: Sourcing plan +
            Suppliers + Quotes   Assembly deadline
                 │                          │
            Return: Lowest-     Return: Bottleneck
            cost sourcing plan  part, on-time?, days late
                 │                          │
                 └──────────────┬───────────┘
                                │
                    ┌───────────▼──────────┐
                    │ COORDINATOR LOGIC    │
                    │ (the agent's brain)  │
                    └───────────┬──────────┘
                                │
                    ┌───────────▼──────────────────┐
                    │ DECISION POINT               │
                    │                              │
                    │ Cost plan on time?           │
                    │ YES → use it                 │
                    │ NO → ask cost spec: "what's  │
                    │      the delta for faster    │
                    │      suppliers?"             │
                    └───────────┬──────────────────┘
                                │
                    ┌───────────▼──────────────────┐
                    │ FINAL DECISION               │
                    │                              │
                    │ Pick suppliers for all parts │
                    │ Document tradeoffs           │
                    │ Write justification          │
                    └───────────┬──────────────────┘
                                │
                    ┌───────────▼──────────────────┐
                    │ OUTPUT FORMATTER             │
                    │ sourcing-recommendation.md   │
                    │                              │
                    │ Convert decision to memo     │
                    └───────────┬──────────────────┘
                                │
                    ┌───────────▼──────────────────┐
                    │ FINAL OUTPUT                 │
                    │                              │
                    │ Professional sourcing memo   │
                    │ (ready for approval)         │
                    └──────────────────────────────┘
```

---

## What You Still Need to Build

### The Coordinator Agent
```python
def coordinator(bike_model, volume, assembly_deadline, supplier_quotes):
    
    # 1. Understand the bike
    bom = load_skill("bom-structure.md")
    parts_list = bom[bike_model]
    
    # 2. Call cost specialist
    cost_specialist = call_claude(
        prompt=f"Find the cheapest sourcing plan for {parts_list}",
        context="cost-optimizer.md"
    )
    sourcing_plan = cost_specialist.output  # dict of part -> supplier
    total_cost = cost_specialist.total_bom_cost
    
    # 3. Call lead-time specialist
    lead_time_specialist = call_claude(
        prompt=f"Analyze if {sourcing_plan} meets deadline {assembly_deadline}",
        context="lead-time-critical-path.md"
    )
    
    # 4. DECISION LOGIC
    if lead_time_specialist.on_time:
        # Cost specialist's plan works. Use it.
        final_plan = sourcing_plan
        decision_note = "Cost-optimized plan is on-time; no tradeoff needed."
    else:
        # Cost specialist's plan is late. Ask: what's the cost to get on time?
        days_late = lead_time_specialist.days_late
        bottleneck_part = lead_time_specialist.bottleneck_part
        
        faster_alternatives = call_claude(
            prompt=f"For {bottleneck_part}, get cost delta for {days_late}-day faster suppliers",
            context="cost-optimizer.md"
        )
        
        # Pick fastest alternative (assume coordinator has rule about this)
        if faster_alternatives.cost_delta < total_cost * 0.05:  # <5% cost increase
            # Pick faster supplier, still profitable
            final_plan = update_plan(sourcing_plan, bottleneck_part, faster_alternatives.fastest)
            decision_note = f"Accept +${faster_alternatives.cost_delta} cost to hit deadline"
        else:
            # Too expensive to get on time. Fail gracefully.
            decision_note = f"Cannot meet deadline without {cost_delta}+ cost increase. Consider extending deadline."
    
    # 5. Format output
    memo = call_claude(
        prompt=f"Format this decision as a sourcing memo",
        context="sourcing-recommendation.md"
    )
    
    return memo
```

### The Data Setup
You'll need:
- List of suppliers (name, origin, lead time, prices by part, incoterm, MOQ)
- List of parts for each bike model
- Assembly deadline
- Target volume per model

---

## Testing the Skills

### Test 1: Cost Optimizer
```
Input: Commuter bike, 6,000 units, all suppliers with quotes
Expected: $137.03 per bike, Frame from Shanghai Steel, Wheels from Taiwan, etc.
```

### Test 2: Lead-Time Specialist
```
Input: The cost specialist's plan (sourcing_plan from Test 1) + deadline of Day 30
Expected: "ON TIME ✓, Frame is bottleneck at Day 28, 2-day margin"
```

### Test 3: Coordinator Decision
```
Input: Test 2 says "ON TIME"
Expected: Use cost specialist's plan as-is, no changes needed
```

### Test 4: Coordinator Decision (Late Scenario)
```
Input: Same cost plan but assembly deadline is Day 25 (5 days earlier)
Expected: Lead-time specialist says "5 days late", Coordinator asks cost specialist for faster frame supplier, decides to pay +$7,500 for express freight, outputs memo explaining the tradeoff
```

---

## Demo Flow (90 Seconds)

1. **Problem (20s):** "A bike has 35 parts from 12 suppliers. One late supplier breaks the assembly line. We need the cheapest plan that hits the deadline."
2. **Show data (10s):** Display supplier quotes (messy: different currencies, incoterms, lead times)
3. **Run coordinator (40s):**
   - Cost specialist: "Cheapest plan is $137/bike, frame from Shanghai"
   - Lead-time specialist: "Frame is 28 days, deadline is 30, ON TIME ✓"
   - Coordinator: "Plan accepted. Writing memo."
4. **Show output (20s):** Display formatted memo with parts table, cost breakdown, lead-time analysis, decision rationale
5. **Close (5s):** "One working sourcing plan in 90 seconds. Cost: $822K. On time. Ready to send to suppliers."

---

## Files Included

```
bom-structure.md                 ← Bike models, parts, criticality, assembly
cost-optimizer.md                ← Cost formula, landed cost, BOM economics
lead-time-critical-path.md       ← Timeline analysis, bottleneck detection
sourcing-recommendation.md       ← Output memo format
```

Each file is complete and ready to use as context for Claude. No additional data files needed for the Skills themselves; the coordinator agent will provide the supplier quotes.

---

## Next Steps

1. **Generate synthetic bike data** (suppliers, quotes, expected answers for eval)
2. **Build the coordinator agent** (orchestrates the two specialists)
3. **Test end-to-end** (run on one bike order, verify output)
4. **Demo and iterate** (show to judges, refine based on feedback)

Questions? Read the individual Skill files — each has detailed examples and output formats.
