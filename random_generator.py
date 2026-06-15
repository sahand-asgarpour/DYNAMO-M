"""Centralised random-number generation for DYNAMO-M.

================================ RECONSTRUCTED STUB ================================
Minimal reconstruction of ``random_generator.RandomNumberGenerator``. The original
was never committed. Consumers use:

  * ``model.random_module.random_state`` - a NumPy Generator; methods used across the
    codebase: ``.lognormal``, ``.integers``, ``.uniform``, ``.choice``.
  * ``model.random_module.random_state_flood`` - a NumPy Generator passed to
    ``FloodRisk.stochastic_flood`` which calls ``.random()``.
  * ``model.random_module.reset_all_seeds()`` - re-seed both generators (called at
    the start of each run for reproducibility).

Both are ``numpy.random.default_rng`` instances. Seeds are fixed so a given run is
reproducible; the EXACT seeding scheme of the original is unknown (PLACEHOLDER).
===================================================================================
"""
import numpy as np

# Fixed default seeds (placeholder values; original scheme unknown).
DEFAULT_SEED = 42
DEFAULT_FLOOD_SEED = 1234


class RandomNumberGenerator:
    def __init__(self, model, seed=DEFAULT_SEED, flood_seed=DEFAULT_FLOOD_SEED):
        self.model = model
        # Allow an optional override from settings if present.
        try:
            seed = int(model.settings.get("general", {}).get("seed", seed))
        except (AttributeError, TypeError, ValueError):
            pass
        self.seed = seed
        self.flood_seed = flood_seed
        self.reset_all_seeds()

    def reset_all_seeds(self):
        """(Re)initialise all generators from the stored seeds."""
        self.random_state = np.random.default_rng(self.seed)
        self.random_state_flood = np.random.default_rng(self.flood_seed)

