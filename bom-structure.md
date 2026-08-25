# BOM Structure: Complete Parts Lists by Bike Model

## Bike Models Offered

### Commuter
- Target market: urban daily commute (10–20 miles)
- Volume: 60% of total production
- Assembly time: 45 minutes once all parts arrive
- Target weight: < 28 lbs

### Mountain
- Target market: trail riding, weekend recreation
- Volume: 25% of total production
- Assembly time: 55 minutes (more complex drivetrain)
- Target weight: < 32 lbs

### Road
- Target market: distance cycling, racing
- Volume: 15% of total production
- Assembly time: 60 minutes (precision alignment critical)
- Target weight: < 22 lbs

---

## Complete Parts List (All Models)

### Frame
| Model | Part # | Description | Weight | Criticality | Substitutable | Lead Time Importance |
|-------|--------|-------------|--------|-------------|----------------|-----------------------|
| Commuter | FR-001 | Aluminum frame 19" | 3.2 lbs | **CRITICAL** | No | HIGHEST — all assembly waits |
| Mountain | FR-002 | Steel frame 19" (reinforced) | 4.1 lbs | **CRITICAL** | No | HIGHEST — all assembly waits |
| Road | FR-003 | Carbon frame 19" | 2.1 lbs | **CRITICAL** | No | HIGHEST — all assembly waits |

**Notes:** Frame is the first component to arrive; every other part waits if frame is late. No substitution possible (SKU-specific geometry and paint).

### Wheels (Front + Rear, 2 units per bike)
| Model | Part # | Description | Weight/unit | Criticality | Substitutable | Notes |
|-------|--------|-------------|-------------|-------------|----------------|-------|
| Commuter | WHL-001 | 26" alloy wheel | 2.1 lbs | CRITICAL | Limited | Can substitute 27.5" if unavailable (requires frame mod) |
| Mountain | WHL-002 | 27.5" alloy wheel (spoked) | 2.3 lbs | CRITICAL | Limited | Can use 26" emergency (loses performance) |
| Road | WHL-003 | 700c carbon wheel | 1.4 lbs | CRITICAL | No | Specific aero profile; no substitute |

**Notes:** Wheels are on critical path (assembly can't proceed without them). Front and rear are separate parts.

### Drivetrain Components
| Part # | Description | Models | Criticality | Substitutable | MOQ Implication |
|--------|-------------|--------|-------------|----------------|----|
| DR-001 | Derailleur (Shimano 7-speed) | Commuter, Mountain | **CRITICAL** | No | Single part; can't break into smaller MOQ |
| DR-002 | Derailleur (Shimano 21-speed) | Road | **CRITICAL** | No | Different supplier, often different MOQ |
| DR-003 | Chain (standard) | All models | CRITICAL | Limited | Generic part; many suppliers |
| DR-004 | Crankset (3-piece) | All models | CRITICAL | Limited | Some interchangeability between models |
| DR-005 | Cassette/sprocket set | All models | CRITICAL | Limited | Model-specific gear ratios |
| DR-006 | Bottom bracket | All models | CRITICAL | Limited | Some standardization across models |

**Notes:** Derailleur is model-specific; cannot substitute Road derailleur into Commuter. Chains and cranksets have more supplier flexibility.

### Braking System
| Part # | Description | Models | Criticality | Substitutable | Notes |
|--------|-------------|--------|-------------|----------------|----|
| BR-001 | V-brake set (front + rear) | Commuter, Mountain | Critical | Limited | Can use mechanical disc brake if unavailable (assembly changes) |
| BR-002 | Hydraulic disc brake set | Road | Critical | No | Premium brake; no substitute for Road model |
| BR-003 | Brake pads | All models | Non-critical | Yes | Generic; many suppliers; can arrive later |
| BR-004 | Brake cables & housings | All models | Non-critical | Yes | Can substitute; often in stock |

**Notes:** Braking system is on critical path (assembly can't test ride without brakes). Pads and cables can arrive after primary assembly if needed.

### Handlebars & Stem
| Part # | Description | Models | Criticality | Substitutable | Notes |
|--------|-------------|--------|-------------|----------------|----|
| HB-001 | Flat handlebar (700mm) | Commuter | Critical | Limited | Width varies; some interchangeability |
| HB-002 | Drop handlebar (420mm) | Road | Critical | No | Road-specific geometry |
| HB-003 | Riser handlebar (760mm) | Mountain | Critical | No | Mountain-specific rise and sweep |
| HB-004 | Stem (80mm, 120mm variants) | All models | Critical | Limited | Size varies; some interchangeability |

**Notes:** Handlebar assembly is on critical path. Stem must match frame and handlebar diameter.

### Seat & Seatpost
| Part # | Description | Models | Criticality | Substitutable | Notes |
|--------|-------------|--------|-------------|----------------|----|
| ST-001 | Padded saddle (gel) | Commuter | Critical | Yes | Generic saddle; can substitute comfort vs. sport |
| ST-002 | Road saddle (narrow) | Road | Critical | Yes | Narrow saddle; can substitute if ergonomic equivalent |
| ST-003 | Mountain saddle (reinforced) | Mountain | Critical | Yes | Durable saddle; can substitute |
| ST-004 | Seatpost (27.2mm, 30.9mm variants) | All models | Critical | Limited | Must match frame seat-tube diameter |

**Notes:** Seat assembly is on critical path. Seatpost diameter is frame-specific but saddle itself has flexibility.

### Cables & Accessories (Non-Critical)
| Part # | Description | Models | Criticality | Substitutable | Lead Time Implication |
|--------|-------------|--------|-------------|----------------|----|
| CB-001 | Shift cables (2x) | All models | Non-critical | Yes | Can arrive up to 1 week late |
| CB-002 | Brake cable housing | All models | Non-critical | Yes | Generic part; many suppliers |
| CB-003 | Grips/bar tape | All models | Non-critical | Yes | Easy substitution; doesn't delay assembly |
| CB-004 | Pedals (platform, clip-in variants) | All models | Non-critical | Yes | Easy to swap; doesn't delay assembly |
| AC-001 | Reflectors & safety lights | All models | Non-critical | Yes | Can be installed post-assembly if needed |
| AC-002 | Bell & fenders | Commuter | Non-critical | Yes | Optional accessories; don't delay core assembly |

**Notes:** These parts can arrive later without stopping assembly line. Can buffer 1–2 weeks late without impact.

---

## Critical Path Definition

### For All Models: Arrival Sequence

1. **Day 0–10:** Frame arrives (longest lead-time item, gates everything)
2. **Day 0–12:** Wheels arrive (gates assembly start)
3. **Day 0–14:** Drivetrain (derailleur, crankset, chain) arrives
4. **Day 0–16:** Braking system arrives
5. **Day 0–18:** Handlebars, stem, seat, seatpost arrive
6. **Day 0–20:** Cables and accessories (can be late; non-critical)

### Assembly Can Begin When:
- Frame ✓
- Wheels ✓
- Derailleur ✓
- Crankset ✓
- Brakes ✓
- Handlebars ✓

If any of these is missing, assembly is blocked.

### Assembly Deadline Impact
- **Target assembly start:** Day 20 (all critical parts arrived)
- **Assembly duration:** 45–60 minutes per bike
- **Bike ready to ship:** Day 21
- **Shipping lead time:** 5–7 days
- **Customer delivery window:** Day 26–28

**Rule:** Frame and wheels are the tightest bottlenecks. If either is late by 1 day, the entire bike shipment is late by 1 day.

---

## Sourcing Constraints by Model

### Commuter (Volume: 6,000 bikes)
- Frame: Only Supplier A makes our geometry
- Wheels: Suppliers A, B, C (choose cheapest)
- Drivetrain: Suppliers B or C for derailleur; generic suppliers for chain/crankset
- Braking: Suppliers A, C, D
- Accessories: 4+ suppliers for each

### Mountain (Volume: 2,500 bikes)
- Frame: Only Supplier B makes the reinforced spec
- Wheels: Suppliers B, C (A discontinued this size)
- Drivetrain: Suppliers A, C (B doesn't make 21-speed)
- Braking: Suppliers A, D
- Accessories: 3+ suppliers for each

### Road (Volume: 1,500 bikes)
- Frame: Only Supplier C makes carbon frame
- Wheels: Only Supplier A makes the aero 700c wheel
- Drivetrain: Only Supplier D makes the 21-speed road derailleur
- Braking: Supplier B (hydraulic disc only)
- Accessories: 2–3 suppliers (tight tolerance)

---

## MOQ and Pricing Implications

### Frame (Commuter)
- Supplier A: MOQ 2,000 @ $18/unit
- Supplier A: MOQ 6,000 @ $16.50/unit (5% discount)
- **Decision:** If you buy 6,000, save $9,000 total. But if you buy 2,000 (hold quantity option), costs more per unit.

### Wheels (Commuter)
- Supplier A: MOQ 1,000 @ $15/unit
- Supplier B: MOQ 3,000 @ $14/unit (less volume than A)
- Supplier C: MOQ 5,000 @ $13.50/unit (cheapest but high MOQ)
- **Decision:** Buying from C saves $1,500 total if you hit 5,000 wheels (10,000 wheel units for 5,000 bikes). But if you only need 6,000 wheels, B is cheaper per unit.

### Derailleur (Commuter, 7-speed)
- Supplier B: MOQ 1,000 @ $22/unit
- Supplier C: MOQ 2,000 @ $20/unit (cheaper at higher volume)
- **Decision:** At 6,000 bikes, both MOQs are easy. Pick by lead time, not MOQ.

---

## Substitutability Rules

### Can Substitute:
- Commuter wheels 26" ↔ 27.5" (affects fit, not ride)
- Generic chain (multiple suppliers equivalent)
- Generic crankset (multiple suppliers equivalent)
- Brake pads & cables (non-critical path)
- Saddles (comfort vs. performance trade-off, not assembly)

### Cannot Substitute:
- Frame (SKU-specific geometry and paint)
- Road derailleur (different gearing than Commuter/Mountain)
- Road 700c wheels (cannot fit on Commuter/Mountain frame)
- Carbon frame (cannot substitute aluminum)

---

## Lead Time Buffers

- **Frame:** +3 days buffer (longest item, gates everything)
- **Wheels:** +2 days buffer
- **Drivetrain critical:** +2 days buffer (derailleur, crankset)
- **Brakes:** +1 day buffer
- **Accessories:** +0 days (can arrive after assembly)

### Why Buffers?
- Port delays, customs clearance, quality inspection hold
- Any supplier 2+ days late triggers line-stop

---

## Usage by the Sourcing Agent

When analyzing a sourcing plan:

1. **Read the frame supplier's lead time.** This is your critical path anchor.
2. **Check wheels supplier's lead time.** Must arrive within 2 days of frame.
3. **Check all drivetrain components' lead times.** Any derailleur late blocks assembly.
4. **Check brakes.** Any 3+ days late = line stop.
5. **Ignore cables and accessories.** They don't gate assembly.

**Decision rule:** If frame is 28 days and assembly deadline is 30 days, you have 2 days margin. You can wait for cheaper suppliers on wheels/drivetrain, but frame MUST hit the 28-day window.
