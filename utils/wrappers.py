"""Profiling wrapper.

================================ RECONSTRUCTED STUB ================================
Minimal reconstruction of ``utils.wrappers.run_with_profiling``. Not exercised by the
adaptation-only test (``--profiling`` defaults to False) but required for import.
===================================================================================
"""
import cProfile
import pstats
import io


def run_with_profiling(model):
    """Run ``model`` under cProfile and print the top cumulative-time entries."""
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        model.run()
        model.report()
    finally:
        profiler.disable()
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
        stats.print_stats(30)
        print(stream.getvalue())
    return model

