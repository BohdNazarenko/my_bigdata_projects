import asyncio
import shutil
import pandas as pd

from pathlib import Path
from watchfiles import awatch, Change
from hadoop.object_storage.aws_controller import S3Storage, CONFIG, logging

# 1) pipeline if new file exists✅
# 2) new csv -> read by pandas.DataFrame with filter and save it to temporary new file✅
# 3) send new data to s3 async to specific bucket folder✅
# 4) delete new input csv file or send it to archive✅
# 5) Logs all work time -> file with logs + send file to s3


CURRENT_DIRECTORY = Path(__file__).resolve().parent
NEW_CSV_ROOT = CURRENT_DIRECTORY / 'new_csv_files'
TMP_PATH = CURRENT_DIRECTORY / 'tmp'
ARCH_PATH = CURRENT_DIRECTORY / 'archive'

csv_filter = lambda c, p: c is Change.added and p.lower().endswith('.csv')
logger = logging.getLogger("S3")


async def is_new_file_input():
    async for changes in awatch(NEW_CSV_ROOT, watch_filter=csv_filter):
        for _, csv_path in changes:
            csv_path = Path(csv_path)

            df = pd.read_csv(csv_path)
            df_filtered = df[df["Kwota"] > 100]
            logger.info("Filter where data of column \"Kwota\" more than 100")

            TMP_PATH.mkdir(exist_ok=True)
            out_path = TMP_PATH / f"{csv_path.stem}_with_filter{csv_path.suffix}"
            df_filtered.to_csv(out_path, index=False)
            logger.info("Save csv-file with filter to tmp")

            storage = S3Storage(
                aws_access_key_id=CONFIG["aws_access_key_id"],
                aws_secret_access_key=CONFIG["aws_secret_access_key"],
                region_name=CONFIG["region_name"],
                container=CONFIG["container"]
            )

            await storage.send_file(local_source=str(out_path), target_name=f"new_csv_analise/{out_path.name}")

            ARCH_PATH.mkdir(exist_ok=True)
            await asyncio.to_thread(shutil.move, csv_path, ARCH_PATH)
            logger.info("Transferring a new file to the archive after processing")

            logger_path = CURRENT_DIRECTORY / "s3_client.log"
            await storage.send_file(local_source=str(logger_path), target_name=f"new_csv_analise/{logger_path.name}")

            return True
    return None


if __name__ == '__main__':
    result = asyncio.run(is_new_file_input())
    print('Результат обработки:', result)
