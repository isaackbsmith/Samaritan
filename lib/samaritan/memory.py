import csv
import logging
from lib.shared.utils import SQLite

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class Memory:

    def __init__(self, base_dir) -> None:
        self.base_dir = base_dir
        self._db_path = self.base_dir.joinpath('data/memory.db')
        self._csv_path = self.base_dir.joinpath('data/core_dump.csv')

    def populate_db(self):
        try:
            with SQLite(self._db_path) as (connection, cursor):
                logger.warning(
                    "[*] No memories found. Restoring from core-dump now.")
                cursor.execute(
                    """CREATE TABLE Memories (category VARCHAR(32) NOT NULL, item INTEGER NOT NULL, response VARCHAR(255), action VARCHAR(255), next VARCHAR(255))""")
                cursor.execute(
                    """CREATE INDEX Memory_cat ON Memories(category)""")
                cursor.execute(
                    """CREATE INDEX Memory_cat_item ON Memories(category, item)""")
                with open(self._csv_path, newline='') as core_dump:
                    memories = csv.DictReader(core_dump)
                    for memory in memories:
                        data = (memory['category'], memory['item'],
                                memory['response'], memory['action'], memory['next'])
                        cursor.execute(
                            "INSERT INTO Memories VALUES (?,?,?,?,?);", data)
                connection.commit()
                logger.debug(
                    "[*] Memories have been successfully restored from core-dump.")
                connection.close()
        except Exception as e:
            logger.warning("[*] Couldn't restore memories from core-dump.")
            print(e)
