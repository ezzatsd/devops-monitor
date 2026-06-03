from api.metrics import get_system_metrics


def test_get_system_metrics_contains_expected_keys():
    metrics = get_system_metrics()

    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "disk_percent" in metrics


def test_get_system_metrics_values_are_percentages():
    metrics = get_system_metrics()

    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100
    assert 0 <= metrics["disk_percent"] <= 100
