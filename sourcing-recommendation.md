# Sourcing Recommendation Memo Format

## Purpose

This Skill defines the structure and format of the final sourcing recommendation that gets delivered to the customer (or internal stakeholder). The coordinator agent uses this format to present the complete sourcing plan for a bike production run.

The memo should read like a professional sourcing recommendation from a procurement analyst, not like raw agent output.

---

## Memo Structure

### HEADER SECTION

```
SOURCING RECOMMENDATION MEMO

TO:       [Customer/Internal Stakeholder]
FROM:     [Your Company Sourcing Team]
DATE:     [Today's Date]
RE:       [Bike Model] Production Run — [Volume] Units
          Target Assembly Date: [Day X]
          Delivery Deadline: [Day Y]
```

---

### EXECUTIVE SUMMARY (150 words max)

One-paragraph summary of the sourcing plan:

**Template:**
```
This memo recommends a sourcing plan for [Bike Model] production 
that achieves [Total Program Cost] total BOM cost and delivers all 
parts on schedule for assembly start by [Date]. 

Key decisions:
- Use [Supplier A] for Frame (cost: $X, lead time: Y days)
- Use [Supplier B] for Drivetrain (cost: $X, lead time: Y days)
- Use [Supplier C] for Wheels & Brakes (cost: $X, lead time: Y days) [consolidation for volume discount]

All critical parts arrive by Day [X]; assembly can begin Day [X]; 
[Volume] bikes ready for shipment Day [X], meeting delivery deadline.

Total Program Cost: $[Total]
Cost per Bike: $[Per Unit]
```

**Example (Commuter, 6,000 bikes):**
```
This memo recommends sourcing 6,000 Commuter bikes at a total 
program cost of $822,180 ($137.03 per bike). All critical parts 
arrive by Day 28; assembly begins Day 29; all bikes ready for 
shipment Day 31, meeting the August 15 delivery deadline with 
a 2-week buffer.

Key decisions:
- Frame from Shanghai Steel (28 days, $17.26)
- Wheels from Taiwan Wheel Co (24 days, $13.50 per wheel)
- Drivetrain from Vietnam Supplier (26 days, $24.15)

Consolidating with Taiwan Wheel Co for wheels AND brakes saves 
$8,200 vs. sourcing brakes separately, while maintaining schedule.
```

---

### PART A: COST ANALYSIS (30% of memo)

**Section Title:** Sourcing Plan & Landed Cost Breakdown

**Table Format:**

| Part Name | Supplier | Unit Price | Currency | Incoterm | Freight | Duty | Landed Cost/Unit | Volume | Total Part Cost | Notes |
|-----------|----------|-----------|----------|----------|---------|------|------------------|--------|-----------------|-------|
| Frame | Shanghai Steel | $18.00 | USD | FOB | +$0.21 | +$0.46 | $18.67 | 6,000 | $112,020 | Volume discount 6K+ |
| Wheels (per) | Taiwan Wheel | $13.50 | USD | CIF | — | — | $13.50 | 12,000 | $162,000 | 2 wheels/bike |
| Derailleur | Vietnam Drivetrain | $20.15 | USD | FOB | +$0.18 | +$0.51 | $20.84 | 6,000 | $125,040 | Lead time: 26d |
| Crankset | Mexico Mfg | $24.80 | USD | DDP | — | — | $24.80 | 6,000 | $148,800 | Fast (20d) |
| Brakes | Taiwan Wheel | $31.50 | USD | CIF | — | — | $31.50 | 6,000 | $189,000 | Consolidation discount |
| Handlebars | US Supplier | $6.25 | USD | DDP | — | — | $6.25 | 6,000 | $37,500 | Domestic, fast |
| Seat & Seatpost | Mexico Mfg | $9.90 | USD | DDP | — | — | $9.90 | 6,000 | $59,400 | Consolidated |
| Cables & Accessories | Multiple | $4.75 | USD | FOB/CIF | +$0.10 | +$0.12 | $4.97 | 6,000 | $29,820 | Multiple suppliers |
| **BOM TOTAL** | - | - | - | - | - | - | **$137.03** | **6,000** | **$822,180** | - |

**Narrative (below table):**

Explanation of key cost drivers and sourcing decisions:

```
FRAME: Sourcing from Shanghai Steel at $18.00 FOB because they are 
the only supplier qualified for our Commuter geometry. At 6,000 unit 
volume, we hit their price break and pay $16.50 instead of $18.00 
per unit, saving $9,000 total. Freight is standard sea freight from 
Shanghai to Los Angeles ($0.21/unit). Import duty is 2.5% on the 
landed value. Total landed cost: $17.26/unit.

WHEELS: Taiwan Wheel Co offers CIF pricing at $13.50/wheel, meaning 
freight and insurance are included in their quote. No additional costs. 
This is cheaper than our second choice (Supplier A at $15/wheel FOB), 
even after adding freight. 2 wheels per bike = 12,000 wheels = $162,000.

DERAILLEUR & DRIVETRAIN: Vietnam Supplier offers 26-day lead time 
and is $0.50/unit cheaper than alternatives. See lead-time section 
below — this supplier is TIGHT on the critical path, so we verify 
they can meet the Day 28 deadline.

CONSOLIDATION WITH TAIWAN WHEEL CO: Taiwan also makes brakes. By 
consolidating wheels + brakes with one supplier, we get a 3% volume 
discount on the brake order ($31.50 vs $32.50 at other suppliers), 
saving $6,000. This is worth the slight risk of single-sourcing.
```

---

### PART B: LEAD TIME ANALYSIS (40% of memo)

**Section Title:** Assembly Schedule & Critical Path Analysis

**Timeline Table:**

| Part | Supplier | Lead Time (days) | Arrival Date | Critical? | Buffer | Margin |
|------|----------|-----------------|--------------|-----------|--------|--------|
| Frame | Shanghai Steel | 28 | Day 28 | YES | +3 recommended | 0 days |
| Wheels | Taiwan Wheel | 24 | Day 24 | YES | +2 recommended | 4 days early |
| Derailleur | Vietnam | 26 | Day 26 | YES | +2 recommended | 2 days early |
| Crankset | Mexico | 20 | Day 20 | YES | +1 recommended | 8 days early |
| Brakes | Taiwan Wheel | 24 | Day 24 | YES | +1 recommended | 4 days early |
| Handlebars | US | 18 | Day 18 | YES | +0 recommended | 10 days early |
| Cables | Multiple | 16 | Day 16 | NO | — | Non-critical |

**Critical Path Summary:**

```
BOTTLENECK PART: Frame (Shanghai Steel)
Lead Time: 28 days
Arrival Date: Day 28
Assembly Start Date: Day 28

All critical parts (frame, wheels, drivetrain, brakes, handlebars) 
must arrive before assembly can begin. Frame is the latest, arriving 
Day 28.

ASSEMBLY TIMELINE:
- Day 28–30: Assemble Batch 1 (1,000 bikes)
- Day 30–31: Assemble Batch 2 (1,000 bikes)  [can start before Batch 1 finishes]
- Day 31: All 6,000 bikes assembled
- Day 31–35: Quality inspection, packaging, palletizing
- Day 36: Ready to ship

DELIVERY DEADLINE: August 15 (Day 50)
Shipping Time: 5 days (Day 36–40)
Customer Delivery: Day 40

RESULT: ON TIME ✓ (with 10-day buffer)
```

**Risk Assessment for Critical Path:**

```
Frame is on the critical path. If Shanghai Steel is even 1 day late, 
the entire assembly schedule slips 1 day.

Mitigation:
- Taiwan Wheel Co (backup supplier) can deliver frames in 35 days 
  (5 days slower) but at the same cost. If Shanghai misses, we have 
  no backup.
- RECOMMENDATION: Accept this risk because we have a 10-day buffer. 
  If Shanghai is 1–5 days late, we still hit the August 15 deadline.
- If Shanghai was 10+ days late, we would pay for express shipment 
  (see cost impact below).

Next-Tightest Part: Derailleur (26 days, 2-day margin)
- If Vietnam Supplier is 2 days late, assembly starts on Day 30 
  instead of Day 28 (still OK; still on time).
```

---

### PART C: SOURCING DECISION RATIONALE (20% of memo)

**Section Title:** Key Sourcing Decisions & Tradeoffs

Explain WHY each decision was made, not just WHAT was decided:

```
1. FRAME SOURCING (Shanghai Steel)

Rationale: Shanghai Steel is the only qualified supplier for our 
Commuter geometry. No alternatives. Cost: $17.26/unit landed.

Alternative Considered: Express shipping from Shanghai (5-day lead time).
Tradeoff: +$1.25/unit = +$7,500 total cost vs. current plan.
Decision: NOT USED. We have 10-day buffer, so standard shipping is sufficient.

2. WHEEL + BRAKE CONSOLIDATION (Taiwan Wheel Co)

Rationale: Taiwan Wheel Co makes both wheels AND brakes. Consolidating 
saves 3% on brakes ($6,000), and wheels are already coming from Taiwan 
(matching origin port = cheaper freight for the combined order).

Alternative Considered: Wheels from Taiwan, Brakes from Supplier D.
Tradeoff: +$6,000 cost but slightly more supply chain diversification.
Decision: CONSOLIDATE. The $6,000 savings plus simplified logistics justify 
single-sourcing wheels + brakes with one supplier.

3. DOMESTIC HANDLEBARS (US Supplier)

Rationale: Domestic handlebars have 18-day lead time (short) and DDP pricing 
($6.25). International suppliers are 21–24 days. Since handlebars are 
critical path and we're tight, using a fast domestic supplier adds safety.

Alternative Considered: Taiwan Handlebar Supplier at $6.10/unit, 24-day lead time.
Tradeoff: -$0.15/unit saved = -$900 total, but ADDS 6 days to critical path.
Decision: REJECT. Not worth the schedule risk.

4. MEXICAN CRANKSET (Mexico Mfg)

Rationale: Mexico manufacturer is 20 days (fastest available), DDP pricing, 
and USMCA tariff advantage (0% duty vs. 2.5% from China/Vietnam). Total 
savings: $5,200 vs. Vietnam alternative.

Alternative Considered: Vietnam Supplier at $24.10, 22 days.
Tradeoff: -$0.70/unit = -$4,200 total savings, but 2 days slower.
Decision: CHOOSE MEXICO. Faster AND cheaper due to tariff advantage.
```

---

### PART D: COST VS. TIMELINE TRADEOFF SENSITIVITY (10% of memo)

**Section Title:** What-If Scenarios

Show what happens if the deadline changes or if Shanghai is late:

```
SCENARIO 1: Assembly Deadline Moves to Day 25 (5 days earlier)

Problem: Frame arrives Day 28 (3 days late).
Solution: Use Shanghai Express (5-day lead time).
Cost Impact: +$1.25/unit × 6,000 = +$7,500
New Total BOM Cost: $829,680

SCENARIO 2: Shanghai Steel Fails (unexpected quality hold)

Problem: No frame available until Day 35 (backup supplier).
Solution: Activate Backup Supplier: Taiwan Wheel Co can make frames 
         (different geometry, but workable).
Cost Impact: +$2.10/unit × 6,000 = +$12,600
Schedule Impact: Backup supplier is 35 days (same as Shanghai, not helpful).
Alternative: Pay for express from Taiwan = +$1.80/unit × 6,000 = +$10,800.
Recommendation: Use Taiwan backup + express freight = +$10,800, saves 1 day.

SCENARIO 3: What if Vietnam Derailleur supplier is 5 days late?

Current: Derailleur arrives Day 26 (2-day margin before assembly start Day 28).
Late: Derailleur arrives Day 31 (3 days after assembly start).
Impact: Assembly starts Day 31 instead of Day 28 (3-day slip).
Solution: Use Faster Supplier (Taiwan) at 18 days, +$0.80/unit.
Cost Impact: +$4,800
Recommendation: Keep Vietnam supplier (we have 10-day total buffer). If this 
              becomes a pattern, switch suppliers mid-year.
```

---

## FOOTER SECTION

```
APPROVAL & NEXT STEPS

This plan is ready for:
1. Finance approval (total cost: $822,180)
2. Purchasing team action (place orders immediately)
3. Supplier communication (confirm lead times)
4. Quality team notification (Taiwan Wheel Co consolidation requires 
   joint inspection protocol)

Questions? Contact: [Your Sourcing Contact]
Plan Valid Through: [Date, typically 30 days]
```

---

## Using This Format in the Agent

**The Coordinator Agent will:**

1. Receive cost specialist output (all parts + costs)
2. Receive lead-time specialist output (all parts + lead times)
3. Compare: Does cost specialist's plan meet the deadline?
   - If YES: Use the cost specialist's plan as-is
   - If NO: Ask cost specialist for cost delta of alternatives
4. Fill in this memo template with the final decisions
5. Output the formatted memo as JSON (for .docx rendering)

**Example Coordinator Logic:**

```
Cost specialist says: Commuter BOM at $137.03/bike, Frame from Shanghai
Lead-time specialist says: Frame arrives Day 28, assembly deadline Day 30, ON TIME ✓
Coordinator decision: Accept cost specialist's plan

Write recommendation memo:
- Executive Summary: "All parts on time, $137.03/bike"
- Cost Analysis: [Full cost table]
- Lead Time Analysis: "Frame is bottleneck, Day 28 arrival, 2-day margin"
- Decisions: "Shanghai Steel for frame, Taiwan Wheel consolidation"
- Scenarios: "If Shanghai is 5+ days late, cost $7,500 for express"
```

---

## Output JSON Format

The memo is rendered as JSON so the agent can include it in the final output:

```json
{
  "memo_type": "SOURCING_RECOMMENDATION",
  "bike_model": "Commuter",
  "volume": 6000,
  "total_program_cost": 822180,
  "cost_per_bike": 137.03,
  "assembly_deadline_day": 30,
  "assembly_start_day": 28,
  "bottleneck_part": "Frame",
  "on_time": true,
  "days_margin": 10,
  "executive_summary": "...",
  "cost_analysis_table": [...],
  "lead_time_analysis": {...},
  "key_decisions": [
    {
      "decision": "Shanghai Steel for Frame",
      "rationale": "Only qualified supplier, volume discount at 6K units",
      "cost": 112020,
      "lead_time_days": 28,
      "alternative_rejected": "Express shipping (5-day lead time, +$7,500)"
    },
    {
      "decision": "Taiwan Wheel Co consolidation (wheels + brakes)",
      "rationale": "$6,000 savings from volume discount, shared origin port",
      "cost": 351000,
      "lead_time_days": 24,
      "alternative_rejected": "Separate brakes supplier (+$6,000 cost)"
    }
  ],
  "sensitivity_scenarios": [
    {
      "scenario": "Shanghai 5 days late",
      "impact": "Assembly 3 days late",
      "mitigation_cost": 7500,
      "recommendation": "Accept risk (10-day buffer exists)"
    }
  ],
  "approval_required": ["Finance", "Purchasing", "Supplier Management"]
}
```

---

## Style Guide

- **Tone:** Professional, analytical, no jargon overload
- **Audience:** Procurement director, finance (CFO), operations (assembly manager)
- **Level of Detail:** Enough for a CFO to approve the spend; enough for ops to execute the plan
- **Decisiveness:** Show that you've made real tradeoffs, not just optimized one variable
- **Honesty:** If there's a risk (Frame is tight on critical path), say it plainly and explain mitigation

**Example GOOD decision write-up:**
```
We chose Shanghai Steel at $17.26 per unit because they are the only 
qualified supplier for our geometry. There are no alternatives. The 
28-day lead time is tight against our 30-day deadline, but we have a 
10-day overall buffer due to fast component sourcing elsewhere. If 
Shanghai is more than 10 days late (which is unlikely given their 
98% on-time record), we have a fallback: pay $1.25/unit extra for 
express freight.
```

**Example BAD decision write-up:**
```
We recommend Shanghai Steel because they are the cheapest and fastest.
```
(Too vague, doesn't explain tradeoffs, no contingency plan)

---

## Remember

This memo is YOUR recommendation to management. It should read like you've done the analysis, made the calls, and are confident in the plan. Use it to build credibility with the sourcing team and the assembly manager who will execute it.
