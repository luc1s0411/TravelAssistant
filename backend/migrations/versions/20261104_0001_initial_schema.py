"""Initial travel-planner schema. Frozen revision; do not import live ORM models.

Revision ID: 20261104_0001
Revises: None
Creates 13 business tables. Downgrade deletes these tables and all their data.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '20261104_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Frozen initial schema; subsequent changes require a new revision.
    op.create_table('users',
    sa.Column('username', sa.String(length=64), nullable=False, comment='账号规范化由认证服务负责'),
    sa.Column('password_hash', sa.String(length=255), nullable=False, comment='成熟密码算法生成的哈希，禁止明文密码'),
    sa.Column('display_name', sa.String(length=64), nullable=False),
    sa.Column('is_active', sa.Boolean(create_constraint=True, name='is_active_bool'), server_default='1', nullable=False),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('username', name=op.f('uq_users_username')),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_table('trip_drafts',
    sa.Column('user_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('revision', sa.Integer(), server_default='1', nullable=False),
    sa.Column('status', sa.Enum('collecting', 'selecting', 'confirmed', 'archived', name='draft_status', native_enum=False, create_constraint=True, length=32), server_default='collecting', nullable=False),
    sa.Column('destination', sa.String(length=128), nullable=True),
    sa.Column('departure_city', sa.String(length=128), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('arrival_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=True),
    sa.Column('departure_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=True),
    sa.Column('timezone_name', sa.String(length=64), server_default='Asia/Shanghai', nullable=False),
    sa.Column('traveler_count', sa.Integer(), nullable=True),
    sa.Column('room_count', sa.Integer(), nullable=True),
    sa.Column('transport_mode', sa.Enum('walking', 'driving', 'transit', 'bicycling', name='transport_mode', native_enum=False, create_constraint=True, length=32), nullable=True),
    sa.Column('preferences', sa.JSON(), nullable=False, comment='兴趣、饮食、节奏、用户确认的限制'),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False),
    sa.CheckConstraint('arrival_at IS NULL OR departure_at IS NULL OR departure_at >= arrival_at', name=op.f('ck_trip_drafts_arrival_range')),
    sa.CheckConstraint('revision > 0', name=op.f('ck_trip_drafts_revision_positive')),
    sa.CheckConstraint('room_count > 0', name=op.f('ck_trip_drafts_room_count_positive')),
    sa.CheckConstraint('start_date IS NULL OR end_date IS NULL OR end_date >= start_date', name=op.f('ck_trip_drafts_date_range')),
    sa.CheckConstraint('traveler_count > 0', name=op.f('ck_trip_drafts_traveler_count_positive')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_trip_drafts_user_id_users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_trip_drafts')),
    sa.UniqueConstraint('id', 'user_id', name='uq_draft_owner'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_drafts_user_updated', 'trip_drafts', ['user_id', 'updated_at'], unique=False)
    op.create_table('confirmed_inputs',
    sa.Column('draft_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('draft_revision', sa.Integer(), nullable=False),
    sa.Column('snapshot', sa.JSON(), nullable=False, comment='不可变的需求和预算快照，不保存原始供应商响应'),
    sa.Column('snapshot_hash', sa.String(length=64), nullable=False, comment='规范化快照 SHA256，小写十六进制'),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.CheckConstraint('draft_revision > 0', name=op.f('ck_confirmed_inputs_draft_revision_positive')),
    sa.ForeignKeyConstraint(['draft_id'], ['trip_drafts.id'], name=op.f('fk_confirmed_inputs_draft_id_trip_drafts'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_confirmed_inputs')),
    sa.UniqueConstraint('id', 'draft_id', name='uq_confirmation_draft'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_confirmation_revision', 'confirmed_inputs', ['draft_id', 'draft_revision'], unique=False)
    op.create_table('draft_budgets',
    sa.Column('draft_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('category', sa.Enum('total', 'lodging', 'food', 'attraction', name='budget_category', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('mode', sa.Enum('unknown', 'limited', 'unlimited', name='budget_mode', native_enum=False, create_constraint=True, length=32), server_default='unknown', nullable=False),
    sa.Column('unit', sa.Enum('room_night', 'person_day', 'person_trip', 'person', 'item', 'vehicle', 'total', name='budget_unit', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('currency', sa.String(length=3), server_default='CNY', nullable=False),
    sa.Column('cap_minor', sa.BigInteger(), nullable=True),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False),
    sa.CheckConstraint("(category = 'total' AND unit = 'total') OR (category = 'lodging' AND unit = 'room_night') OR (category = 'food' AND unit = 'person_day') OR (category = 'attraction' AND unit = 'person_trip')", name=op.f('ck_draft_budgets_budget_category_unit')),
    sa.CheckConstraint("(mode = 'limited' AND cap_minor IS NOT NULL AND cap_minor >= 0) OR (mode IN ('unknown', 'unlimited') AND cap_minor IS NULL)", name=op.f('ck_draft_budgets_budget_mode_amount')),
    sa.ForeignKeyConstraint(['draft_id'], ['trip_drafts.id'], name=op.f('fk_draft_budgets_draft_id_trip_drafts'), ondelete='RESTRICT'),
    sa.CheckConstraint("currency = 'CNY'", name=op.f("ck_draft_budgets_currency_cny")),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_draft_budgets')),
    sa.UniqueConstraint('draft_id', 'category', name='uq_budget_category'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_table('trip_selections',
    sa.Column('draft_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('category', sa.Enum('lodging', 'food', 'attraction', name='category', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('source_provider', sa.String(length=32), nullable=False),
    sa.Column('source_item_id', sa.String(length=255), nullable=True, comment='仅保存获得授权的外部引用'),
    sa.Column('source_product_id', sa.String(length=255), nullable=True),
    sa.Column('display_name', sa.String(length=255), nullable=False, comment='获准保存的名称或用户自定标签'),
    sa.Column('source_refs', sa.JSON(), nullable=False),
    sa.Column('usage_key', sa.String(length=64), nullable=False, comment='服务端生成的幂等使用实例键；重复添加复用，跨天使用用新键'),
    sa.Column('use_start_date', sa.Date(), nullable=True),
    sa.Column('use_end_date', sa.Date(), nullable=True, comment='住宿离店日为不含当日，其他项目按业务说明'),
    sa.Column('quantity', sa.Integer(), server_default='1', nullable=False, comment='计价数量，不自动等于人数或晚数'),
    sa.Column('is_mandatory', sa.Boolean(create_constraint=True, name='is_mandatory_bool'), server_default='0', nullable=False),
    sa.Column('is_active', sa.Boolean(create_constraint=True, name='is_active_bool'), server_default='1', nullable=False, comment='移除选择只置为 false，保留历史确认关联'),
    sa.Column('user_note', sa.Text(), nullable=True),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False),
    sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
    sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
    sa.Column('coordinate_system', sa.Enum('gcj02', 'wgs84', name='coordinate_system', native_enum=False, create_constraint=True, length=32), nullable=True),
    sa.Column('address', sa.String(length=512), nullable=True, comment='仅保存获授权内容或用户填写地址'),
    sa.Column('currency', sa.String(length=3), server_default='CNY', nullable=False),
    sa.Column('price_kind', sa.Enum('unknown', 'reference', 'quoted', 'user_entered', name='price_kind', native_enum=False, create_constraint=True, length=32), server_default='unknown', nullable=False),
    sa.Column('price_unit', sa.Enum('room_night', 'person_day', 'person_trip', 'person', 'item', 'vehicle', 'total', name='price_unit', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('price_min_minor', sa.BigInteger(), nullable=True, comment='单价下限，整数分；未知为 NULL'),
    sa.Column('price_max_minor', sa.BigInteger(), nullable=True, comment='单价上限，整数分；明确免费为 0'),
    sa.Column('price_queried_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=True),
    sa.Column('price_conditions', sa.JSON(), nullable=False, comment='获准保存的日期、规格等计价条件'),
    sa.CheckConstraint("(price_kind = 'unknown' AND price_min_minor IS NULL AND price_max_minor IS NULL) OR (price_kind = 'reference' AND price_min_minor IS NOT NULL) OR (price_kind IN ('quoted','user_entered') AND price_min_minor IS NOT NULL AND price_max_minor IS NOT NULL)", name=op.f('ck_trip_selections_price_known_pair')),
    sa.CheckConstraint('(longitude IS NULL AND latitude IS NULL AND coordinate_system IS NULL) OR (longitude IS NOT NULL AND latitude IS NOT NULL AND coordinate_system IS NOT NULL)', name=op.f('ck_trip_selections_coordinate_pair')),
    sa.CheckConstraint('latitude IS NULL OR (latitude >= -90 AND latitude <= 90)', name=op.f('ck_trip_selections_latitude_range')),
    sa.CheckConstraint('longitude IS NULL OR (longitude >= -180 AND longitude <= 180)', name=op.f('ck_trip_selections_longitude_range')),
    sa.CheckConstraint('price_max_minor IS NULL OR price_max_minor >= 0', name=op.f('ck_trip_selections_price_max_nonnegative')),
    sa.CheckConstraint('price_max_minor IS NULL OR price_min_minor IS NULL OR price_max_minor >= price_min_minor', name=op.f('ck_trip_selections_price_range')),
    sa.CheckConstraint('price_min_minor IS NULL OR price_min_minor >= 0', name=op.f('ck_trip_selections_price_min_nonnegative')),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_trip_selections_quantity_positive')),
    sa.CheckConstraint('use_start_date IS NULL OR use_end_date IS NULL OR use_end_date >= use_start_date', name=op.f('ck_trip_selections_use_date_range')),
    sa.ForeignKeyConstraint(['draft_id'], ['trip_drafts.id'], name=op.f('fk_trip_selections_draft_id_trip_drafts'), ondelete='RESTRICT'),
    sa.CheckConstraint("currency = 'CNY'", name=op.f("ck_trip_selections_currency_cny")),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_trip_selections')),
    sa.UniqueConstraint('draft_id', 'usage_key', name='uq_selection_usage'),
    sa.UniqueConstraint('id', 'draft_id', name='uq_selection_draft'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_selection_draft_active_category', 'trip_selections', ['draft_id', 'is_active', 'category'], unique=False)
    op.create_table('confirmed_selections',
    sa.Column('confirmation_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('draft_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('selection_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('snapshot', sa.JSON(), nullable=False, comment='本次确认时的选择快照，后续候选修改不改变此内容'),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.ForeignKeyConstraint(['confirmation_id', 'draft_id'], ['confirmed_inputs.id', 'confirmed_inputs.draft_id'], name='fk_confirmed_selection_input', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['selection_id', 'draft_id'], ['trip_selections.id', 'trip_selections.draft_id'], name='fk_confirmed_selection_draft', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_confirmed_selections')),
    sa.UniqueConstraint('confirmation_id', 'selection_id', name='uq_confirmed_selection'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_table('plans',
    sa.Column('user_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('draft_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('confirmation_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('current_version', sa.Integer(), server_default='0', nullable=False, comment='0 为尚无成功版本；发布必须在事务内更新'),
    sa.Column('is_archived', sa.Boolean(create_constraint=True, name='is_archived_bool'), server_default='0', nullable=False),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False),
    sa.CheckConstraint('current_version >= 0', name=op.f('ck_plans_current_version_nonnegative')),
    sa.ForeignKeyConstraint(['confirmation_id', 'draft_id'], ['confirmed_inputs.id', 'confirmed_inputs.draft_id'], name='fk_plan_confirmation', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['draft_id', 'user_id'], ['trip_drafts.id', 'trip_drafts.user_id'], name='fk_plan_draft_owner', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_plans')),
    sa.UniqueConstraint('id', 'draft_id', name='uq_plan_draft'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_plans_user_updated', 'plans', ['user_id', 'is_archived', 'updated_at'], unique=False)
    op.create_table('plan_versions',
    sa.Column('plan_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('timezone_name', sa.String(length=64), nullable=False),
    sa.Column('input_snapshot', sa.JSON(), nullable=False),
    sa.Column('budget_summary', sa.JSON(), nullable=False, comment='已知小计、区间、未知项目；金额仍使用分'),
    sa.Column('warnings', sa.JSON(), nullable=False),
    sa.Column('change_summary', sa.Text(), nullable=True),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.CheckConstraint('end_date >= start_date', name=op.f('ck_plan_versions_version_date_range')),
    sa.CheckConstraint('version > 0', name=op.f('ck_plan_versions_version_positive')),
    sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], name=op.f('fk_plan_versions_plan_id_plans'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_plan_versions')),
    sa.UniqueConstraint('id', 'plan_id', name='uq_version_plan'),
    sa.UniqueConstraint('plan_id', 'version', name='uq_plan_version_number'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_table('planning_requests',
    sa.Column('user_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('draft_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('confirmation_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('idempotency_key', sa.String(length=64), nullable=False),
    sa.Column('request_hash', sa.String(length=64), nullable=False, comment='规范化请求 SHA256，不存原始对话'),
    sa.Column('status', sa.Enum('pending', 'running', 'succeeded', 'failed', name='request_status', native_enum=False, create_constraint=True, length=32), server_default='pending', nullable=False),
    sa.Column('plan_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=True),
    sa.Column('error_code', sa.String(length=64), nullable=True),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('updated_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False),
    sa.CheckConstraint("status <> 'succeeded' OR plan_id IS NOT NULL", name=op.f('ck_planning_requests_request_success_plan')),
    sa.ForeignKeyConstraint(['confirmation_id', 'draft_id'], ['confirmed_inputs.id', 'confirmed_inputs.draft_id'], name='fk_request_confirmation', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['draft_id', 'user_id'], ['trip_drafts.id', 'trip_drafts.user_id'], name='fk_request_draft_owner', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['plan_id', 'draft_id'], ['plans.id', 'plans.draft_id'], name='fk_request_plan_draft', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_planning_requests')),
    sa.UniqueConstraint('user_id', 'idempotency_key', name='uq_request_user_key'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_request_user_status', 'planning_requests', ['user_id', 'status'], unique=False)
    op.create_table('plan_items',
    sa.Column('plan_version_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('plan_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('draft_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('selection_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=True, comment='休息或留空可无选择；新增商家须先经用户确认'),
    sa.Column('category', sa.Enum('lodging', 'food', 'attraction', 'rest', 'free_time', name='activity_kind', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('activity_date', sa.Date(), nullable=False),
    sa.Column('sequence_no', sa.Integer(), nullable=False),
    sa.Column('starts_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=True),
    sa.Column('ends_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=True, comment='住宿可跨夜；按明确区间查询'),
    sa.Column('is_time_fixed', sa.Boolean(create_constraint=True, name='is_time_fixed_bool'), server_default='0', nullable=False),
    sa.Column('source_refs', sa.JSON(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('longitude', sa.Numeric(precision=10, scale=7), nullable=True),
    sa.Column('latitude', sa.Numeric(precision=10, scale=7), nullable=True),
    sa.Column('coordinate_system', sa.Enum('gcj02', 'wgs84', name='coordinate_system', native_enum=False, create_constraint=True, length=32), nullable=True),
    sa.Column('address', sa.String(length=512), nullable=True, comment='仅保存获授权内容或用户填写地址'),
    sa.CheckConstraint('(longitude IS NULL AND latitude IS NULL AND coordinate_system IS NULL) OR (longitude IS NOT NULL AND latitude IS NOT NULL AND coordinate_system IS NOT NULL)', name=op.f('ck_plan_items_coordinate_pair')),
    sa.CheckConstraint('latitude IS NULL OR (latitude >= -90 AND latitude <= 90)', name=op.f('ck_plan_items_latitude_range')),
    sa.CheckConstraint('longitude IS NULL OR (longitude >= -180 AND longitude <= 180)', name=op.f('ck_plan_items_longitude_range')),
    sa.CheckConstraint('sequence_no > 0', name=op.f('ck_plan_items_sequence_no_positive')),
    sa.CheckConstraint('starts_at IS NULL OR ends_at IS NULL OR ends_at > starts_at', name=op.f('ck_plan_items_activity_time_range')),
    sa.ForeignKeyConstraint(['plan_id', 'draft_id'], ['plans.id', 'plans.draft_id'], name='fk_item_plan_draft', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['plan_version_id', 'plan_id'], ['plan_versions.id', 'plan_versions.plan_id'], name='fk_item_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['selection_id', 'draft_id'], ['trip_selections.id', 'trip_selections.draft_id'], name='fk_item_selection', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_plan_items')),
    sa.UniqueConstraint('id', 'plan_version_id', name='uq_item_version'),
    sa.UniqueConstraint('plan_version_id', 'activity_date', 'sequence_no', name='uq_item_sequence'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_item_version_date_category', 'plan_items', ['plan_version_id', 'activity_date', 'category'], unique=False)
    op.create_table('revision_previews',
    sa.Column('plan_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('base_version', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'applied', 'expired', 'cancelled', name='preview_status', native_enum=False, create_constraint=True, length=32), server_default='pending', nullable=False),
    sa.Column('proposed_plan', sa.JSON(), nullable=False, comment='仅结构化变更提案；确认前不发布'),
    sa.Column('change_summary', sa.Text(), nullable=False),
    sa.Column('expires_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False),
    sa.Column('applied_version', sa.Integer(), nullable=True),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.CheckConstraint("(status = 'applied' AND applied_version IS NOT NULL AND applied_version > base_version) OR (status <> 'applied' AND applied_version IS NULL)", name=op.f('ck_revision_previews_preview_applied_state')),
    sa.ForeignKeyConstraint(['plan_id', 'applied_version'], ['plan_versions.plan_id', 'plan_versions.version'], name='fk_preview_applied_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['plan_id', 'base_version'], ['plan_versions.plan_id', 'plan_versions.version'], name='fk_preview_base_version', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_revision_previews')),
    sa.UniqueConstraint('plan_id', 'applied_version', name='uq_preview_applied_version'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_preview_plan_status', 'revision_previews', ['plan_id', 'status'], unique=False)
    op.create_table('plan_costs',
    sa.Column('plan_version_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('plan_item_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=True),
    sa.Column('category', sa.String(length=32), nullable=False, comment='lodging/food/attraction/transport/other'),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('multiplier', sa.Integer(), nullable=False, comment='明确计价份数；房晚、人数等由服务计算'),
    sa.Column('source_refs', sa.JSON(), nullable=False),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.Column('currency', sa.String(length=3), server_default='CNY', nullable=False),
    sa.Column('price_kind', sa.Enum('unknown', 'reference', 'quoted', 'user_entered', name='price_kind', native_enum=False, create_constraint=True, length=32), server_default='unknown', nullable=False),
    sa.Column('price_unit', sa.Enum('room_night', 'person_day', 'person_trip', 'person', 'item', 'vehicle', 'total', name='price_unit', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('price_min_minor', sa.BigInteger(), nullable=True, comment='单价下限，整数分；未知为 NULL'),
    sa.Column('price_max_minor', sa.BigInteger(), nullable=True, comment='单价上限，整数分；明确免费为 0'),
    sa.Column('price_queried_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=True),
    sa.Column('price_conditions', sa.JSON(), nullable=False, comment='获准保存的日期、规格等计价条件'),
    sa.CheckConstraint("(price_kind = 'unknown' AND price_min_minor IS NULL AND price_max_minor IS NULL) OR (price_kind = 'reference' AND price_min_minor IS NOT NULL) OR (price_kind IN ('quoted','user_entered') AND price_min_minor IS NOT NULL AND price_max_minor IS NOT NULL)", name=op.f('ck_plan_costs_price_known_pair')),
    sa.CheckConstraint("category IN ('lodging','food','attraction','transport','other')", name=op.f('ck_plan_costs_cost_category')),
    sa.CheckConstraint('multiplier > 0', name=op.f('ck_plan_costs_multiplier_positive')),
    sa.CheckConstraint('price_max_minor IS NULL OR price_max_minor >= 0', name=op.f('ck_plan_costs_price_max_nonnegative')),
    sa.CheckConstraint('price_max_minor IS NULL OR price_min_minor IS NULL OR price_max_minor >= price_min_minor', name=op.f('ck_plan_costs_price_range')),
    sa.CheckConstraint('price_min_minor IS NULL OR price_min_minor >= 0', name=op.f('ck_plan_costs_price_min_nonnegative')),
    sa.ForeignKeyConstraint(['plan_item_id', 'plan_version_id'], ['plan_items.id', 'plan_items.plan_version_id'], name='fk_cost_item_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['plan_version_id'], ['plan_versions.id'], name=op.f('fk_plan_costs_plan_version_id_plan_versions'), ondelete='RESTRICT'),
    sa.CheckConstraint("currency = 'CNY'", name=op.f("ck_plan_costs_currency_cny")),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_plan_costs')),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_cost_version_category', 'plan_costs', ['plan_version_id', 'category'], unique=False)
    op.create_table('plan_routes',
    sa.Column('plan_version_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('from_item_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('to_item_id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False),
    sa.Column('transport_mode', sa.Enum('walking', 'driving', 'transit', 'bicycling', name='transport_mode', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('status', sa.Enum('verified', 'unverified', 'failed', name='route_status', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('distance_meters', sa.Integer(), nullable=True),
    sa.Column('queried_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=True),
    sa.Column('source_provider', sa.String(length=32), nullable=True),
    sa.Column('geometry', sa.JSON(), nullable=True, comment='仅获准保存时提供折线和坐标类型，否则查询后展示'),
    sa.Column('id', sa.String(length=36).with_variant(sa.String(length=36, collation='ascii_bin'), 'mysql'), nullable=False, comment='UUID 字符串'),
    sa.Column('created_at', sa.DateTime().with_variant(mysql.DATETIME(fsp=6), 'mysql'), nullable=False, comment='UTC 创建时间'),
    sa.CheckConstraint("status <> 'verified' OR (duration_seconds IS NOT NULL AND distance_meters IS NOT NULL AND queried_at IS NOT NULL AND source_provider IS NOT NULL)", name=op.f('ck_plan_routes_verified_route_fields')),
    sa.CheckConstraint('distance_meters IS NULL OR distance_meters >= 0', name=op.f('ck_plan_routes_distance_nonnegative')),
    sa.CheckConstraint('duration_seconds IS NULL OR duration_seconds >= 0', name=op.f('ck_plan_routes_duration_nonnegative')),
    sa.CheckConstraint('from_item_id <> to_item_id', name=op.f('ck_plan_routes_route_distinct_endpoints')),
    sa.ForeignKeyConstraint(['from_item_id', 'plan_version_id'], ['plan_items.id', 'plan_items.plan_version_id'], name='fk_route_from_version', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['plan_version_id'], ['plan_versions.id'], name=op.f('fk_plan_routes_plan_version_id_plan_versions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['to_item_id', 'plan_version_id'], ['plan_items.id', 'plan_items.plan_version_id'], name='fk_route_to_version', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_plan_routes')),
    sa.UniqueConstraint('plan_version_id', 'from_item_id', 'to_item_id', 'transport_mode', name='uq_route_pair_mode'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
        # End of frozen revision.


def downgrade() -> None:
    # Frozen initial schema; subsequent changes require a new revision.
    op.drop_table('plan_routes')
    op.drop_index('ix_cost_version_category', table_name='plan_costs')
    op.drop_table('plan_costs')
    op.drop_index('ix_preview_plan_status', table_name='revision_previews')
    op.drop_table('revision_previews')
    op.drop_index('ix_item_version_date_category', table_name='plan_items')
    op.drop_table('plan_items')
    op.drop_index('ix_request_user_status', table_name='planning_requests')
    op.drop_table('planning_requests')
    op.drop_table('plan_versions')
    op.drop_index('ix_plans_user_updated', table_name='plans')
    op.drop_table('plans')
    op.drop_table('confirmed_selections')
    op.drop_index('ix_selection_draft_active_category', table_name='trip_selections')
    op.drop_table('trip_selections')
    op.drop_table('draft_budgets')
    op.drop_index('ix_confirmation_revision', table_name='confirmed_inputs')
    op.drop_table('confirmed_inputs')
    op.drop_index('ix_drafts_user_updated', table_name='trip_drafts')
    op.drop_table('trip_drafts')
    op.drop_table('users')
        # End of frozen revision.
