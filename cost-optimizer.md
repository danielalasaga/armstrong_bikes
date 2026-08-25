# Cost Optimizer: Landed Cost Calculation & BOM Economics

## Job

Take a list of parts, suppliers' quotes for each part, and find the lowest-cost complete sourcing plan for a given volume and bike model.

**Input:**
- Bike model (Commuter, Mountain, or Road)
- Total volume (e.g., 6,000 Commuter bikes)
- Supplier quotes for each part (price, currency, incoterm, MOQ, lead time)

**Output:**
- Lowest-cost sourcing plan: supplier pick for each part
- Total BOM cost per bike
- Total program cost (volume × per-bike cost)
- Cost vs. next-cheapest alternative (delta)
- Token count

---

## Cost Calculation Formula

For each part and supplier combination:

```
Landed Cost Per Unit = [
  (Unit Price in USD) +
  (Freight Cost Per Unit) +
  (Import Duty) +
  (Insurance) +
  (MOQ Surcharge, if applicable)
] × (Quantity Adjustment Factor)
```

### Step 1: Convert Unit Price to USD

**If quote is in foreign currency:**
```
USD Price = Quote Price × Exchange Rate
```

Exchange rates (use fixed rates, don't call live API):
- CNY: 1 CNY = $0.138 USD
- EUR: 1 EUR = $1.085 USD
- VND: 1 VND = $0.0000394 USD
- JPY: 1 JPY = $0.00667 USD

---

### Step 2: Normalize Freight Based on Incoterm

**If supplier quotes FOB (Free on Board):**
- Supplier's unit price does NOT include freight
- YOU pay freight from origin port to Los Angeles
- Look up freight cost for origin port → LA
- Example: Shanghai to LA by sea = $0.21 per unit

**If supplier quotes CIF (Cost, Insurance, Freight):**
- Supplier's unit price INCLUDES ocean freight and insurance
- Freight is already baked in
- Add $0 for freight
- Insurance is already included; see note below

**If supplier quotes DDP (Delivered Duty Paid):**
- Supplier's unit price includes EVERYTHING (freight, duty, insurance)
- You pay nothing extra except the invoice
- Add $0 for additional freight or duty

**If supplier quotes EXW (Ex Works):**
- Supplier's unit price is factory price only
- YOU pay for everything: freight, duty, insurance
- Add full freight cost + duty (see Step 3)

**Standard freight rates (sea, Shanghai/Vietnam/Taiwan to LA):**
- FOB quote: +$0.18–$0.24 per unit (sea, 20–25 days)
- Air freight (if available): +$1.20–$1.40 per unit (4–5 days, rare for parts)

---

### Step 3: Calculate Import Duty

**If incoterm is DDP:** Skip this (duty already paid by supplier).

**If incoterm is FOB, CIF, or EXW:**
```
Duty = (USD Price + Freight Cost) × Duty Rate
```

Duty rates by part category (use HS codes if available):
- **Frames:** 2.5% (iron/steel) or 0% (carbon)
- **Wheels:** 2.5% (metal frames) or 0% (alloy)
- **Drivetrain (gears, chains, cranks):** 0% (most mechanical parts are duty-free)
- **Brakes:** 2.6% (measuring instruments/machinery)
- **Handlebars/seat posts:** 2.5% (iron/steel articles)
- **Cables & accessories:** 0–2.5%

**Conservative rule:** If unsure, assume 2.5% duty.

---

### Step 4: Add Insurance

**If incoterm is CIF or DDP:** Skip this (insurance already included).

**If incoterm is FOB, EXW, or FCA:**
```
Insurance = (USD Price + Freight Cost + Duty) × 0.5%
```

Insurance covers loss/damage during transit. Standard rate is 0.5% of insurable value.

---

### Step 5: Apply MOQ Surcharge (If Volume < MOQ)

**If you want to order less than the supplier's MOQ:**
```
Quantity Adjustment Factor = (MOQ / Your Quantity) × 1.15
```

**Example:**
- You want 1,000 wheels
- Supplier C's MOQ is 5,000 wheels
- You can't order 1,000 alone
- Option A: Order 5,000 (hit MOQ) → no surcharge, lower cost per unit
- Option B: Order 1,000 from Supplier A (higher MOQ) → pay surcharge

**MOQ Surcharge Logic:**
- If you hit the MOQ, apply no surcharge (you get the good price)
- If you're below the MOQ and this is a "small order," add 15% surcharge (handling, setup costs)
- If multiple suppliers' MOQs are all above your volume, pick the supplier with best per-unit cost (even with surcharge)

---

### Step 6: Quantity Adjustment Factor for Volume Discounts

**If supplier offers price breaks at higher volumes:**

```
Price Break = [
  (Volume 1: 1,000–2,999 units @ $X/unit) OR
  (Volume 2: 3,000–4,999 units @ $X-10%/unit) OR
  (Volume 3: 5,000+ units @ $X-20%/unit)
]
```

**Decision rule:**
- For Commuter frame at 6,000 units: Supplier A's price is $18/unit at MOQ 2,000, but $16.50/unit at MOQ 6,000. Hit the MOQ, pay $16.50.
- For Commuter wheel at 6,000 bikes = 12,000 wheel units: Supplier C's MOQ is 5,000 wheels @ $13.50/unit. You hit the MOQ; apply the discount.

---

## Complete Landed Cost Example

### Part: Commuter Frame (6,000 units needed)

**Supplier A Quote:**
- Unit Price: $18 USD
- Incoterm: FOB
- Origin: Shanghai
- MOQ: 2,000 @ $18/unit, 6,000 @ $16.50/unit
- Lead time: 28 days

**Calculation:**
1. USD Price: $18 (already in USD)
2. Freight: FOB Shanghai → LA = $0.21/unit
3. Duty: (18 + 0.21) × 2.5% = $0.455
4. Insurance: (18 + 0.21 + 0.455) × 0.5% = $0.092
5. Volume discount: At 6,000 units, hit the $16.50 price point

**Landed Cost Per Frame:**
```
$16.50 (volume-adjusted unit price)
+ $0.21 (freight)
+ $0.455 (duty)
+ $0.092 (insurance)
= $17.257 per frame
```

**Total Program Cost:** $17.257 × 6,000 = **$103,542**

---

### Part: Commuter Wheels (6,000 bikes = 12,000 wheel units)

**Supplier C Quote:**
- Unit Price: $13.50 USD
- Incoterm: CIF
- Origin: Taiwan
- MOQ: 5,000 wheels
- Lead time: 22 days

**Calculation:**
1. USD Price: $13.50
2. Freight: $0 (CIF = freight included)
3. Duty: $0 (CIF includes duty on most wheels)
4. Insurance: $0 (CIF includes insurance)
5. Volume discount: At 12,000 units, well above MOQ; no surcharge

**Landed Cost Per Wheel:**
```
$13.50 (CIF = all-in price)
= $13.50 per wheel
```

**Total Program Cost (2 wheels per bike):** $13.50 × 2 × 6,000 = **$162,000**

---

## BOM Cost Aggregation

For a complete Commuter bike (6,000 units):

| Part | Supplier | Units/Bike | Cost/Unit | Total Cost |
|------|----------|-----------|-----------|-----------|
| Frame | A | 1 | $17.26 | $103,542 |
| Wheels (2x) | C | 2 | $13.50 | $162,000 |
| Derailleur | B | 1 | $20.15 | $120,900 |
| Chain | D | 1 | $8.42 | $50,520 |
| Crankset | E | 1 | $24.80 | $148,800 |
| Brakes | C | 1 | $31.50 | $189,000 |
| Handlebars | F | 1 | $6.25 | $37,500 |
| Seat & post | G | 1 | $9.90 | $59,400 |
| Cables & acc. | Multiple | - | $4.75 | $28,500 |
| **BOM TOTAL** | - | - | **$137.03** | **$900,162** |

---

## Cost Optimization Strategy

### Option 1: Lowest Cost Per Unit (Greedy)
```
For each part, pick the supplier with lowest landed cost.
Total BOM: $137.03/bike
```

### Option 2: Volume Consolidation (Fewer Suppliers)
```
If you pick 3 suppliers for all parts, you might get volume discounts.
Example: Supplier A makes frames + wheels + brakes
         Supplier B makes drivetrain
         Supplier C makes accessories
Total BOM: $135.50/bike (saves $9,180)
Tradeoff: Less flexibility; if one supplier fails, more parts are late.
```

### Option 3: Balance Cost + Lead Time
```
Pick cheapest suppliers for non-critical parts (wheels, accessories).
Pick fastest suppliers for critical parts (frame, derailleur).
Total BOM: $138.50/bike
Tradeoff: Slightly more expensive, but frame and derailleur both arrive on time.
```

---

## Output Format

Return your cost analysis as JSON:

```json
{
  "bike_model": "Commuter",
  "volume": 6000,
  "sourcing_plan": [
    {
      "part_name": "Frame",
      "supplier_id": "SUP_A",
      "supplier_name": "Shanghai Steel",
      "unit_price_quote": 18.00,
      "currency": "USD",
      "incoterm": "FOB",
      "freight_cost": 0.21,
      "duty_rate": 0.025,
      "insurance_rate": 0.005,
      "landed_cost_per_unit": 17.26,
      "volume": 6000,
      "total_part_cost": 103542,
      "lead_time_days": 28,
      "notes": "Volume discount at 6,000 units"
    },
    {
      "part_name": "Wheels (per wheel)",
      "supplier_id": "SUP_C",
      "supplier_name": "Taiwan Wheel Co",
      "unit_price_quote": 13.50,
      "currency": "USD",
      "incoterm": "CIF",
      "freight_cost": 0.00,
      "duty_rate": 0.00,
      "insurance_rate": 0.00,
      "landed_cost_per_unit": 13.50,
      "volume": 12000,
      "total_part_cost": 162000,
      "lead_time_days": 22,
      "notes": "CIF includes all costs; 2 wheels per bike"
    }
  ],
  "total_bom_cost_per_bike": 137.03,
  "total_program_cost": 900162,
  "cost_vs_next_alternative": -5200,
  "tokens_used": 850
}
```

---

## Decision Rules

1. **Always prefer DDP quotes** (lowest total cost, no surprises)
2. **CIF quotes are next best** (freight & insurance baked in, still clean)
3. **FOB quotes need careful freight calculation** (easy to underestimate)
4. **EXW quotes are highest-risk** (you pay for everything; easy to miss costs)
5. **If MOQ > your volume, pick the supplier with best per-unit cost** (even if you can't hit exact MOQ, you're charged upcharge anyway)
6. **Volume discounts are real** (if you need 6,000 and the breakpoint is 5,000, hit it)
7. **Currency fluctuation:** Use fixed rates (don't call live API in a demo)

---

## What NOT to Do

- ❌ Don't add freight to a CIF quote (it's already there)
- ❌ Don't forget duty on FOB quotes (it's a real cost the buyer pays)
- ❌ Don't ignore MOQ surcharges (small orders cost more)
- ❌ Don't pick a supplier 3% cheaper if it's 15 days late (lead-time specialist overrides)
- ❌ Don't double-count insurance (CIF includes it; FOB needs separate insurance line)

---

## Usage by the Sourcing Coordinator

The coordinator will:
1. Call you with a parts list and supplier quotes
2. You return the lowest-cost sourcing plan
3. The coordinator then calls the Lead-Time specialist: "Can we hit the deadline with this plan?"
4. If lead-time specialist says "No, frame is 35 days and we need 30," the coordinator asks you: "What's the cost delta if we use the next-fastest frame supplier?"
5. You return: "Fastest frame is $3 more per unit" 
6. Coordinator decides: Use the faster frame supplier despite the cost.

Your job: be accurate on cost. The lead-time specialist will override you if needed.
