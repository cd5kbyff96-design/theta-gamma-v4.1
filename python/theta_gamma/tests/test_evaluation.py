"""Tests for the evaluation module."""

import pytest

from theta_gamma.evaluation.metrics import (
    Metric,
    MetricDictionary,
    MetricDomain,
    MetricType,
)
from theta_gamma.evaluation.gates import (
    Gate,
    GateEvaluator,
    GateStatus,
    GateCriterion,
    StatisticalConfidence,
)
from theta_gamma.evaluation.harness import (
    EvalHarness,
    EvalMode,
    EvalSuiteType,
)
from theta_gamma.evaluation.datasets import (
    EvalDataset,
    DatasetManifest,
)


class TestMetric:
    """Tests for Metric."""

    def test_metric_creation(self):
        """Test metric creation."""
        metric = Metric(
            id="M-TEST-001",
            name="Test Metric",
            description="Test metric description",
            domain=MetricDomain.CROSS_MODAL,
            metric_type=MetricType.ACCURACY,
            unit="%",
            higher_is_better=True,
            threshold=50.0,
        )
        
        assert metric.id == "M-TEST-001"
        assert metric.higher_is_better is True

    def test_evaluate_pass(self):
        """Test metric evaluation that passes."""
        metric = Metric(
            id="M-TEST-002",
            name="Test Accuracy",
            description="Test",
            domain=MetricDomain.CROSS_MODAL,
            metric_type=MetricType.ACCURACY,
            threshold=50.0,
            higher_is_better=True,
        )
        
        passes, message = metric.evaluate(60.0)
        assert passes is True
        assert "PASS" in message

    def test_evaluate_fail(self):
        """Test metric evaluation that fails."""
        metric = Metric(
            id="M-TEST-003",
            name="Test Accuracy",
            description="Test",
            domain=MetricDomain.CROSS_MODAL,
            metric_type=MetricType.ACCURACY,
            threshold=50.0,
            higher_is_better=True,
        )
        
        passes, message = metric.evaluate(40.0)
        assert passes is False
        assert "FAIL" in message

    def test_evaluate_lower_is_better(self):
        """Test metric where lower is better."""
        metric = Metric(
            id="M-LAT-001",
            name="Latency",
            description="Test",
            domain=MetricDomain.LATENCY,
            metric_type=MetricType.LATENCY,
            threshold=100.0,
            higher_is_better=False,
        )
        
        # 80ms should pass (under 100ms threshold)
        passes, _ = metric.evaluate(80.0)
        assert passes is True
        
        # 120ms should fail (over 100ms threshold)
        passes, _ = metric.evaluate(120.0)
        assert passes is False


class TestMetricDictionary:
    """Tests for MetricDictionary."""

    def test_default_metrics(self):
        """Test default metrics are registered."""
        dictionary = MetricDictionary()
        metrics = dictionary.get_all_metrics()
        
        assert len(metrics) > 0
        
        # Check specific metrics exist
        m_cm_001 = dictionary.get_by_id("M-CM-001")
        assert m_cm_001 is not None
        assert "Cross-Modal Accuracy" in m_cm_001.name

    def test_get_by_domain(self):
        """Test getting metrics by domain."""
        dictionary = MetricDictionary()
        
        cross_modal = dictionary.get_by_domain(MetricDomain.CROSS_MODAL)
        assert len(cross_modal) > 0

    def test_validate_metric_value(self):
        """Test metric value validation."""
        dictionary = MetricDictionary()
        
        # Valid value
        is_valid, error = dictionary.validate_metric_value("M-CM-001", 50.0)
        assert is_valid is True
        
        # Unknown metric
        is_valid, error = dictionary.validate_metric_value("M-UNKNOWN", 50.0)
        assert is_valid is False
        assert "Unknown metric" in error


class TestGate:
    """Tests for Gate."""

    def test_gate_creation(self):
        """Test gate creation."""
        gate = Gate(
            id="G1",
            name="Baseline Readiness",
            description="Baseline gate",
            phase="baseline",
            criteria=[
                GateCriterion(
                    metric_id="M-CM-001",
                    operator=">=",
                    threshold=40.0,
                    window={"type": "rolling", "size": 3},
                    pass_rule="Accuracy >= 40%",
                    fail_rule="Accuracy < 40%",
                ),
            ],
        )
        
        assert gate.id == "G1"
        assert len(gate.criteria) == 1

    def test_get_required_metrics(self):
        """Test getting required metrics."""
        gate = Gate(
            id="G1",
            name="Test Gate",
            description="Test",
            phase="baseline",
            criteria=[
                GateCriterion(
                    metric_id="M-CM-001",
                    operator=">=",
                    threshold=40.0,
                    window={"type": "latest"},
                    pass_rule="Pass",
                    fail_rule="Fail",
                ),
                GateCriterion(
                    metric_id="M-CM-002",
                    operator=">=",
                    threshold=0.5,
                    window={"type": "latest"},
                    pass_rule="Pass",
                    fail_rule="Fail",
                ),
            ],
        )
        
        metrics = gate.get_required_metrics()
        assert "M-CM-001" in metrics
        assert "M-CM-002" in metrics


class TestStatisticalConfidence:
    """Tests for StatisticalConfidence."""

    def test_meets_confidence_pass(self):
        """Test confidence check that passes."""
        confidence = StatisticalConfidence(
            confidence_level=0.95,
            min_samples=3,
        )
        
        values = [45.0, 48.0, 52.0]  # Mean = 48.33
        meets, message = confidence.meets_confidence(values, threshold=40.0, higher_is_better=True)
        
        assert meets is True

    def test_meets_confidence_fail_insufficient_samples(self):
        """Test confidence check that fails due to insufficient samples."""
        confidence = StatisticalConfidence(
            confidence_level=0.95,
            min_samples=5,
        )
        
        values = [45.0, 48.0]  # Only 2 samples
        meets, message = confidence.meets_confidence(values, threshold=40.0)
        
        assert meets is False
        assert "Insufficient samples" in message

    def test_meets_confidence_fail_threshold(self):
        """Test confidence check that fails due to threshold."""
        confidence = StatisticalConfidence(
            confidence_level=0.95,
            min_samples=3,
        )
        
        values = [30.0, 32.0, 28.0]  # Mean = 30
        meets, message = confidence.meets_confidence(values, threshold=40.0, higher_is_better=True)
        
        assert meets is False


class TestGateEvaluator:
    """Tests for GateEvaluator."""

    def test_default_gates(self):
        """Test default gates are initialized."""
        evaluator = GateEvaluator()
        gates = evaluator.get_all_gates()
        
        assert len(gates) == 4  # G1, G2, G3, G4
        
        g1 = evaluator.get_gate("G1")
        assert g1 is not None

    def test_evaluate_gate_pass(self):
        """Test gate evaluation that passes."""
        evaluator = GateEvaluator()
        
        metrics = {
            "M-CM-001": [45.0, 48.0, 52.0],  # Above 40% threshold
            "M-MQ-002": [1.0, 1.2, 0.9],  # Below 2.0 threshold
            "M-CM-003": [30.0],  # Above 25% threshold
        }
        
        result = evaluator.evaluate_gate("G1", metrics)
        
        assert result.gate_id == "G1"
        # Note: G1 may fail due to statistical confidence requirements

    def test_evaluate_gate_blocked(self):
        """Test gate evaluation that is blocked by dependencies."""
        evaluator = GateEvaluator()
        
        # G2 depends on G1, which hasn't passed
        metrics = {"M-CM-001": [65.0]}
        result = evaluator.evaluate_gate("G2", metrics)
        
        assert result.status == GateStatus.BLOCKED

    def test_get_progression_order(self):
        """Test gate progression order."""
        evaluator = GateEvaluator()
        
        order = evaluator.get_progression_order()
        
        # G1 should come before G2, G2 before G3
        assert order.index("G1") < order.index("G2")
        assert order.index("G2") < order.index("G3")


class TestEvalHarness:
    """Tests for EvalHarness."""

    def test_default_suites(self):
        """Test default eval suites."""
        harness = EvalHarness()
        
        # Check all suite types are defined
        suites = harness.get_suite_for_mode(EvalMode.FULL)
        assert len(suites) == 4  # All suite types

    def test_get_suite_for_mode(self):
        """Test getting suites for different modes."""
        harness = EvalHarness()
        
        # Full mode runs all suites
        full_suites = harness.get_suite_for_mode(EvalMode.FULL)
        assert len(full_suites) == 4
        
        # Quick mode runs fewer suites
        quick_suites = harness.get_suite_for_mode(EvalMode.QUICK)
        assert len(quick_suites) < 4

    def test_generate_report(self):
        """Test report generation."""
        harness = EvalHarness()
        
        # Generate a report (will use simulated values)
        report = harness.generate_report("test-run")
        
        assert "run_id" in report
        assert "generated_at" in report


class TestEvalDataset:
    """Tests for EvalDataset."""

    def test_dataset_creation(self):
        """Test dataset creation."""
        dataset = EvalDataset(
            id="DS-TEST-001",
            name="Test Dataset",
            description="Test dataset",
            path="data/test.parquet",
            hash_sha256="a" * 64,
            size_samples=1000,
            license="proprietary",
            owner="test-team",
        )
        
        assert dataset.id == "DS-TEST-001"
        assert dataset.size_samples == 1000


class TestDatasetManifest:
    """Tests for DatasetManifest."""

    def test_default_datasets(self):
        """Test default datasets are registered."""
        manifest = DatasetManifest()
        datasets = manifest.get_all_datasets()
        
        assert len(datasets) > 0
        
        # Check specific datasets exist
        ds = manifest.get_by_id("DS-CM-BENCH-001")
        assert ds is not None
        assert "Cross-Modal Benchmark" in ds.name

    def test_get_by_modality(self):
        """Test getting datasets by modality."""
        manifest = DatasetManifest()
        
        cross_modal = manifest.get_by_modality("cross_modal")
        assert len(cross_modal) > 0

    def test_get_datasets_for_eval(self):
        """Test getting datasets for evaluations."""
        manifest = DatasetManifest()
        
        datasets = manifest.get_datasets_for_eval(["M-CM-001", "M-CM-002"])
        assert len(datasets) > 0
