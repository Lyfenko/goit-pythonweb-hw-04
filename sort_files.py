import argparse
import asyncio
import logging
from pathlib import Path
import aioshutil
import os

logging.basicConfig(level=logging.INFO, format='[Час: %(asctime)s] [Рівень: %(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)


async def read_folder(source: Path, output: Path):
    tasks = []
    loop = asyncio.get_running_loop()

    entries = await loop.run_in_executor(None, lambda: list(os.scandir(source)))

    for entry in entries:
        entry_path = Path(entry.path)
        if entry.is_dir():
            tasks.append(read_folder(entry_path, output))
        elif entry.is_file():
            tasks.append(copy_file(entry_path, output))
    await asyncio.gather(*tasks)


async def copy_file(file_path: Path, output: Path):
    try:
        ext = file_path.suffix[1:] or 'no_extension'
        dest_folder = output / ext
        dest_folder.mkdir(parents=True, exist_ok=True)

        dest_file = dest_folder / file_path.name
        await aioshutil.copy(file_path, dest_file)
        logger.info(f"Файл {file_path} скопійовано до {dest_folder}")
    except Exception as e:
        logger.error(f"Помилка при копіюванні файлу {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням")
    parser.add_argument('source', type=str, nargs='?', help="Шлях до вихідної папки")
    parser.add_argument('output', type=str, nargs='?', help="Шлях до папки призначення")
    args = parser.parse_args()

    source_folder = Path(args.source) if args.source else Path(input("Введіть шлях до вихідної папки: ")).resolve()
    output_folder = Path(args.output) if args.output else Path(input("Введіть шлях до папки призначення: ")).resolve()

    if not source_folder.is_dir():
        logger.error(f"Вихідна папка '{source_folder}' не знайдена або не є папкою.")
        return
    if not output_folder.exists():
        output_folder.mkdir(parents=True)

    asyncio.run(read_folder(source_folder, output_folder))


if __name__ == "__main__":
    main()
