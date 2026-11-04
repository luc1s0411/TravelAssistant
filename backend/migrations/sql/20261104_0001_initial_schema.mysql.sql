-- Offline review SQL; no database was connected. Apply via Alembic, not twice.
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 20261104_0001

CREATE TABLE users (
    username VARCHAR(64) NOT NULL COMMENT '账号规范化由认证服务负责', 
    password_hash VARCHAR(255) NOT NULL COMMENT '成熟密码算法生成的哈希，禁止明文密码', 
    display_name VARCHAR(64) NOT NULL, 
    is_active BOOL NOT NULL DEFAULT '1', 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    updated_at DATETIME(6) NOT NULL, 
    CONSTRAINT pk_users PRIMARY KEY (id), 
    CONSTRAINT uq_users_username UNIQUE (username), 
    CONSTRAINT ck_users_is_active_bool CHECK (is_active IN (0, 1))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE TABLE trip_drafts (
    user_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    revision INTEGER NOT NULL DEFAULT '1', 
    status VARCHAR(32) NOT NULL DEFAULT 'collecting', 
    destination VARCHAR(128), 
    departure_city VARCHAR(128), 
    start_date DATE, 
    end_date DATE, 
    arrival_at DATETIME(6), 
    departure_at DATETIME(6), 
    timezone_name VARCHAR(64) NOT NULL DEFAULT 'Asia/Shanghai', 
    traveler_count INTEGER, 
    room_count INTEGER, 
    transport_mode VARCHAR(32), 
    preferences JSON NOT NULL COMMENT '兴趣、饮食、节奏、用户确认的限制', 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    updated_at DATETIME(6) NOT NULL, 
    CONSTRAINT pk_trip_drafts PRIMARY KEY (id), 
    CONSTRAINT ck_trip_drafts_arrival_range CHECK (arrival_at IS NULL OR departure_at IS NULL OR departure_at >= arrival_at), 
    CONSTRAINT ck_trip_drafts_revision_positive CHECK (revision > 0), 
    CONSTRAINT ck_trip_drafts_room_count_positive CHECK (room_count > 0), 
    CONSTRAINT ck_trip_drafts_date_range CHECK (start_date IS NULL OR end_date IS NULL OR end_date >= start_date), 
    CONSTRAINT ck_trip_drafts_traveler_count_positive CHECK (traveler_count > 0), 
    CONSTRAINT fk_trip_drafts_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT, 
    CONSTRAINT uq_draft_owner UNIQUE (id, user_id), 
    CONSTRAINT ck_trip_drafts_draft_status CHECK (status IN ('collecting', 'selecting', 'confirmed', 'archived')), 
    CONSTRAINT ck_trip_drafts_transport_mode CHECK (transport_mode IN ('walking', 'driving', 'transit', 'bicycling'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_drafts_user_updated ON trip_drafts (user_id, updated_at);

CREATE TABLE confirmed_inputs (
    draft_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    draft_revision INTEGER NOT NULL, 
    snapshot JSON NOT NULL COMMENT '不可变的需求和预算快照，不保存原始供应商响应', 
    snapshot_hash VARCHAR(64) NOT NULL COMMENT '规范化快照 SHA256，小写十六进制', 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    CONSTRAINT pk_confirmed_inputs PRIMARY KEY (id), 
    CONSTRAINT ck_confirmed_inputs_draft_revision_positive CHECK (draft_revision > 0), 
    CONSTRAINT fk_confirmed_inputs_draft_id_trip_drafts FOREIGN KEY(draft_id) REFERENCES trip_drafts (id) ON DELETE RESTRICT, 
    CONSTRAINT uq_confirmation_draft UNIQUE (id, draft_id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_confirmation_revision ON confirmed_inputs (draft_id, draft_revision);

CREATE TABLE draft_budgets (
    draft_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    category VARCHAR(32) NOT NULL, 
    mode VARCHAR(32) NOT NULL DEFAULT 'unknown', 
    unit VARCHAR(32) NOT NULL, 
    currency VARCHAR(3) NOT NULL DEFAULT 'CNY', 
    cap_minor BIGINT, 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    updated_at DATETIME(6) NOT NULL, 
    CONSTRAINT pk_draft_budgets PRIMARY KEY (id), 
    CONSTRAINT ck_draft_budgets_budget_category_unit CHECK ((category = 'total' AND unit = 'total') OR (category = 'lodging' AND unit = 'room_night') OR (category = 'food' AND unit = 'person_day') OR (category = 'attraction' AND unit = 'person_trip')), 
    CONSTRAINT ck_draft_budgets_budget_mode_amount CHECK ((mode = 'limited' AND cap_minor IS NOT NULL AND cap_minor >= 0) OR (mode IN ('unknown', 'unlimited') AND cap_minor IS NULL)), 
    CONSTRAINT fk_draft_budgets_draft_id_trip_drafts FOREIGN KEY(draft_id) REFERENCES trip_drafts (id) ON DELETE RESTRICT, 
    CONSTRAINT ck_draft_budgets_currency_cny CHECK (currency = 'CNY'), 
    CONSTRAINT uq_budget_category UNIQUE (draft_id, category), 
    CONSTRAINT ck_draft_budgets_budget_category CHECK (category IN ('total', 'lodging', 'food', 'attraction')), 
    CONSTRAINT ck_draft_budgets_budget_mode CHECK (mode IN ('unknown', 'limited', 'unlimited')), 
    CONSTRAINT ck_draft_budgets_budget_unit CHECK (unit IN ('room_night', 'person_day', 'person_trip', 'person', 'item', 'vehicle', 'total'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE TABLE trip_selections (
    draft_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    category VARCHAR(32) NOT NULL, 
    source_provider VARCHAR(32) NOT NULL, 
    source_item_id VARCHAR(255) COMMENT '仅保存获得授权的外部引用', 
    source_product_id VARCHAR(255), 
    display_name VARCHAR(255) NOT NULL COMMENT '获准保存的名称或用户自定标签', 
    source_refs JSON NOT NULL, 
    usage_key VARCHAR(64) NOT NULL COMMENT '服务端生成的幂等使用实例键；重复添加复用，跨天使用用新键', 
    use_start_date DATE, 
    use_end_date DATE COMMENT '住宿离店日为不含当日，其他项目按业务说明', 
    quantity INTEGER NOT NULL COMMENT '计价数量，不自动等于人数或晚数' DEFAULT '1', 
    is_mandatory BOOL NOT NULL DEFAULT '0', 
    is_active BOOL NOT NULL COMMENT '移除选择只置为 false，保留历史确认关联' DEFAULT '1', 
    user_note TEXT, 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    updated_at DATETIME(6) NOT NULL, 
    longitude NUMERIC(10, 7), 
    latitude NUMERIC(10, 7), 
    coordinate_system VARCHAR(32), 
    address VARCHAR(512) COMMENT '仅保存获授权内容或用户填写地址', 
    currency VARCHAR(3) NOT NULL DEFAULT 'CNY', 
    price_kind VARCHAR(32) NOT NULL DEFAULT 'unknown', 
    price_unit VARCHAR(32) NOT NULL, 
    price_min_minor BIGINT COMMENT '单价下限，整数分；未知为 NULL', 
    price_max_minor BIGINT COMMENT '单价上限，整数分；明确免费为 0', 
    price_queried_at DATETIME(6), 
    price_conditions JSON NOT NULL COMMENT '获准保存的日期、规格等计价条件', 
    CONSTRAINT pk_trip_selections PRIMARY KEY (id), 
    CONSTRAINT ck_trip_selections_price_known_pair CHECK ((price_kind = 'unknown' AND price_min_minor IS NULL AND price_max_minor IS NULL) OR (price_kind = 'reference' AND price_min_minor IS NOT NULL) OR (price_kind IN ('quoted','user_entered') AND price_min_minor IS NOT NULL AND price_max_minor IS NOT NULL)), 
    CONSTRAINT ck_trip_selections_coordinate_pair CHECK ((longitude IS NULL AND latitude IS NULL AND coordinate_system IS NULL) OR (longitude IS NOT NULL AND latitude IS NOT NULL AND coordinate_system IS NOT NULL)), 
    CONSTRAINT ck_trip_selections_latitude_range CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)), 
    CONSTRAINT ck_trip_selections_longitude_range CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180)), 
    CONSTRAINT ck_trip_selections_price_max_nonnegative CHECK (price_max_minor IS NULL OR price_max_minor >= 0), 
    CONSTRAINT ck_trip_selections_price_range CHECK (price_max_minor IS NULL OR price_min_minor IS NULL OR price_max_minor >= price_min_minor), 
    CONSTRAINT ck_trip_selections_price_min_nonnegative CHECK (price_min_minor IS NULL OR price_min_minor >= 0), 
    CONSTRAINT ck_trip_selections_quantity_positive CHECK (quantity > 0), 
    CONSTRAINT ck_trip_selections_use_date_range CHECK (use_start_date IS NULL OR use_end_date IS NULL OR use_end_date >= use_start_date), 
    CONSTRAINT fk_trip_selections_draft_id_trip_drafts FOREIGN KEY(draft_id) REFERENCES trip_drafts (id) ON DELETE RESTRICT, 
    CONSTRAINT ck_trip_selections_currency_cny CHECK (currency = 'CNY'), 
    CONSTRAINT uq_selection_usage UNIQUE (draft_id, usage_key), 
    CONSTRAINT uq_selection_draft UNIQUE (id, draft_id), 
    CONSTRAINT ck_trip_selections_category CHECK (category IN ('lodging', 'food', 'attraction')), 
    CONSTRAINT ck_trip_selections_is_mandatory_bool CHECK (is_mandatory IN (0, 1)), 
    CONSTRAINT ck_trip_selections_is_active_bool CHECK (is_active IN (0, 1)), 
    CONSTRAINT ck_trip_selections_coordinate_system CHECK (coordinate_system IN ('gcj02', 'wgs84')), 
    CONSTRAINT ck_trip_selections_price_kind CHECK (price_kind IN ('unknown', 'reference', 'quoted', 'user_entered')), 
    CONSTRAINT ck_trip_selections_price_unit CHECK (price_unit IN ('room_night', 'person_day', 'person_trip', 'person', 'item', 'vehicle', 'total'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_selection_draft_active_category ON trip_selections (draft_id, is_active, category);

CREATE TABLE confirmed_selections (
    confirmation_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    draft_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    selection_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    snapshot JSON NOT NULL COMMENT '本次确认时的选择快照，后续候选修改不改变此内容', 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    CONSTRAINT pk_confirmed_selections PRIMARY KEY (id), 
    CONSTRAINT fk_confirmed_selection_input FOREIGN KEY(confirmation_id, draft_id) REFERENCES confirmed_inputs (id, draft_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_confirmed_selection_draft FOREIGN KEY(selection_id, draft_id) REFERENCES trip_selections (id, draft_id) ON DELETE RESTRICT, 
    CONSTRAINT uq_confirmed_selection UNIQUE (confirmation_id, selection_id)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE TABLE plans (
    user_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    draft_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    confirmation_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    title VARCHAR(128) NOT NULL, 
    current_version INTEGER NOT NULL COMMENT '0 为尚无成功版本；发布必须在事务内更新' DEFAULT '0', 
    is_archived BOOL NOT NULL DEFAULT '0', 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    updated_at DATETIME(6) NOT NULL, 
    CONSTRAINT pk_plans PRIMARY KEY (id), 
    CONSTRAINT ck_plans_current_version_nonnegative CHECK (current_version >= 0), 
    CONSTRAINT fk_plan_confirmation FOREIGN KEY(confirmation_id, draft_id) REFERENCES confirmed_inputs (id, draft_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_plan_draft_owner FOREIGN KEY(draft_id, user_id) REFERENCES trip_drafts (id, user_id) ON DELETE RESTRICT, 
    CONSTRAINT uq_plan_draft UNIQUE (id, draft_id), 
    CONSTRAINT ck_plans_is_archived_bool CHECK (is_archived IN (0, 1))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_plans_user_updated ON plans (user_id, is_archived, updated_at);

CREATE TABLE plan_versions (
    plan_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    version INTEGER NOT NULL, 
    start_date DATE NOT NULL, 
    end_date DATE NOT NULL, 
    timezone_name VARCHAR(64) NOT NULL, 
    input_snapshot JSON NOT NULL, 
    budget_summary JSON NOT NULL COMMENT '已知小计、区间、未知项目；金额仍使用分', 
    warnings JSON NOT NULL, 
    change_summary TEXT, 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    CONSTRAINT pk_plan_versions PRIMARY KEY (id), 
    CONSTRAINT ck_plan_versions_version_date_range CHECK (end_date >= start_date), 
    CONSTRAINT ck_plan_versions_version_positive CHECK (version > 0), 
    CONSTRAINT fk_plan_versions_plan_id_plans FOREIGN KEY(plan_id) REFERENCES plans (id) ON DELETE RESTRICT, 
    CONSTRAINT uq_version_plan UNIQUE (id, plan_id), 
    CONSTRAINT uq_plan_version_number UNIQUE (plan_id, version)
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE TABLE planning_requests (
    user_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    draft_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    confirmation_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    idempotency_key VARCHAR(64) NOT NULL, 
    request_hash VARCHAR(64) NOT NULL COMMENT '规范化请求 SHA256，不存原始对话', 
    status VARCHAR(32) NOT NULL DEFAULT 'pending', 
    plan_id VARCHAR(36) COLLATE ascii_bin, 
    error_code VARCHAR(64), 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    updated_at DATETIME(6) NOT NULL, 
    CONSTRAINT pk_planning_requests PRIMARY KEY (id), 
    CONSTRAINT ck_planning_requests_request_success_plan CHECK (status <> 'succeeded' OR plan_id IS NOT NULL), 
    CONSTRAINT fk_request_confirmation FOREIGN KEY(confirmation_id, draft_id) REFERENCES confirmed_inputs (id, draft_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_request_draft_owner FOREIGN KEY(draft_id, user_id) REFERENCES trip_drafts (id, user_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_request_plan_draft FOREIGN KEY(plan_id, draft_id) REFERENCES plans (id, draft_id) ON DELETE RESTRICT, 
    CONSTRAINT uq_request_user_key UNIQUE (user_id, idempotency_key), 
    CONSTRAINT ck_planning_requests_request_status CHECK (status IN ('pending', 'running', 'succeeded', 'failed'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_request_user_status ON planning_requests (user_id, status);

CREATE TABLE plan_items (
    plan_version_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    plan_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    draft_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    selection_id VARCHAR(36) COLLATE ascii_bin COMMENT '休息或留空可无选择；新增商家须先经用户确认', 
    category VARCHAR(32) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    activity_date DATE NOT NULL, 
    sequence_no INTEGER NOT NULL, 
    starts_at DATETIME(6), 
    ends_at DATETIME(6) COMMENT '住宿可跨夜；按明确区间查询', 
    is_time_fixed BOOL NOT NULL DEFAULT '0', 
    source_refs JSON NOT NULL, 
    notes TEXT, 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    longitude NUMERIC(10, 7), 
    latitude NUMERIC(10, 7), 
    coordinate_system VARCHAR(32), 
    address VARCHAR(512) COMMENT '仅保存获授权内容或用户填写地址', 
    CONSTRAINT pk_plan_items PRIMARY KEY (id), 
    CONSTRAINT ck_plan_items_coordinate_pair CHECK ((longitude IS NULL AND latitude IS NULL AND coordinate_system IS NULL) OR (longitude IS NOT NULL AND latitude IS NOT NULL AND coordinate_system IS NOT NULL)), 
    CONSTRAINT ck_plan_items_latitude_range CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)), 
    CONSTRAINT ck_plan_items_longitude_range CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180)), 
    CONSTRAINT ck_plan_items_sequence_no_positive CHECK (sequence_no > 0), 
    CONSTRAINT ck_plan_items_activity_time_range CHECK (starts_at IS NULL OR ends_at IS NULL OR ends_at > starts_at), 
    CONSTRAINT fk_item_plan_draft FOREIGN KEY(plan_id, draft_id) REFERENCES plans (id, draft_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_item_version FOREIGN KEY(plan_version_id, plan_id) REFERENCES plan_versions (id, plan_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_item_selection FOREIGN KEY(selection_id, draft_id) REFERENCES trip_selections (id, draft_id) ON DELETE RESTRICT, 
    CONSTRAINT uq_item_version UNIQUE (id, plan_version_id), 
    CONSTRAINT uq_item_sequence UNIQUE (plan_version_id, activity_date, sequence_no), 
    CONSTRAINT ck_plan_items_activity_kind CHECK (category IN ('lodging', 'food', 'attraction', 'rest', 'free_time')), 
    CONSTRAINT ck_plan_items_is_time_fixed_bool CHECK (is_time_fixed IN (0, 1)), 
    CONSTRAINT ck_plan_items_coordinate_system CHECK (coordinate_system IN ('gcj02', 'wgs84'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_item_version_date_category ON plan_items (plan_version_id, activity_date, category);

CREATE TABLE revision_previews (
    plan_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    base_version INTEGER NOT NULL, 
    status VARCHAR(32) NOT NULL DEFAULT 'pending', 
    proposed_plan JSON NOT NULL COMMENT '仅结构化变更提案；确认前不发布', 
    change_summary TEXT NOT NULL, 
    expires_at DATETIME(6) NOT NULL, 
    applied_version INTEGER, 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    CONSTRAINT pk_revision_previews PRIMARY KEY (id), 
    CONSTRAINT ck_revision_previews_preview_applied_state CHECK ((status = 'applied' AND applied_version IS NOT NULL AND applied_version > base_version) OR (status <> 'applied' AND applied_version IS NULL)), 
    CONSTRAINT fk_preview_applied_version FOREIGN KEY(plan_id, applied_version) REFERENCES plan_versions (plan_id, version) ON DELETE RESTRICT, 
    CONSTRAINT fk_preview_base_version FOREIGN KEY(plan_id, base_version) REFERENCES plan_versions (plan_id, version) ON DELETE RESTRICT, 
    CONSTRAINT uq_preview_applied_version UNIQUE (plan_id, applied_version), 
    CONSTRAINT ck_revision_previews_preview_status CHECK (status IN ('pending', 'applied', 'expired', 'cancelled'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_preview_plan_status ON revision_previews (plan_id, status);

CREATE TABLE plan_costs (
    plan_version_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    plan_item_id VARCHAR(36) COLLATE ascii_bin, 
    category VARCHAR(32) NOT NULL COMMENT 'lodging/food/attraction/transport/other', 
    title VARCHAR(255) NOT NULL, 
    multiplier INTEGER NOT NULL COMMENT '明确计价份数；房晚、人数等由服务计算', 
    source_refs JSON NOT NULL, 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    currency VARCHAR(3) NOT NULL DEFAULT 'CNY', 
    price_kind VARCHAR(32) NOT NULL DEFAULT 'unknown', 
    price_unit VARCHAR(32) NOT NULL, 
    price_min_minor BIGINT COMMENT '单价下限，整数分；未知为 NULL', 
    price_max_minor BIGINT COMMENT '单价上限，整数分；明确免费为 0', 
    price_queried_at DATETIME(6), 
    price_conditions JSON NOT NULL COMMENT '获准保存的日期、规格等计价条件', 
    CONSTRAINT pk_plan_costs PRIMARY KEY (id), 
    CONSTRAINT ck_plan_costs_price_known_pair CHECK ((price_kind = 'unknown' AND price_min_minor IS NULL AND price_max_minor IS NULL) OR (price_kind = 'reference' AND price_min_minor IS NOT NULL) OR (price_kind IN ('quoted','user_entered') AND price_min_minor IS NOT NULL AND price_max_minor IS NOT NULL)), 
    CONSTRAINT ck_plan_costs_cost_category CHECK (category IN ('lodging','food','attraction','transport','other')), 
    CONSTRAINT ck_plan_costs_multiplier_positive CHECK (multiplier > 0), 
    CONSTRAINT ck_plan_costs_price_max_nonnegative CHECK (price_max_minor IS NULL OR price_max_minor >= 0), 
    CONSTRAINT ck_plan_costs_price_range CHECK (price_max_minor IS NULL OR price_min_minor IS NULL OR price_max_minor >= price_min_minor), 
    CONSTRAINT ck_plan_costs_price_min_nonnegative CHECK (price_min_minor IS NULL OR price_min_minor >= 0), 
    CONSTRAINT fk_cost_item_version FOREIGN KEY(plan_item_id, plan_version_id) REFERENCES plan_items (id, plan_version_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_plan_costs_plan_version_id_plan_versions FOREIGN KEY(plan_version_id) REFERENCES plan_versions (id) ON DELETE RESTRICT, 
    CONSTRAINT ck_plan_costs_currency_cny CHECK (currency = 'CNY'), 
    CONSTRAINT ck_plan_costs_price_kind CHECK (price_kind IN ('unknown', 'reference', 'quoted', 'user_entered')), 
    CONSTRAINT ck_plan_costs_price_unit CHECK (price_unit IN ('room_night', 'person_day', 'person_trip', 'person', 'item', 'vehicle', 'total'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

CREATE INDEX ix_cost_version_category ON plan_costs (plan_version_id, category);

CREATE TABLE plan_routes (
    plan_version_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    from_item_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    to_item_id VARCHAR(36) COLLATE ascii_bin NOT NULL, 
    transport_mode VARCHAR(32) NOT NULL, 
    status VARCHAR(32) NOT NULL, 
    duration_seconds INTEGER, 
    distance_meters INTEGER, 
    queried_at DATETIME(6), 
    source_provider VARCHAR(32), 
    geometry JSON COMMENT '仅获准保存时提供折线和坐标类型，否则查询后展示', 
    id VARCHAR(36) COLLATE ascii_bin NOT NULL COMMENT 'UUID 字符串', 
    created_at DATETIME(6) NOT NULL COMMENT 'UTC 创建时间', 
    CONSTRAINT pk_plan_routes PRIMARY KEY (id), 
    CONSTRAINT ck_plan_routes_verified_route_fields CHECK (status <> 'verified' OR (duration_seconds IS NOT NULL AND distance_meters IS NOT NULL AND queried_at IS NOT NULL AND source_provider IS NOT NULL)), 
    CONSTRAINT ck_plan_routes_distance_nonnegative CHECK (distance_meters IS NULL OR distance_meters >= 0), 
    CONSTRAINT ck_plan_routes_duration_nonnegative CHECK (duration_seconds IS NULL OR duration_seconds >= 0), 
    CONSTRAINT ck_plan_routes_route_distinct_endpoints CHECK (from_item_id <> to_item_id), 
    CONSTRAINT fk_route_from_version FOREIGN KEY(from_item_id, plan_version_id) REFERENCES plan_items (id, plan_version_id) ON DELETE RESTRICT, 
    CONSTRAINT fk_plan_routes_plan_version_id_plan_versions FOREIGN KEY(plan_version_id) REFERENCES plan_versions (id) ON DELETE RESTRICT, 
    CONSTRAINT fk_route_to_version FOREIGN KEY(to_item_id, plan_version_id) REFERENCES plan_items (id, plan_version_id) ON DELETE RESTRICT, 
    CONSTRAINT uq_route_pair_mode UNIQUE (plan_version_id, from_item_id, to_item_id, transport_mode), 
    CONSTRAINT ck_plan_routes_transport_mode CHECK (transport_mode IN ('walking', 'driving', 'transit', 'bicycling')), 
    CONSTRAINT ck_plan_routes_route_status CHECK (status IN ('verified', 'unverified', 'failed'))
)CHARSET=utf8mb4 ENGINE=InnoDB COLLATE utf8mb4_bin;

INSERT INTO alembic_version (version_num) VALUES ('20261104_0001');

