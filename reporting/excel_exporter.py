from pathlib import Path
from typing import Any, Dict, List

from pandas import DataFrame


def export_results(results: Dict[str, Any], output_dir: str = "output") -> List[str]:
    """Export supported report DataFrames to Excel files.

    The function writes out DataFrames found under the expected result keys:
    "Trade Logs", "Holdings History", and "Monthly Returns".
    Missing or unsupported entries are skipped without raising.

    Args:
        results: A mapping of result names to values, typically DataFrames.
        output_dir: Path to the directory where Excel files will be written.

    Returns:
        A list of file paths for the spreadsheets that were successfully exported.
    """
    target_directory = Path(output_dir)
    target_directory.mkdir(parents=True, exist_ok=True)

    EXPORT_FILES = {
        "Trade Logs": "trade_logs.xlsx",
        "Holdings History": "holdings_history.xlsx",
        "Monthly Returns": "monthly_returns.xlsx",
    }

    exported_files: List[str] = []

    for result_name, filename in EXPORT_FILES.items():
        dataframe = results.get(result_name)
        if not isinstance(dataframe, DataFrame):
            continue

        output_path = target_directory / filename
        dataframe.to_excel(output_path, index=False)
        exported_files.append(str(output_path))

    return exported_files
