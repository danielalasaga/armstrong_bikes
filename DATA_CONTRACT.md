# Data Contract — Armstrong Bikes Sourcing API

All requests and responses use `application/json`. The streaming endpoint uses `text/event-stream`.
All amounts are in **USD**. All dates are **ISO 8601**. Day numbers are integers relative to order placement (Day 0).

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/rfq` | Submit a sourcing request; returns SSE stream |
| `GET` | `/api/v1/rfq/{rfq_id}` | Retrieve a completed RFQ result |
| `POST` | `/api/v1/rfq/{rfq_id}/qa` | Ask a question about a completed memo |
| `GET` | `/api/v1/suppliers` | List suppliers in the reference database |
| `GET` | `/api/v1/health` | Health check |

---

## Shared Types

### `SupplierQuote`

```json
{
  "part_name": "Frame",
  "supplier_id": "SUP_A",
  "unit_price": 18.00,
  "currency": "USD",
  "incoterm": "FOB",
  "lead_time_days": 28,
  "moq": 2000
}
```

| Field | Type | Required | Values / Notes |
|---|---|---|---|
| `part_name` | string | Yes | Any part name matching BOM structure (e.g. `"Frame"`, `"Wheels"`, `"Derailleur"`) |
| `supplier_id` | string | Yes | Caller-defined identifier |
| `unit_price` | float | Yes | Price per unit in the stated currency |
| `currency` | string | No | ISO 4217; default `"USD"` |
| `incoterm` | enum | Yes | `"FOB"` `"CIF"` `"DDP"` `"EXW"` `"FCA"` |
| `lead_time_days` | int | Yes | Days from order placement to delivery at destination |
| `moq` | int | No | Minimum order quantity; default `1` |

---

### `PartCostLine`

One row in the cost analysis table.

```json
{
  "part_name": "Frame",
  "supplier_id": "SUP_A",
  "supplier_name": "Shanghai Steel Co",
  "unit_price_quote": 18.00,
  "currency": "USD",
  "incoterm": "FOB",
  "freight_cost": 0.21,
  "duty_rate": 0.025,
  "insurance_rate": 0.005,
  "landed_cost_per_unit": 17.26,
  "volume": 6000,
  "total_part_cost": 103542.00,
  "lead_time_days": 28,
  "notes": "Volume discount applied at 6,000 units"
}
```

---

### `CostAnalysis`

```json
{
  "bike_model": "Commuter",
  "volume": 6000,
  "sourcing_plan": [ /* array of PartCostLine */ ],
  "total_bom_cost_per_bike": 137.03,
  "total_program_cost": 822180.00,
  "cost_vs_next_alternative": -5200.00,
  "tokens_used": 1100
}
```

---

### `PartLeadTimeLine`

```json
{
  "part_name": "Frame",
  "supplier_id": "SUP_A",
  "lead_time_days": 28,
  "arrival_date_day": 28,
  "criticality": "CRITICAL"
}
```

`criticality`: `"CRITICAL"` | `"NON_CRITICAL"`

---

### `BottleneckAnalysis`

```json
{
  "bottleneck_part": "Frame",
  "bottleneck_lead_time": 28,
  "fastest_alternative_supplier": "SUP_B",
  "fastest_alternative_lead_time": 18,
  "fastest_alternative_cost_delta_per_unit": 2.24,
  "fastest_alternative_total_cost_delta": 13440.00,
  "recommendation": "Not needed; on time with current plan"
}
```

Fields marked nullable will be `null` when no faster alternative exists.

---

### `LeadTimeAnalysis`

```json
{
  "bike_model": "Commuter",
  "volume": 6000,
  "assembly_deadline_day": 30,
  "sourcing_plan_lead_times": [ /* array of PartLeadTimeLine */ ],
  "critical_path_part": "Frame",
  "critical_path_arrival_day": 28,
  "assembly_can_start_day": 28,
  "assembly_duration_days": 2,
  "all_bikes_ready_day": 30,
  "on_time": true,
  "days_late": 0,
  "days_early": 2,
  "bottleneck_analysis": { /* BottleneckAnalysis */ },
  "tokens_used": 850
}
```

---

### `CoordinatorDecision`

```json
{
  "decision": "accept",
  "bottleneck_part": null,
  "cost_delta_per_unit": null,
  "total_cost_delta": null,
  "reasoning": "Cost-optimised plan is on time with 2 day(s) margin. No trade-off needed."
}
```

| `decision` value | Meaning |
|---|---|
| `"accept"` | Cost plan is on time with ≥3 day margin; accepted as-is |
| `"accept_with_warning"` | On time but <3 day margin; watch the bottleneck part |
| `"swap_bottleneck"` | Plan is late; coordinator switched the bottleneck part to a faster supplier |
| `"deadline_at_risk"` | Plan is late and no affordable faster supplier exists |

---

### `MemoOutput`

```json
{
  "json_memo": {
    "header": { "to": "...", "from": "...", "re": "...", "date": "..." },
    "executive_summary": "...",
    "cost_analysis": { /* structured cost table */ },
    "lead_time_analysis": { /* structured timeline */ },
    "decision_rationale": "...",
    "sensitivity_scenarios": [ /* array */ ]
  },
  "markdown": "# Sourcing Recommendation Memo\n\n..."
}
```

`json_memo` follows the structure defined in `sourcing-recommendation.md`.
`markdown` is the full memo as a Markdown string, ready for `marked.parse()`.

---

### `CompletedRFQ`

```json
{
  "rfq_id": "RFQ-005",
  "status": "complete",
  "bike_model": "Commuter",
  "volume": 6000,
  "cost_analysis": { /* CostAnalysis */ },
  "lead_time_analysis": { /* LeadTimeAnalysis */ },
  "coordinator_decision": { /* CoordinatorDecision */ },
  "memo": { /* MemoOutput */ },
  "tokens_used_total": 2180,
  "cost_per_decision_usd": 0.056,
  "completed_at": "2026-08-25T14:32:00Z",
  "error": null
}
```

`status`: `"complete"` | `"error"`. When `"error"`, `error` contains the failure message; all analysis fields may be `null`.

---

## `POST /api/v1/rfq`

**Request** — `application/json`

```json
{
  "rfq_id": "RFQ-005",
  "bike_model": "Commuter",
  "volume": 6000,
  "assembly_deadline_day": 30,
  "optimization_strategy": "greedy",
  "supplier_quotes": [
    {
      "part_name": "Frame",
      "supplier_id": "SUP_A",
      "unit_price": 18.00,
      "currency": "USD",
      "incoterm": "FOB",
      "lead_time_days": 28,
      "moq": 2000
    },
    {
      "part_name": "Wheels",
      "supplier_id": "SUP_C",
      "unit_price": 13.50,
      "currency": "USD",
      "incoterm": "CIF",
      "lead_time_days": 22,
      "moq": 5000
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `rfq_id` | string | No | Auto-generated UUID if omitted |
| `bike_model` | enum | Yes | `"Commuter"` `"Mountain"` `"Road"` |
| `volume` | int | Yes | Must be > 0 |
| `assembly_deadline_day` | int | Yes | Must be > 0 |
| `optimization_strategy` | enum | No | `"greedy"` (default) `"consolidation"` `"balanced"` |
| `supplier_quotes` | array | Yes | At least 1 quote; must cover the Frame part |

**Response** — `text/event-stream`

One SSE event per line, each formatted as:
```
data: {JSON}\n\n
```

Terminal message: `data: [DONE]\n\n`

### SSE Events (in order)

#### `rfq_started`
Emitted immediately after validation passes.

```json
{
  "event": "rfq_started",
  "rfq_id": "RFQ-005",
  "payload": {
    "bike_model": "Commuter",
    "volume": 6000,
    "assembly_deadline_day": 30,
    "quote_count": 2
  }
}
```

#### `cost_analysis_complete`
Emitted when the Cost Specialist (Haiku 4.5) finishes.

```json
{
  "event": "cost_analysis_complete",
  "rfq_id": "RFQ-005",
  "payload": { /* CostAnalysis */ }
}
```

#### `lead_time_analysis_complete`
Emitted when the Lead-Time Specialist (Haiku 4.5) finishes.

```json
{
  "event": "lead_time_analysis_complete",
  "rfq_id": "RFQ-005",
  "payload": { /* LeadTimeAnalysis */ }
}
```

#### `coordinator_decision`
Emitted after the coordinator applies the decision tree (pure Python, no LLM call).
If `decision` is `"swap_bottleneck"`, a second Cost Specialist call runs before the formatter.

```json
{
  "event": "coordinator_decision",
  "rfq_id": "RFQ-005",
  "payload": { /* CoordinatorDecision */ }
}
```

#### `memo_complete`
Emitted when the Output Formatter (Sonnet 4.6) finishes. This is the final event before `[DONE]`.

```json
{
  "event": "memo_complete",
  "rfq_id": "RFQ-005",
  "payload": { /* MemoOutput */ }
}
```

#### `error`
Emitted if any stage fails. The stream ends after this event.

```json
{
  "event": "error",
  "rfq_id": "RFQ-005",
  "payload": {
    "stage": "cost_specialist",
    "message": "Failed to parse JSON from model response"
  }
}
```

`stage` values: `"cost_specialist"` `"lead_time_specialist"` `"cost_specialist_swap"` `"output_formatter"` `"stream"`

---

## `GET /api/v1/rfq/{rfq_id}`

Returns the completed RFQ persisted in memory after the stream finishes.

**Response** — `CompletedRFQ` (see above)

**Errors:**

```json
{ "detail": "RFQ not found" }
```
HTTP 404 — `rfq_id` not in memory (stream not yet complete or server restarted).

---

## `POST /api/v1/rfq/{rfq_id}/qa`

Ask a follow-up question about a completed sourcing memo.
The Q&A agent (Sonnet 4.6) loads all four skill files plus the completed memo as context.

**Request**

```json
{
  "question": "Why was the frame supplier chosen over the Taiwan alternative?"
}
```

**Response**

```json
{
  "rfq_id": "RFQ-005",
  "question": "Why was the frame supplier chosen over the Taiwan alternative?",
  "answer": "## Frame Supplier Selection\n\nShanghai Steel was selected because...",
  "tokens_used": 310
}
```

`answer` is Markdown-formatted text, ready for `marked.parse()`.

**Errors:**

```json
{ "detail": "RFQ not found or not yet complete" }
```
HTTP 404 — RFQ hasn't completed streaming yet.

---

## `GET /api/v1/suppliers`

Returns all suppliers currently loaded in the in-memory reference database.

**Response**

```json
[
  {
    "supplier_id": "SUP_A",
    "name": "Shanghai Steel Co",
    "country": "CN",
    "parts": ["Frame"],
    "lead_time_days": 28,
    "default_incoterm": "FOB",
    "moq": 2000,
    "currency": "USD",
    "risk_tier": 2
  }
]
```

Returns `[]` if `data/suppliers.json` is empty.

---

## `GET /api/v1/health`

```json
{
  "status": "ok",
  "reference_data_loaded": true,
  "skills_loaded": ["bom", "cost", "lead_time", "recommendation"]
}
```

---

## Error Format

All non-streaming errors follow FastAPI's standard format:

```json
{
  "detail": "Human-readable error message"
}
```

Validation errors (HTTP 422):

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "bike_model"],
      "msg": "Field required"
    }
  ]
}
```

---

## Frontend Consumption Notes

- **POST-SSE**: `EventSource` only supports `GET`. Use `fetch()` with `response.body.getReader()` + `TextDecoder` to consume the SSE stream from a `POST`.
- **Event parsing**: Each line starting with `data: ` contains a JSON string. Strip the prefix, parse with `JSON.parse()`, check the `event` field, then use `payload`.
- **Terminal signal**: Stop reading when a line equals `data: [DONE]`.
- **Markdown rendering**: Both `memo.markdown` (from `memo_complete`) and `answer` (from Q&A) are Markdown strings — pass through `marked.parse()` before inserting into the DOM.

---

## Agent Model Assignments

| Agent | Model | Rationale |
|---|---|---|
| Cost Specialist | `claude-haiku-4-5-20251001` | Fast structured JSON; math-heavy |
| Lead-Time Specialist | `claude-haiku-4-5-20251001` | Fast structured JSON; algorithmic |
| Output Formatter | `claude-sonnet-4-6` | Polished prose + structured memo JSON |
| Q&A Agent | `claude-sonnet-4-6` | Nuanced multi-document reasoning |
| Coordinator decision | Pure Python | Deterministic; no LLM needed |
