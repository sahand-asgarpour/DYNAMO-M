"""Command-line argument parsing for DYNAMO-M.

================================ RECONSTRUCTED STUB ================================
Minimal reconstruction of the original ``utils.parse_arguments``. It defines every
``args.*`` attribute that the codebase reads (discovered by grepping for ``args.``)
with reasonable defaults, so that ``run.py`` can build the model. The numerics /
behaviour are placeholders until the original implementation is supplied.
===================================================================================
"""
import argparse


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(
        description="DYNAMO-M runner (reconstructed stub argument parser)."
    )

    # --- study area selection ------------------------------------------------
    parser.add_argument("--area", dest="area", nargs="+", default=["NLD"],
                        help="ISO3 / region code(s) present in DataDrive.")
    parser.add_argument("--subdivision", dest="subdivision", default="GADM",
                        choices=["GADM", "GDL"], help="Admin subdivision source.")
    parser.add_argument("--admin_level", dest="admin_level", default="1",
                        help="Admin level (kept as string, used in file names).")
    parser.add_argument("--coastal_only", dest="coastal_only", action="store_true",
                        default=False, help="Only build coastal (flood-plain) nodes.")

    # --- climate / socio-economic scenario -----------------------------------
    parser.add_argument("--rcp", dest="rcp", default="rcp4p5",
                        help="RCP scenario (e.g. rcp4p5, rcp8p5, control).")
    parser.add_argument("--ssp", dest="ssp", default="ssp2", help="SSP scenario.")

    # --- config / settings files ---------------------------------------------
    parser.add_argument("--config", dest="config", default="config.yml")
    parser.add_argument("--settings", dest="settings", default="settings.yml")

    # --- agent / government / beach strategies -------------------------------
    parser.add_argument("--government_strategy", dest="government_strategy",
                        default="no_government")
    parser.add_argument("--beach_manager_strategy", dest="beach_manager_strategy",
                        default="none")

    # --- feature toggles ------------------------------------------------------
    parser.add_argument("--run_without_gravity_model", dest="run_without_gravity_model",
                        action="store_true", default=False)
    parser.add_argument("--run_with_checks", dest="run_with_checks",
                        action="store_true", default=False)
    parser.add_argument("--run_from_cache", dest="run_from_cache",
                        action="store_true", default=False)
    parser.add_argument("--profiling", dest="profiling", action="store_true",
                        default=False)

    # --- low-memory mode ------------------------------------------------------
    parser.add_argument("--low_memory_mode", dest="low_memory_mode",
                        action="store_true", default=False)
    parser.add_argument("--low_memory_mode_folder", dest="low_memory_mode_folder",
                        default="DataDrive/temp")

    # --- GUI / server ---------------------------------------------------------
    parser.add_argument("--GUI", dest="GUI", action="store_true", default=False)
    parser.add_argument("--no-browser", dest="browser", action="store_false",
                        default=True)
    parser.add_argument("--port", dest="port", type=int, default=8521)

    # NOTE: deliberately no ``--report_folder`` argument. ``model.py`` does
    # ``if 'report_folder' in self.args`` and would otherwise override the
    # reporter's config-derived export folder with ``None``.

    args = parser.parse_args(argv)
    return args

