"""Architecture smoke tests for the software/research separation."""


def test_software_namespaces_import():
    from espresso3d.software import agent, export, generation, interface, library, pipeline

    assert agent is not None
    assert export is not None
    assert generation is not None
    assert interface is not None
    assert library is not None
    assert pipeline is not None


def test_research_namespaces_import():
    from espresso3d.research import (
        dataset,
        experiment_runner,
        ground_truth,
        hardware_profiling,
        metrics,
        result_visualization,
        statistical_analysis,
    )

    assert dataset is not None
    assert experiment_runner is not None
    assert ground_truth is not None
    assert hardware_profiling is not None
    assert metrics is not None
    assert result_visualization is not None
    assert statistical_analysis is not None
