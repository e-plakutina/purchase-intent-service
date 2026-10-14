"""Получение датасета Online Shoppers Purchasing Intention Dataset.

Запуск: python download_dataset.py

Скрипт пробует скачать датасет с Kaggle через kagglehub.
Если скачать не получилось (нет сети или авторизации Kaggle), печатает инструкцию для скачивания вручную.
"""

import shutil
import sys
from pathlib import Path

import pandas as pd

from purchase_intent.config import settings

KAGGLE_DATASET = "imakash3011/online-shoppers-purchasing-intention-dataset"
KAGGLE_URL = f"https://www.kaggle.com/datasets/{KAGGLE_DATASET}"
FILE_NAME = "online_shoppers_intention.csv"
N_ROWS = 12_330
COLUMNS = [
    "Administrative",
    "Administrative_Duration",
    "Informational",
    "Informational_Duration",
    "ProductRelated",
    "ProductRelated_Duration",
    "BounceRates",
    "ExitRates",
    "PageValues",
    "SpecialDay",
    "Month",
    "OperatingSystems",
    "Browser",
    "Region",
    "TrafficType",
    "VisitorType",
    "Weekend",
    "Revenue",
]

DATA_PATH = settings.data_dir / FILE_NAME


def download(data_dir: Path) -> None:
    """Скачивает датасет с Kaggle и копирует csv файл в data_dir."""
    try:
        import kagglehub
    except ImportError as error:
        raise ImportError(
            "Не установлен kagglehub: uv sync --group data или pip install kagglehub"
        ) from error

    downloaded = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    matches = list(downloaded.rglob(FILE_NAME))
    if not matches:
        raise FileNotFoundError(f"В скачанном датасете нет файла {FILE_NAME}")
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(matches[0], data_dir / FILE_NAME)


def check(path: Path) -> list[str]:
    """Проблемы с файлами; если пришел пустой список - все в порядке."""
    frame = pd.read_csv(path)
    problems = []
    missing = sorted(set(COLUMNS) - set(frame.columns))
    if missing:
        problems.append(f"Нет колонок {missing}")
    if len(frame) != N_ROWS:
        problems.append(f"{len(frame)} строк, в оригинальном датасете {N_ROWS}")
    return problems


def main() -> int:
    if not DATA_PATH.exists():
        print(f"Нет файла {DATA_PATH}, скачиваю {KAGGLE_DATASET} с Kaggle...")
        try:
            download(settings.data_dir)
        except Exception as error:
            print(
                f"Не удалось скачать датасет: {error}\n\n"
                f"Скачайте его вручную: {KAGGLE_URL}\n"
                f"и положите {FILE_NAME} в {settings.data_dir}, затем запустите скрипт снова.",
                file=sys.stderr,
            )
            return 1

    problems = check(DATA_PATH)
    if problems:
        print(
            "Файл не совпадает с оригинальным датасетом:\n- " + "\n-".join(problems),
            file=sys.stderr,
        )
        return 1

    print(f"{DATA_PATH}: готово")
    return 0


if __name__ == "__main__":
    sys.exit(main())
