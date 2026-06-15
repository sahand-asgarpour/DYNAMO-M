"""Per-country GDP / GDP-per-capita trajectories.

================================ RECONSTRUCTED STUB ================================
Minimal reconstruction of ``GDP_change.GDP_change``. The original was never
committed. Consumers use:

  * ``agents.GDP_change.GDP_country[iso3].loc[year]``  -> scalar national GDP. Used as
    a DENOMINATOR in ``coastal_nodes`` (must be > 0).
  * ``agents.GDP_change.gpd_per_capita_dict[iso3]``    -> DataFrame indexed by year
    with a ``'perc_increase'`` column (used by ``government_agent`` cumprod logic).
  * ``agents.GDP_change.step()``                        -> advance one timestep.

The test runs with ``settings['general']['include_economic_growth'] = False`` so no
growth is applied: ``perc_increase`` is 1.0 every year and GDP is held constant.
The absolute GDP value is a PLACEHOLDER (1.0) - it only feeds a ratio that is not
reported in the adaptation-only test. Replace with the real module for meaningful
economic dynamics.
===================================================================================
"""
import numpy as np
import pandas as pd

# Year span covering historical + projection range used by the model.
_YEAR_MIN = 2000
_YEAR_MAX = 2101

# Placeholder constant national GDP (denominator only; must be > 0).
_PLACEHOLDER_GDP = 1.0


class GDP_change:
    def __init__(self, model, agents):
        self.model = model
        self.agents = agents
        self._build_tables()

    def _iso3_codes(self):
        """Unique ISO3 codes for the regions currently in the model."""
        try:
            ids = self.agents.regions.ids
        except AttributeError:
            ids = []
        iso3 = sorted({region_id[:3] for region_id in ids})
        # Always include explicitly requested areas as a fallback.
        area = self.model.args.area
        area = area if isinstance(area, (list, tuple)) else [area]
        for a in area:
            if a[:3] not in iso3:
                iso3.append(a[:3])
        return iso3 or ["NLD"]

    def _build_tables(self):
        years = np.arange(_YEAR_MIN, _YEAR_MAX + 1)
        self.gpd_per_capita_dict = {}
        self.GDP_country = {}
        for iso3 in self._iso3_codes():
            # No economic growth -> annual percentage increase of 1.0 (i.e. x1).
            self.gpd_per_capita_dict[iso3] = pd.DataFrame(
                {"perc_increase": np.ones(years.size, dtype=np.float64)},
                index=years,
            )
            self.GDP_country[iso3] = pd.Series(
                np.full(years.size, _PLACEHOLDER_GDP, dtype=np.float64),
                index=years,
            )

    def step(self):
        """No-op when economic growth is disabled (placeholder)."""
        if not self.model.settings["general"].get("include_economic_growth", False):
            return
        # Original growth dynamics are unavailable; intentionally a no-op.
        return

