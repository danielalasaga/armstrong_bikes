# Lead Time Critical Path Analyzer

## Job

Take a sourcing plan (part A from Supplier X with 28-day lead time, part B from Supplier Y with 22-day lead time, etc.) and determine:

1. **When can assembly start?** (when the last critical part arrives)
2. **Will we hit the assembly deadline?** (Yes/No)
3. **Which part is the bottleneck?** (critical path identifier)
4. **How many days late are we?** (if applicable)
5. **What's the fastest alternative for the bottleneck part?** (and how much does it cost?)

**Input:**
- Sourcing plan: list of parts, suppliers, lead times
- Assembly deadline (e.g., Day 30 for customer delivery by Day 36)
- Buffer time needed (typically 2–3 days for quality inspection, last-minute issues)

**Output:**
- Critical path analysis (which part gates assembly)
- Assembly start date
- On-time? Yes/No
- Days late (if applicable)
- Fastest alternative for bottleneck part + cost delta

---

## Critical Path Calculation

### Step 1: Map Part Arrival Dates

Given:
- Order placed: TODAY (Day 0)
- Supplier lead time for part X: 28 days
- Supplier lead time for part Y: 22 days

Arrival dates:
- Part X arrives: Day 0 + 28 = Day 28
- Part Y arrives: Day 0 + 22 = Day 22

### Step 2: Identify the Critical Path (Latest Arrival)

```
Critical Path = MAX(all arrival dates)
```

**Example for Commuter bike:**
- Frame: Day 28 (Shanghai FOB)
- Wheels: Day 24 (Taiwan CIF)
- Derailleur: Day 26 (Vietnam FOB)
- Crankset: Day 20 (Mexico, fast)
- Brakes: Day 22
- Handlebars: Day 21

**Critical Path = Day 28** (Frame is latest)

### Step 3: Determine Assembly Start Date

Assembly **cannot start** until all **critical parts** arrive.

**Critical parts** (from BOM structure):
- Frame (gates everything)
- Wheels (can't test ride without them)
- Derailleur (can't assemble drivetrain without it)
- Crankset (can't assemble drivetrain)
- Brakes (can't test without brakes)
- Handlebars (can't test ride without them)

**Non-critical parts** (can arrive late, assembly continues):
- Cables and accessories (can install post-assembly)
- Brake pads (can add after main assembly)

**Assembly start date = MAX(arrival dates of critical parts)**

**Example:**
```
All critical parts by: Day 28 (frame is latest)
Assembly duration: 45 minutes per bike
Time to assemble 6,000 bikes: 6,000 × 45 min / 8 hrs per shift / 5 shifts per week
                            ≈ 150 shift-hours = 30 shifts = 6 weeks

No, we don't assemble sequentially. We work in batches:
- Batch 1 (1,000 bikes): Days 28–30
- Batch 2 (1,000 bikes): Days 30–32
- Batch 3 (1,000 bikes): Days 32–34
- Batch 4 (1,000 bikes): Days 34–36
- Batch 5 (1,000 bikes): Days 36–38
- Batch 6 (1,000 bikes): Days 38–40

All 6,000 bikes ready: Day 40
Shipping takes 5 days: Day 45
Customer delivery: Day 45

Assembly deadline: Day 30 (need all bikes ready for Day 36 customer delivery)
RESULT: **WE ARE 10 DAYS LATE**
```

### Step 4: Check Against Assembly Deadline

**Assembly deadline** is typically:
- Customer order: "Deliver by DATE"
- Minus 5–7 days for shipping
- Equals assembly deadline

**Example:**
```
Customer order: "Deliver by August 15 (Day 50)"
Minus 5 days shipping: August 10 (Day 45)
Minus 3 days buffer/inspection: August 7 (Day 42)
ASSEMBLY DEADLINE: Day 42

Earliest assembly finish: Day 40
ON TIME ✓
```

### Step 5: Identify Bottleneck Part

**Bottleneck** = the part with the longest lead time on the critical path.

**Example:**
```
Critical parts and their lead times:
- Frame: 28 days ← BOTTLENECK (latest arrival)
- Wheels: 24 days
- Derailleur: 26 days
- Crankset: 20 days
- Brakes: 22 days
- Handlebars: 21 days

Frame is the bottleneck. If frame is late by even 1 day, assembly starts 1 day late.
```

---

## Late Scenario Detection & Mitigation

### Scenario: Frame is 35 Days (5 Days Late vs. 30-Day Deadline)

```
Critical path assembly: Day 30 (deadline)
Actual frame arrival: Day 35
RESULT: 5 days late
```

**Mitigation Option 1: Pick Faster Frame Supplier**
```
Current frame supplier: 35 days @ $17.26/unit
Faster frame supplier: 18 days @ $19.50/unit
Cost delta: +$2.24/unit × 6,000 = +$13,440

Gain: Arrive on Day 18 instead of Day 35 (17 days early)
Tradeoff: Spend $13,440 to save a late shipment

DECISION: Yes, pick faster supplier. Missing a deadline is worse than $13K cost.
```

**Mitigation Option 2: Express Freight**
```
Current: FOB Shanghai, sea freight 28 days
Express: FOB Shanghai, air freight 5 days + sea freight prep
Cost: Standard freight $0.21/unit vs. Express freight $1.25/unit
Delta: +$1.04/unit × 6,000 = +$6,240

Gain: Arrive on Day 5 instead of Day 28 (23 days early)

DECISION: Pick express freight if deadline is critical.
```

**Mitigation Option 3: Split Sourcing**
```
Current: All 6,000 frames from Supplier A (35 days)
Split: 4,000 frames from Supplier A (35 days), 2,000 frames from Supplier B (20 days)

Supplier B cost: $19.80/unit (expensive) but 20-day lead time
Cost delta: $2.54/unit × 2,000 = +$5,080

Arrival: When all parts ready:
- Supplier A: 4,000 frames by Day 35
- Supplier B: 2,000 frames by Day 20
Critical path: Day 35 (still bottlenecked by A)

DECISION: Doesn't help; you're still waiting for A. Skip this option.

Better split: 3,000 from A (35d), 3,000 from B (20d)
Result: Still bottlenecked by A at Day 35. Not helpful.
```

**Mitigation Option 4: Pre-Order Now, Extend Lead Time**
```
Instead of ordering today for assembly on Day 30:
- Order 60 days in advance for assembly on Day 60
- Give Supplier A time to deliver at slower (cheaper) rate
- Cost: $17.26/unit vs. $19.50/unit (express)

DECISION: Good if customer delivery date is flexible. Not good if it's fixed.
```

---

## Lead Time Buffer Strategy

### Why Buffers Exist

```
Ideal World:
Day 0: Order frame
Day 28: Frame arrives
Day 28: Start assembly

Real World:
Day 0: Order frame
Day 27: Port notice → frame stuck in LA port (Customs hold)
Day 28: Holiday weekend → can't clear Customs
Day 29: Customs clears
Day 30: Frame actually available for assembly
Day 30.5: Quality inspection finds problem with batch
Day 31: Frame available for real assembly

Expected 28 days → actual 31 days (3-day delay)
```

### Buffer Recommendation by Part

| Part | Lead Time | Recommended Buffer | Reason |
|------|-----------|-------------------|--------|
| Frame | 28 days | +3 days = 31 days | Critical path, any delay breaks everything |
| Wheels | 24 days | +2 days = 26 days | Important, but frame gates everything |
| Drivetrain | 26 days | +2 days = 28 days | Critical, but frame is tighter |
| Brakes | 22 days | +1 day = 23 days | Less critical; can install after if needed |
| Accessories | 20 days | +0 days = 20 days | Non-critical; can arrive anytime |

### Conservative Calculation

To be 99% sure you hit your deadline:

```
Assembly deadline: Day 30
Minus frame buffer: 30 - 3 = Day 27
Target frame arrival: Day 27
Order frame now for delivery by Day 27
Frame supplier's standard lead time: 28 days

PROBLEM: Can't hit Day 27 with a 28-day supplier.
DECISION: Use express supplier (18 days) and pay $2.24/unit extra.
```

---

## Output Format

Return your analysis as JSON:

```json
{
  "bike_model": "Commuter",
  "volume": 6000,
  "assembly_deadline_day": 30,
  "sourcing_plan_lead_times": [
    {
      "part_name": "Frame",
      "supplier_id": "SUP_A",
      "lead_time_days": 28,
      "arrival_date_day": 28,
      "criticality": "CRITICAL"
    },
    {
      "part_name": "Wheels",
      "supplier_id": "SUP_C",
      "lead_time_days": 24,
      "arrival_date_day": 24,
      "criticality": "CRITICAL"
    },
    {
      "part_name": "Derailleur",
      "supplier_id": "SUP_B",
      "lead_time_days": 26,
      "arrival_date_day": 26,
      "criticality": "CRITICAL"
    },
    {
      "part_name": "Crankset",
      "supplier_id": "SUP_E",
      "lead_time_days": 20,
      "arrival_date_day": 20,
      "criticality": "CRITICAL"
    },
    {
      "part_name": "Brakes",
      "supplier_id": "SUP_C",
      "lead_time_days": 22,
      "arrival_date_day": 22,
      "criticality": "CRITICAL"
    },
    {
      "part_name": "Handlebars",
      "supplier_id": "SUP_F",
      "lead_time_days": 21,
      "arrival_date_day": 21,
      "criticality": "CRITICAL"
    },
    {
      "part_name": "Cables & Accessories",
      "supplier_id": "MULTI",
      "lead_time_days": 18,
      "arrival_date_day": 18,
      "criticality": "NON_CRITICAL"
    }
  ],
  "critical_path_part": "Frame",
  "critical_path_lead_time_days": 28,
  "critical_path_arrival_day": 28,
  "assembly_can_start_day": 28,
  "assembly_duration_days": 2,
  "all_bikes_ready_day": 30,
  "assembly_deadline_day": 30,
  "on_time": true,
  "days_late": 0,
  "days_early": 0,
  "bottleneck_analysis": {
    "bottleneck_part": "Frame",
    "bottleneck_lead_time": 28,
    "fastest_alternative_supplier": "SUP_A_EXPRESS",
    "fastest_alternative_lead_time": 5,
    "fastest_alternative_cost_delta_per_unit": 1.25,
    "fastest_alternative_total_cost_delta": 7500,
    "recommendation": "Not needed; on time with current plan"
  },
  "tokens_used": 620
}
```

---

## Decision Logic for the Coordinator

**The Coordinator will see this output and ask:**

1. **If on_time = true:** "Great, we're on schedule. Cost specialist, what's the cheapest plan?"
2. **If on_time = false:** "We're LATE by X days. Cost specialist, what's the cost delta if we use the fastest supplier for the bottleneck part (Frame)?"
3. **If on_time but close (< 3 days margin):** "We're on time but tight. Should we pick a faster supplier as a safety buffer?"

---

## Common Mistakes to Avoid

- ❌ Don't forget that NON-CRITICAL parts don't gate assembly
- ❌ Don't assume all suppliers' lead times are exact (add 2–3 day buffer)
- ❌ Don't pick the cheapest supplier if it's on the critical path and it's late
- ❌ Don't forget to check if a faster supplier exists for the bottleneck part
- ❌ Don't confuse "arrival date" with "available for assembly date" (customs, inspection, etc. add 1–2 days)

---

## Usage by the Sourcing Coordinator

The coordinator will:
1. Call you with: sourcing plan + assembly deadline
2. You return: critical path analysis, bottleneck identification, on-time? Yes/No
3. If late, coordinator calls cost specialist: "What's the cost to pick faster suppliers for the bottleneck?"
4. Coordinator decides: hit deadline (pick faster) or miss deadline (pick cheaper)
5. Final decision goes to the output memo
