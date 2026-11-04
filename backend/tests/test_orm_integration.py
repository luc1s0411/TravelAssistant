"""Verify the supplied models are registered in the supplied offline migration."""

import io
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.dialects import mysql

from app.db import models  # noqa: F401 -- register all models
from app.db.base import Base, UTCDateTime


def test_initial_migration_covers_registered_tables_offline():
    backend = Path(__file__).resolve().parents[1]
    output = io.StringIO()
    config = Config(str(backend / "alembic.ini"), output_buffer=output)
    command.upgrade(config, "head", sql=True)

    sql = output.getvalue()
    created = set(re.findall(r"CREATE TABLE (\w+)\s*\(", sql))
    assert created - {"alembic_version"} == set(Base.metadata.tables)
    assert len(Base.metadata.tables) == 13
    assert "20261104_0001" in sql


def test_utc_datetime_rejects_naive_and_converts_aware_values():
    timestamp = UTCDateTime()
    dialect = mysql.dialect()
    local = datetime(2026, 11, 4, 12, tzinfo=timezone(timedelta(hours=8)))
    stored = timestamp.process_bind_param(local, dialect)
    assert stored == datetime(2026, 11, 4, 4)
    assert timestamp.process_result_value(stored, dialect) == datetime(2026, 11, 4, 4, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="时间必须包含时区"):
        timestamp.process_bind_param(local.replace(tzinfo=None), dialect)
