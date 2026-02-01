"""
Signal storage for Phase 8: Feedback / Signal Loop.

Handles persistence of raw signals and aggregated signals.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from models.signal import Signal, AggregatedSignal

logger = logging.getLogger(__name__)


class SignalStore:
    """Storage for raw signals.

    Signals are stored in JSONL format (one JSON object per line).
    Each signal is immutable once stored.
    """

    def __init__(self, storage_dir: Path = None):
        """Initialize signal store.

        Args:
            storage_dir: Base directory for signal storage (default: vault/signals/)
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path("vault/signals")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_signal_file_path(self, artifact_id: str) -> Path:
        """Get file path for artifact's signals.

        Args:
            artifact_id: Artifact ID

        Returns:
            Path to signal file
        """
        # Use artifact ID as filename (sanitized)
        safe_id = artifact_id.replace("/", "_").replace("\\", "_")
        return self.storage_dir / f"{safe_id}.signals.jsonl"

    def save_signal(self, signal: Signal) -> None:
        """Save a single signal to storage.

        Args:
            signal: Signal to save

        Raises:
            OSError: If file write fails
        """
        file_path = self._get_signal_file_path(signal.artifact_id)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert signal to dictionary
        signal_dict = {
            "signal_id": signal.signal_id,
            "signal_type": signal.signal_type.value,
            "source": signal.source.value,
            "artifact_id": signal.artifact_id,
            "artifact_type": signal.artifact_type,
            "collected_at": signal.collected_at,
            "raw_payload": signal.raw_payload,
            "normalized_data": signal.normalized_data,
            "metadata": signal.metadata,
            "version": signal.version
        }

        # Append to JSONL file
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(signal_dict, ensure_ascii=False) + '\n')

        logger.debug(f"Saved signal {signal.signal_id} to {file_path}")

    def save_signals(self, signals: List[Signal]) -> None:
        """Save multiple signals to storage.

        Args:
            signals: List of signals to save

        Raises:
            OSError: If file write fails
        """
        for signal in signals:
            self.save_signal(signal)

    def load_signals_for_artifact(self, artifact_id: str) -> List[Signal]:
        """Load all signals for an artifact.

        Args:
            artifact_id: Artifact ID

        Returns:
            List of Signal objects
        """
        file_path = self._get_signal_file_path(artifact_id)

        if not file_path.exists():
            logger.debug(f"No signal file found for {artifact_id}")
            return []

        signals = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    signal_dict = json.loads(line)
                    signal = self._dict_to_signal(signal_dict)
                    signals.append(signal)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse signal: {e}")
                    continue

        logger.debug(f"Loaded {len(signals)} signals for {artifact_id}")
        return signals

    def load_all_signals(self) -> List[Signal]:
        """Load all signals from storage.

        Returns:
            List of all Signal objects
        """
        all_signals = []

        # Find all signal files
        signal_files = list(self.storage_dir.glob("*.signals.jsonl"))

        for signal_file in signal_files:
            with open(signal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        signal_dict = json.loads(line)
                        signal = self._dict_to_signal(signal_dict)
                        all_signals.append(signal)
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Failed to parse signal from {signal_file}: {e}")
                        continue

        logger.info(f"Loaded {len(all_signals)} total signals from {len(signal_files)} files")
        return all_signals

    def _dict_to_signal(self, signal_dict: Dict[str, Any]) -> Signal:
        """Convert dictionary to Signal object.

        Args:
            signal_dict: Signal dictionary

        Returns:
            Signal instance
        """
        from models.signal import SignalType, SignalSource

        return Signal(
            signal_id=signal_dict["signal_id"],
            signal_type=SignalType(signal_dict["signal_type"]),
            source=SignalSource(signal_dict["source"]),
            artifact_id=signal_dict["artifact_id"],
            artifact_type=signal_dict["artifact_type"],
            collected_at=signal_dict["collected_at"],
            raw_payload=signal_dict["raw_payload"],
            normalized_data=signal_dict.get("normalized_data", {}),
            metadata=signal_dict.get("metadata", {}),
            version=signal_dict.get("version", "1.0")
        )

    def count_signals_for_artifact(self, artifact_id: str) -> int:
        """Count signals for an artifact.

        Args:
            artifact_id: Artifact ID

        Returns:
            Number of signals
        """
        file_path = self._get_signal_file_path(artifact_id)

        if not file_path.exists():
            return 0

        count = 0
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    count += 1

        return count

    def list_artifacts_with_signals(self) -> List[str]:
        """List all artifact IDs that have signals.

        Returns:
            List of artifact IDs
        """
        signal_files = list(self.storage_dir.glob("*.signals.jsonl"))
        artifact_ids = []

        for signal_file in signal_files:
            # Extract artifact ID from filename
            artifact_id = signal_file.stem.replace(".signals", "")
            artifact_ids.append(artifact_id)

        return artifact_ids


class AggregatedSignalStore:
    """Storage for aggregated signals.

    Aggregated signals are stored in JSON format.
    """

    def __init__(self, storage_dir: Path = None):
        """Initialize aggregated signal store.

        Args:
            storage_dir: Base directory for storage (default: vault/signals/aggregations/)
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path("vault/signals/aggregations")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_aggregation(self, aggregation: AggregatedSignal) -> None:
        """Save an aggregated signal.

        Args:
            aggregation: AggregatedSignal to save

        Raises:
            OSError: If file write fails
        """
        file_path = self.storage_dir / f"{aggregation.aggregation_id}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "aggregation_id": aggregation.aggregation_id,
            "artifact_id": aggregation.artifact_id,
            "artifact_type": aggregation.artifact_type,
            "window_start": aggregation.window_start,
            "window_end": aggregation.window_end,
            "generated_at": aggregation.generated_at,
            "signal_count": aggregation.signal_count,
            "signal_type_counts": aggregation.signal_type_counts,
            "source_counts": aggregation.source_counts,
            "metrics": aggregation.metrics,
            "method_version": aggregation.method_version,
            "signal_ids": aggregation.signal_ids,
            "raw_signals_file": aggregation.raw_signals_file,
            "metadata": aggregation.metadata
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.debug(f"Saved aggregation {aggregation.aggregation_id} to {file_path}")

    def load_aggregation(self, aggregation_id: str) -> Optional[AggregatedSignal]:
        """Load an aggregated signal by ID.

        Args:
            aggregation_id: Aggregation ID

        Returns:
            AggregatedSignal if found, None otherwise
        """
        file_path = self.storage_dir / f"{aggregation_id}.json"

        if not file_path.exists():
            logger.debug(f"Aggregation not found: {aggregation_id}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return AggregatedSignal(
            aggregation_id=data["aggregation_id"],
            artifact_id=data["artifact_id"],
            artifact_type=data["artifact_type"],
            window_start=data["window_start"],
            window_end=data["window_end"],
            generated_at=data["generated_at"],
            signal_count=data["signal_count"],
            signal_type_counts=data["signal_type_counts"],
            source_counts=data["source_counts"],
            metrics=data["metrics"],
            method_version=data["method_version"],
            signal_ids=data["signal_ids"],
            raw_signals_file=data.get("raw_signals_file", ""),
            metadata=data.get("metadata", {})
        )

    def load_aggregations_for_artifact(self, artifact_id: str) -> List[AggregatedSignal]:
        """Load all aggregations for an artifact.

        Args:
            artifact_id: Artifact ID

        Returns:
            List of AggregatedSignal objects
        """
        aggregations = []

        # Find all aggregation files
        aggregation_files = list(self.storage_dir.glob("*.json"))

        for agg_file in aggregation_files:
            with open(agg_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if data.get("artifact_id") == artifact_id:
                        aggregation = AggregatedSignal(
                            aggregation_id=data["aggregation_id"],
                            artifact_id=data["artifact_id"],
                            artifact_type=data["artifact_type"],
                            window_start=data["window_start"],
                            window_end=data["window_end"],
                            generated_at=data["generated_at"],
                            signal_count=data["signal_count"],
                            signal_type_counts=data["signal_type_counts"],
                            source_counts=data["source_counts"],
                            metrics=data["metrics"],
                            method_version=data["method_version"],
                            signal_ids=data["signal_ids"],
                            raw_signals_file=data.get("raw_signals_file", ""),
                            metadata=data.get("metadata", {})
                        )
                        aggregations.append(aggregation)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse aggregation from {agg_file}: {e}")
                    continue

        logger.debug(f"Loaded {len(aggregations)} aggregations for {artifact_id}")
        return aggregations

    def load_all_aggregations(self) -> List[AggregatedSignal]:
        """Load all aggregations from storage.

        Returns:
            List of all AggregatedSignal objects
        """
        aggregations = []

        # Find all aggregation files
        aggregation_files = list(self.storage_dir.glob("*.json"))

        for agg_file in aggregation_files:
            with open(agg_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    aggregation = AggregatedSignal(
                        aggregation_id=data["aggregation_id"],
                        artifact_id=data["artifact_id"],
                        artifact_type=data["artifact_type"],
                        window_start=data["window_start"],
                        window_end=data["window_end"],
                        generated_at=data["generated_at"],
                        signal_count=data["signal_count"],
                        signal_type_counts=data["signal_type_counts"],
                        source_counts=data["source_counts"],
                        metrics=data["metrics"],
                        method_version=data["method_version"],
                        signal_ids=data["signal_ids"],
                        raw_signals_file=data.get("raw_signals_file", ""),
                        metadata=data.get("metadata", {})
                    )
                    aggregations.append(aggregation)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse aggregation from {agg_file}: {e}")
                    continue

        logger.info(f"Loaded {len(aggregations)} total aggregations")
        return aggregations


class FeedbackReportStore:
    """Storage for feedback reports.

    Reports are stored in JSON format.
    """

    def __init__(self, storage_dir: Path = None):
        """Initialize feedback report store.

        Args:
            storage_dir: Base directory for storage (default: vault/reports/)
        """
        self.storage_dir = Path(storage_dir) if storage_dir else Path("vault/reports")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_report(self, report_dict: Dict[str, Any], report_id: str) -> None:
        """Save a feedback report.

        Args:
            report_dict: Report dictionary (from FeedbackReport dataclass)
            report_id: Report ID

        Raises:
            OSError: If file write fails
        """
        file_path = self.storage_dir / f"{report_id}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved feedback report {report_id} to {file_path}")

    def load_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Load a feedback report by ID.

        Args:
            report_id: Report ID

        Returns:
            Report dictionary if found, None otherwise
        """
        file_path = self.storage_dir / f"{report_id}.json"

        if not file_path.exists():
            logger.debug(f"Report not found: {report_id}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def list_reports(self) -> List[str]:
        """List all report IDs.

        Returns:
            List of report IDs
        """
        report_files = list(self.storage_dir.glob("*.json"))
        report_ids = [f.stem for f in report_files]
        return report_ids
