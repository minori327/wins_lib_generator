# Wins Library System - Phase 8: Feedback / Signal Loop

This document describes Phase 8 of the Wins Library System: the Feedback / Signal Loop.

---

## Overview

Phase 8 captures, normalizes, and evaluates signals generated **after** Phase 7 publishing events, and produces structured feedback that **MAY influence future Phase 5 decisions**.

### Key Responsibilities

- ✅ **Signal Collection**: Collect post-publish signals (usage, engagement, feedback)
- ✅ **Normalization**: Normalize signals into structured Signal objects
- ✅ **Aggregation**: Aggregate signals over time windows
- ✅ **Feedback Generation**: Produce feedback summaries and recommendations
- ✅ **Read-Only Interface**: Provide evidence inputs for Phase 5 (future runs only)

### What Phase 8 Does NOT Do

- ❌ Modify existing SuccessStory content
- ❌ Modify Phase 6 outputs
- ❌ Modify Phase 7 publish records
- ❌ Automatically change Phase 5 scoring or decisions
- ❌ Retroactively alter past approvals
- ❌ Leak feedback directly into rendering or publishing

---

## Architecture

### Components

1. **Signal Models** ([models/signal.py](../models/signal.py))
   - `Signal`: Base model for all signal types
   - `EngagementSignal`: Views, clicks, downloads
   - `FeedbackSignal`: Ratings, comments, sentiment
   - `UsageSignal`: Access patterns, contexts
   - `OutcomeSignal`: Business impact (revenue, deals)
   - `AggregatedSignal`: Time-windowed aggregations
   - `FeedbackReport`: Summary with insights and recommendations

2. **Signal Ingestion Agent** ([agents/signal_ingestion_agent.py](../agents/signal_ingestion_agent.py))
   - Collects signals from various sources
   - Normalizes raw data into structured Signal objects
   - Supports JSON/JSONL batch ingestion

3. **Signal Aggregation** ([workflow/signal_aggregation.py](../workflow/signal_aggregation.py))
   - Aggregates signals over time windows
   - Computes metrics (averages, totals, distributions)
   - Generates insights and recommendations
   - Creates feedback reports

4. **Signal Storage** ([workflow/signal_storage.py](../workflow/signal_storage.py))
   - `SignalStore`: JSONL storage for raw signals (immutable)
   - `AggregatedSignalStore`: JSON storage for aggregations
   - `FeedbackReportStore`: JSON storage for reports

5. **Phase 5 Interface** ([workflow/phase5_feedback_interface.py](../workflow/phase5_feedback_interface.py))
   - Read-only access to signal data
   - Query methods for Phase 5 agents
   - Returns evidence, not decisions

---

## Signal Types

### 1. Engagement Signals

Track how users interact with published content.

**Metrics:**
- `views`: Number of views
- `clicks`: Number of clicks
- `downloads`: Number of downloads
- `time_spent_seconds`: Average time on page
- `unique_visitors`: Unique visitor count

**Sources:** Website analytics, CMS analytics, tracking tools

**Example:**
```python
from models.signal import EngagementSignal
from agents.signal_ingestion_agent import ingest_engagement_signal

signal = ingest_engagement_signal(
    artifact_id="pub-20260201153045-a1b2c3d4",
    artifact_type="marketing_output",
    source=SignalSource.WEBSITE,
    raw_data={
        "views": 1250,
        "clicks": 87,
        "downloads": 23,
        "time_spent_seconds": 245,
        "unique_visitors": 890
    }
)
```

### 2. Feedback Signals

Collect direct user feedback.

**Metrics:**
- `rating`: Numeric rating (1-5 scale)
- `sentiment`: Sentiment category (positive/neutral/negative/mixed)
- `comment`: Short comment
- `feedback_text`: Longer feedback text

**Sources:** Surveys, comments, reactions, reviews

**Example:**
```python
from models.signal import FeedbackSignal, FeedbackSentiment
from agents.signal_ingestion_agent import ingest_feedback_signal

signal = ingest_feedback_signal(
    artifact_id="pub-20260201153045-a1b2c3d4",
    artifact_type="executive_output",
    source=SignalSource.SURVEY,
    raw_data={
        "rating": 5,
        "sentiment": "positive",
        "comment": "Very helpful for sales calls",
        "feedback_text": "This story helped me close a deal..."
    }
)
```

### 3. Usage Signals

Track how and where content is used.

**Metrics:**
- `access_count`: Number of times accessed
- `last_accessed_at`: Last access timestamp
- `used_in_contexts`: Contexts where used (e.g., ["sales_call", "presentation"])
- `referrers`: Referrer sources

**Sources:** Access logs, usage tracking, CRM

**Example:**
```python
from models.signal import UsageSignal
from agents.signal_ingestion_agent import ingest_usage_signal

signal = ingest_usage_signal(
    artifact_id="pub-20260201153045-a1b2c3d4",
    artifact_type="obsidian_note",
    source=SignalSource.MANUAL,
    raw_data={
        "access_count": 15,
        "last_accessed_at": "2026-02-01T10:30:00Z",
        "used_in_contexts": ["sales_call", "customer_meeting", "presentation"],
        "referrers": ["sales_team", "marketing"]
    }
)
```

### 4. Outcome Signals

Track business impact attributed to stories.

**Metrics:**
- `outcome_type`: Type of outcome (e.g., "deal_closed", "renewal", "expansion")
- `outcome_description`: Description of the outcome
- `attributed_revenue`: Revenue attributed to this story
- `attributed_deals`: Number of deals attributed
- `customer_reference`: Whether customer became a reference

**Sources:** CRM, manual reports, deal tracking

**Example:**
```python
from models.signal import OutcomeSignal
from agents.signal_ingestion_agent import ingest_outcome_signal

signal = ingest_outcome_signal(
    artifact_id="pub-20260201153045-a1b2c3d4",
    artifact_type="marketing_output",
    source=SignalSource.MANUAL,
    raw_data={
        "outcome_type": "deal_closed",
        "outcome_description": "Customer cited this success story as key factor in signing",
        "attributed_revenue": 125000.00,
        "attributed_deals": 1,
        "customer_reference": True
    }
)
```

---

## Signal Flow

### 1. Signal Ingestion

Signals are ingested from various sources:

```python
from agents.signal_ingestion_agent import ingest_signal_from_dict
from workflow.signal_storage import SignalStore

# Ingest from dictionary (manual or API)
raw_signal_data = {
    "signal_type": "engagement",
    "artifact_id": "pub-20260201153045-a1b2c3d4",
    "artifact_type": "marketing_output",
    "source": "website",
    "views": 1250,
    "clicks": 87,
    "downloads": 23
}

signal = ingest_signal_from_dict(raw_signal_data)

# Store signal
store = SignalStore()
store.save_signal(signal)
```

### 2. Batch Ingestion from File

Ingest multiple signals from JSON or JSONL file:

```python
from agents.signal_ingestion_agent import ingest_signals_from_file
from workflow.signal_storage import SignalStore

# Load signals from file
signals = ingest_signals_from_file(Path("signals/website_analytics.jsonl"))

# Store all signals
store = SignalStore()
store.save_signals(signals)
```

**File Format (JSONL):**
```jsonl
{"signal_type":"engagement","artifact_id":"pub-xxx","artifact_type":"marketing_output","source":"website","views":1250,"clicks":87}
{"signal_type":"feedback","artifact_id":"pub-xxx","artifact_type":"marketing_output","source":"survey","rating":5,"sentiment":"positive"}
```

### 3. Signal Aggregation

Aggregate signals over a time window:

```python
from workflow.signal_aggregation import aggregate_signals_for_artifact
from workflow.signal_storage import SignalStore

# Load signals
store = SignalStore()
signals = store.load_signals_for_artifact("pub-20260201153045-a1b2c3d4")

# Aggregate
aggregation = aggregate_signals_for_artifact(
    artifact_id="pub-20260201153045-a1b2c3d4",
    artifact_type="marketing_output",
    signals=signals,
    window_start="2026-01-01T00:00:00Z",
    window_end="2026-01-31T23:59:59Z"
)

print(aggregation.metrics)
# {
#   "engagement": {"total_views": 5000, "engagement_rate": 0.069},
#   "feedback": {"avg_rating": 4.5, "rating_count": 12}
# }
```

### 4. Feedback Report Generation

Generate feedback report with insights and recommendations:

```python
from workflow.signal_aggregation import generate_feedback_report_for_artifact

report = generate_feedback_report_for_artifact(
    artifact_id="pub-20260201153045-a1b2c3d4",
    artifact_type="marketing_output",
    signals=signals,
    window_start="2026-01-01T00:00:00Z",
    window_end="2026-01-31T23:59:59Z"
)

print(report.insights)
# ["High engagement with 5000 total views", "Positive feedback with average rating 4.5/5"]

print(report.recommendations)
# [FeedbackRecommendation(recommendation_type="boost", confidence="high", reason="...")]
```

---

## Phase 5 Integration

### Read-Only Interface

Phase 5 can access signal data through the read-only `FeedbackInterface`:

```python
from workflow.phase5_feedback_interface import get_feedback_interface

# Get interface
feedback = get_feedback_interface()

# Get signal summary for a story
summary = feedback.get_signal_summary_for_story("win-2026-01-US-1234abcd")

print(summary)
# {
#   "story_id": "win-2026-01-US-1234abcd",
#   "total_signals": 45,
#   "signal_type_breakdown": {"engagement": 12, "feedback": 8, "usage": 15, "outcome": 10},
#   "latest_metrics": {
#     "engagement": {"total_views": 5000, "engagement_rate": 0.069},
#     "feedback": {"avg_rating": 4.5, "rating_count": 12}
#   },
#   "recommendation_types": ["boost"],
#   "has_data": True
# }
```

### Using Feedback in Phase 5

Phase 5 agents may use signal data as **evidence** in future decisions:

```python
from agents.success_evaluation_agent import evaluate_success_story
from workflow.phase5_feedback_interface import get_feedback_interface

# Get feedback evidence
feedback = get_feedback_interface()
summary = feedback.get_signal_summary_for_story(story.id)

# Use as evidence in evaluation (advisory only)
if summary["has_data"]:
    metrics = summary["latest_metrics"]

    # Check if story is high-performing
    if "feedback" in metrics and metrics["feedback"]["avg_rating"] >= 4.5:
        # This is EVIDENCE, not an automatic score change
        evidence.append(f"High user rating: {metrics['feedback']['avg_rating']}/5")

    # Check attributed revenue
    if "outcome" in metrics and metrics["outcome"]["total_attributed_revenue"] > 0:
        revenue = metrics["outcome"]["total_attributed_revenue"]
        evidence.append(f"Attributed revenue: ${revenue:,.0f}")

    # Pass evidence to evaluation (human still decides)
    result = evaluate_success_story(story, additional_evidence=evidence)
```

**Critical:** Phase 8 provides evidence, Phase 5 makes decisions. Feedback is **advisory**, not authoritative.

---

## Recommendations

### Recommendation Types

Phase 8 generates the following recommendation types:

| Type | Confidence | Trigger | Suggested Action |
|------|------------|---------|------------------|
| **boost** | High/medium | High rating, high revenue | Feature more prominently |
| **deprecate** | Low | Low usage, low views | Consider archiving |
| **investigate** | High/medium | Low rating, negative feedback | Review and update content |
| **update** | Medium | Mixed feedback | Update content or format |

### Example Recommendations

```python
recommendations = [
    FeedbackRecommendation(
        recommendation_type="boost",
        confidence="high",
        reason="High average rating (4.7/5) from 15 ratings",
        evidence=["sig-xxx", "sig-yyy", "sig-zzz"],
        suggested_action="Consider featuring this story more prominently"
    ),
    FeedbackRecommendation(
        recommendation_type="investigate",
        confidence="high",
        reason="More negative feedback (3) than positive (1)",
        evidence=["sig-aaa", "sig-bbb"],
        suggested_action="Review feedback and consider content updates"
    )
]
```

---

## Storage

### Raw Signals

Stored in JSONL format (one signal per line):

```
vault/signals/
├── pub-20260201153045-a1b2c3d4.signals.jsonl
├── pub-20260201153122-b2c3d4e5.signals.jsonl
└── pub-20260201153200-c3d4e5f6.signals.jsonl
```

**Format:**
```jsonl
{"signal_id":"sig-20260201...","signal_type":"engagement","source":"website","artifact_id":"pub-xxx","collected_at":"2026-02-01T15:30:45Z","raw_payload":{"views":1250}}
{"signal_id":"sig-20260201...","signal_type":"feedback","source":"survey","artifact_id":"pub-xxx","collected_at":"2026-02-01T16:00:00Z","raw_payload":{"rating":5}}
```

### Aggregated Signals

Stored in JSON format:

```
vault/signals/aggregations/
├── agg-20260201160000.json
├── agg-20260201170000.json
└── agg-20260201180000.json
```

### Feedback Reports

Stored in JSON format:

```
vault/reports/
├── report-pub-xxx-2026-01-01-2026-01-31.json
├── report-pub-yyy-2026-01-01-2026-01-31.json
└── report-collection-10-2026-01-01.json
```

---

## Configuration

Signal collection configuration can be added to `config/publish_config.yaml` or a new `config/signal_config.yaml`:

```yaml
# Signal Collection Configuration
signal_collection:
  enabled: true

  # Collection intervals
  collection_interval_hours: 24  # How often to collect signals

  # Aggregation windows
  default_aggregation_days: 30  # Default time window for aggregations

  # Storage paths
  signal_storage_dir: "vault/signals"
  aggregation_storage_dir: "vault/signals/aggregations"
  report_storage_dir: "vault/reports"

  # Signal sources
  sources:
    website_analytics:
      enabled: true
      type: "api"
      endpoint: "https://analytics.example.com/api"
      collect_metrics: ["views", "clicks", "downloads"]

    slack:
      enabled: true
      type: "webhook"
      collect_reactions: true
      collect_replies: true

    manual:
      enabled: true
      allowed_types: ["feedback", "usage", "outcome"]

  # Aggregation methods
  aggregation:
    method_version: "1.0"
    include_raw_signal_references: true
```

---

## Usage Examples

### Example 1: Manual Signal Entry

```python
from agents.signal_ingestion_agent import create_manual_signal
from workflow.signal_storage import SignalStore

# Create manual feedback signal
signal = create_manual_signal(
    artifact_id="pub-20260201153045-a1b2c3d4",
    artifact_type="executive_output",
    signal_type=SignalType.FEEDBACK,
    data={
        "rating": 5,
        "sentiment": "positive",
        "comment": "Very useful for executive briefings",
        "feedback_text": "This story helped me..."
    }
)

# Store signal
store = SignalStore()
store.save_signal(signal)
```

### Example 2: Generate Monthly Report

```python
from workflow.signal_aggregation import generate_collection_feedback_report
from workflow.signal_storage import SignalStore

# Load all signals
store = SignalStore()
all_signals = store.load_all_signals()

# Get all artifact IDs
artifact_ids = store.list_artifacts_with_signals()

# Generate collection report for January
report = generate_collection_feedback_report(
    artifact_ids=artifact_ids,
    all_signals=all_signals,
    window_start="2026-01-01T00:00:00Z",
    window_end="2026-01-31T23:59:59Z"
)

print(f"Total signals: {report.total_signals}")
print(f"Insights: {report.insights}")
```

### Example 3: Query High-Performing Stories

```python
from workflow.phase5_feedback_interface import get_feedback_interface

feedback = get_feedback_interface()

# Get stories with rating >= 4.5
high_performers = feedback.get_high_performing_stories(
    min_rating=4.5,
    min_revenue=0
)

print(f"High performers: {high_performers}")
# ["win-2026-01-US-1234abcd", "win-2026-01-UK-5678efgh"]
```

---

## Determinism & Reproducibility

Phase 8 guarantees:
- **Reproducible aggregations**: Same signals + same window = same aggregation
- **Immutable raw signals**: Never modified, only appended
- **Versioned methods**: Aggregation methods have explicit versions
- **No hidden scoring**: All metrics are explicit and transparent

---

## Boundary Compliance

### Phase 8 DOES NOT:

- ❌ Modify SuccessStory content
- ❌ Modify Phase 6 outputs
- ❌ Modify Phase 7 publish records
- ❌ Automatically change Phase 5 scores
- ❌ Retroactively alter past approvals
- ❌ Leak feedback into Phase 6 rendering or Phase 7 publishing

### Phase 8 DOES:

- ✅ Collect signals from external sources
- ✅ Normalize signals into structured objects
- ✅ Aggregate signals over time windows
- ✅ Generate recommendations (advisory only)
- ✅ Provide read-only interface for Phase 5
- ✅ Preserve raw signals for audit trail

---

## Future Enhancements

Potential future features for Phase 8:

1. **Automated Signal Collection**: Background workers to collect signals from APIs/webhooks
2. **Machine Learning Insights**: ML models to detect patterns and anomalies
3. **A/B Testing Feedback**: Track performance of different story versions
4. **Real-Time Dashboards**: UI for viewing signal data and trends
5. **Correlation Analysis**: Identify which story attributes correlate with success
6. **Predictive Models**: Predict which stories will perform well

---

*Phase 8: Feedback / Signal Loop*
*Last Updated: 2026-02-01*
