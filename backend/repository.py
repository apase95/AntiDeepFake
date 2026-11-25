import asyncio
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

FIELDS = ('analysis_id', 'source_type', 'duration_seconds', 'window_count',
          'overall_risk_level', 'max_cv_score', 'processing_time_ms')
COLUMNS = ','.join(FIELDS)


class MemoryRepository:
    name = 'memory'

    async def start(self): pass
    async def close(self): pass
    async def ready(self): return True
    async def cases(self): return []
    async def logs(self): return list(reversed(self.rows))

    def __init__(self):
        self.rows = []

    async def insert(self, row):
        self.rows.append({**row, 'created_at': datetime.now(timezone.utc).isoformat()})
        del self.rows[:-100]


class SqliteRepository:
    name = 'sqlite'

    def __init__(self, path):
        self.path = path

    async def query(self, sql, args=()):
        def execute():
            with closing(sqlite3.connect(self.path)) as conn, conn:
                conn.row_factory = sqlite3.Row
                return [dict(row) for row in conn.execute(sql, args)]
        return await asyncio.to_thread(execute)

    async def start(self):
        await self.query('CREATE TABLE IF NOT EXISTS analysis_logs (analysis_id TEXT PRIMARY KEY, '
                         'source_type TEXT, duration_seconds INTEGER, window_count INTEGER, '
                         'overall_risk_level TEXT, max_cv_score REAL, processing_time_ms INTEGER, '
                         'created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        await self.query('CREATE TABLE IF NOT EXISTS test_cases (case_id TEXT PRIMARY KEY, '
                         'title TEXT, description TEXT, video_url TEXT, cached_analysis TEXT)')

    async def close(self): pass

    async def ready(self):
        try:
            await self.query('SELECT analysis_id FROM analysis_logs LIMIT 0')
            await self.query('SELECT case_id FROM test_cases LIMIT 0')
            return True
        except sqlite3.Error:
            return False

    async def cases(self):
        return decode_cases(await self.query('SELECT * FROM test_cases ORDER BY case_id'))

    async def logs(self):
        return await self.query('SELECT * FROM analysis_logs ORDER BY rowid DESC LIMIT 100')

    async def insert(self, row):
        await self.query(f'INSERT INTO analysis_logs ({COLUMNS}) VALUES (?,?,?,?,?,?,?)',
                         tuple(row[field] for field in FIELDS))


def decode_cases(rows):
    for row in rows:
        row.pop('updated_at', None)
        if isinstance(row['cached_analysis'], str):
            row['cached_analysis'] = json.loads(row['cached_analysis'])
    return rows


class PostgresRepository:
    name = 'postgres'

    def __init__(self, url):
        self.url = url
        self.pool = None

    async def start(self):
        import asyncpg
        self.pool = await asyncpg.create_pool(self.url, min_size=1, max_size=4,
                                             timeout=5, command_timeout=5, statement_cache_size=0)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def ready(self):
        try:
            await self.pool.fetch('SELECT analysis_id FROM analysis_logs LIMIT 0')
            await self.pool.fetch('SELECT case_id FROM test_cases LIMIT 0')
            return True
        except Exception:
            return False

    async def cases(self):
        return decode_cases([dict(row) for row in await self.pool.fetch('SELECT * FROM test_cases ORDER BY case_id')])

    async def logs(self):
        return [dict(row) for row in await self.pool.fetch('SELECT * FROM analysis_logs ORDER BY created_at DESC LIMIT 100')]

    async def insert(self, row):
        args = ','.join(f'${index}' for index in range(1, len(FIELDS) + 1))
        await self.pool.execute(f'INSERT INTO analysis_logs ({COLUMNS}) VALUES ({args})',
                                *(row[field] for field in FIELDS))
