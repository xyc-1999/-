-- ============================================================
--  enterprise-agent-system  数据库初始化脚本
--  由 docker-compose 挂载到 MySQL 容器并在首次启动时自动执行
-- ============================================================

CREATE DATABASE IF NOT EXISTS `enterprise_agent`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `enterprise_agent`;

-- ---------- Agent 定义表 ----------
CREATE TABLE IF NOT EXISTS `agents` (
  `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name`          VARCHAR(128)   NOT NULL COMMENT 'Agent 名称',
  `description`   TEXT           NULL COMMENT '用途描述',
  `system_prompt` TEXT           NULL COMMENT '系统提示词',
  `model`         VARCHAR(128)   NOT NULL DEFAULT 'deepseek-chat' COMMENT '默认模型',
  `state`         VARCHAR(32)    NOT NULL DEFAULT 'active' COMMENT 'active|disabled',
  `meta`          TEXT           NULL COMMENT '扩展元信息(JSON)',
  `created_at`    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_agents_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 定义表';

-- ---------- 会话记录表 ----------
CREATE TABLE IF NOT EXISTS `session_records` (
  `id`          BIGINT       NOT NULL AUTO_INCREMENT,
  `session_id`  VARCHAR(64)  NOT NULL COMMENT '会话ID',
  `agent_id`    BIGINT       NULL COMMENT '关联 Agent',
  `user_id`     VARCHAR(64)  NULL COMMENT '用户标识',
  `role`        VARCHAR(16)  NOT NULL COMMENT 'user|assistant|tool',
  `content`     TEXT         NULL COMMENT '消息内容(JSON 序列化)',
  `meta`        JSON         NULL COMMENT '扩展信息',
  `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_agent_id` (`agent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话会话记录表';

-- ---------- 客户工单表 ----------
CREATE TABLE IF NOT EXISTS `tickets` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`     VARCHAR(64)   NOT NULL COMMENT '用户标识',
  `subject`     VARCHAR(255)  NOT NULL COMMENT '工单主题',
  `content`     TEXT          NULL COMMENT '工单描述',
  `priority`    VARCHAR(16)   NOT NULL DEFAULT 'normal' COMMENT 'low|normal|high|urgent',
  `status`      VARCHAR(16)   NOT NULL DEFAULT 'open' COMMENT 'open|processing|resolved|closed',
  `created_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tickets_user` (`user_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客户工单表';

-- 示例工单数据（便于前端抽屉展示）
INSERT INTO `tickets` (`user_id`, `subject`, `content`, `priority`, `status`)
SELECT 'demo-user-001', '无法登录 OA 系统', '连续三次尝试登录企业 OA 均提示密码错误，重置邮箱未收到验证码。', 'high', 'processing'
WHERE NOT EXISTS (SELECT 1 FROM `tickets` WHERE `id`=1);

INSERT INTO `tickets` (`user_id`, `subject`, `content`, `priority`, `status`)
SELECT 'demo-user-001', '报销单据被驳回', '上周提交的差旅报销单（单号 RF-2026-1021）被驳回，原因为发票抬头不符，请协助确认正确抬头。', 'normal', 'open'
WHERE NOT EXISTS (SELECT 1 FROM `tickets` WHERE `id`=2);

INSERT INTO `tickets` (`user_id`, `subject`, `content`, `priority`, `status`)
SELECT 'demo-user-001', '申请开通飞书语音会议权限', '日常跨部门沟通需要使用音视频会议，当前账号无法发起会议，请开通权限。', 'low', 'closed'
WHERE NOT EXISTS (SELECT 1 FROM `tickets` WHERE `id`=3);
INSERT INTO `agents` (`name`, `description`, `system_prompt`, `model`)
SELECT 'default-assistant', '默认企业助手', '你是一位专业的企业智能助手。', 'deepseek-chat'
WHERE NOT EXISTS (SELECT 1 FROM `agents` WHERE `name` = 'default-assistant');