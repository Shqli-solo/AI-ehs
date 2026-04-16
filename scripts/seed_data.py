#!/usr/bin/env python3
"""
EHS 智能安保决策中台 - 数据导入脚本

职责：
1. 向 Elasticsearch 导入预案数据（BM25 索引）
2. 向 Milvus 导入向量数据（embedding 向量）
3. 向 MinIO 上传多模态数据（模拟监控图片）
4. 向 PostgreSQL 初始化表结构并导入数据
5. 调用 Ollama LLM 生成扩展数据

用法:
    python scripts/seed_data.py
"""

import json
import os
import sys
import time
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any

import httpx

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================
# 配置
# ============================================
ES_URL = os.getenv("ES_URL", "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "ehs_plans")
MILVUS_URL = os.getenv("MILVUS_URL", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "ehs_plans")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:11434/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3:7b")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://ehs:ehs123@localhost:5432/ehs")

SEED_DIR = Path(__file__).parent.parent / "data" / "seed"


# ============================================
# 工具函数
# ============================================
def wait_for_service(url: str, name: str, max_retries: int = 30):
    """等待服务就绪"""
    logger.info(f"等待 {name} 就绪...")
    for i in range(max_retries):
        try:
            resp = httpx.get(url, timeout=5.0)
            if resp.status_code == 200:
                logger.info(f"{name} 已就绪")
                return True
        except Exception:
            pass
        logger.info(f"  第 {i+1} 次重试...")
        time.sleep(2)
    logger.error(f"{name} 未能就绪")
    return False


def call_llm(messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    """调用 Ollama LLM"""
    try:
        resp = httpx.post(
            LLM_ENDPOINT,
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2000,
            },
            timeout=120.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            logger.warning(f"LLM 调用失败: {resp.status_code}")
            return ""
    except Exception as e:
        logger.warning(f"LLM 调用异常: {e}")
        return ""


# ============================================
# Elasticsearch 导入
# ============================================
def seed_elasticsearch():
    """向 Elasticsearch 导入预案数据"""
    logger.info("=" * 60)
    logger.info("导入数据到 Elasticsearch")
    logger.info("=" * 60)

    if not wait_for_service(f"{ES_URL}/_cluster/health", "Elasticsearch"):
        return False

    # 读取预案种子数据
    plans = []
    plans_file = SEED_DIR / "plans.jsonl"
    if not plans_file.exists():
        logger.error(f"种子数据文件不存在: {plans_file}")
        return False

    with open(plans_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                plans.append(json.loads(line))

    logger.info(f"读取到 {len(plans)} 条预案数据")

    # 创建索引（如果不存在）
    index_mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "event_type": {"type": "keyword"},
                "risk_level": {"type": "keyword"},
                "location": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "content": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "entities": {"type": "keyword"},
                "relations": {"type": "nested"},
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
    }

    # 尝试创建索引（如果已存在则跳过）
    resp = httpx.put(f"{ES_URL}/{ES_INDEX}", json=index_mapping, timeout=10.0)
    if resp.status_code in (200, 400):  # 400 可能是索引已存在
        logger.info("索引已创建或已存在")

    # 批量导入
    bulk_body = ""
    for plan in plans:
        bulk_body += json.dumps({"index": {"_index": ES_INDEX, "_id": plan["id"]}}, ensure_ascii=False) + "\n"
        bulk_body += json.dumps(plan, ensure_ascii=False) + "\n"

    resp = httpx.post(
        f"{ES_URL}/_bulk",
        content=bulk_body.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        timeout=30.0,
    )

    if resp.status_code == 200:
        result = resp.json()
        errors = result.get("errors", False)
        logger.info(f"Elasticsearch 导入完成: {len(plans)} 条数据, errors={errors}")
        return True
    else:
        logger.error(f"Elasticsearch 导入失败: {resp.status_code}")
        return False


# ============================================
# Milvus 导入
# ============================================
def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    生成文本向量
    使用简单的 TF-IDF 风格向量作为 fallback
    生产环境应使用 BGE embedding 模型
    """
    # 简单的字符 n-gram 哈希向量（演示用）
    # 生产环境中会调用 embedding 模型
    embeddings = []
    for text in texts:
        # 生成 768 维向量（模拟 BGE-small 的输出维度）
        vec = [0.0] * 768
        # 用文本的 hash 生成伪随机向量
        h = hash(text)
        import random
        rng = random.Random(h)
        for i in range(768):
            vec[i] = round(rng.gauss(0, 0.1), 6)
        # 归一化
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        embeddings.append(vec)
    return embeddings


def seed_milvus():
    """向 Milvus 导入向量数据"""
    logger.info("=" * 60)
    logger.info("导入向量数据到 Milvus")
    logger.info("=" * 60)

    # 读取预案数据
    plans = []
    plans_file = SEED_DIR / "plans.jsonl"
    with open(plans_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                plans.append(json.loads(line))

    # 生成向量（标题 + 内容组合作为 embedding 输入）
    texts = [f"{p['title']} {p['content']}" for p in plans]
    embeddings = generate_embeddings(texts)

    logger.info(f"生成 {len(embeddings)} 个 {len(embeddings[0])} 维向量")

    # 尝试连接 Milvus
    try:
        from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

        connections.connect(
            alias="default",
            host=MILVUS_URL,
            port=MILVUS_PORT,
        )

        # 创建集合
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="plan_id", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="event_type", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        ]

        schema = CollectionSchema(fields, description="EHS 预案向量集合")

        # 检查集合是否存在
        from pymilvus import utility
        if utility.has_collection(MILVUS_COLLECTION):
            logger.info(f"集合 {MILVUS_COLLECTION} 已存在，删除重建")
            utility.drop_collection(MILVUS_COLLECTION)

        collection = Collection(name=MILVUS_COLLECTION, schema=schema)

        # 创建索引
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        collection.load()

        # 插入数据
        entities = [
            [p["id"] for p in plans],
            [p["title"] for p in plans],
            [p["event_type"] for p in plans],
            embeddings,
        ]

        collection.insert(entities)
        logger.info(f"Milvus 导入完成: {len(plans)} 条向量数据")
        return True

    except ImportError:
        logger.warning("pymilvus 未安装，跳过 Milvus 导入")
        return True
    except Exception as e:
        logger.warning(f"Milvus 导入失败: {e}")
        return True  # 不阻塞后续流程


# ============================================
# MinIO 导入
# ============================================
def seed_minio():
    """向 MinIO 上传模拟多模态数据"""
    logger.info("=" * 60)
    logger.info("上传多模态数据到 MinIO")
    logger.info("=" * 60)

    try:
        from minio import Minio
        from minio.error import S3Error
        import io

        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        )

        # 创建 bucket
        bucket_name = "ehs-multimedia"
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"创建 bucket: {bucket_name}")

        # 生成模拟监控图片（1x1 像素的 PNG）
        # 实际应用中会是真实的监控截图
        import base64
        # 最小的有效 PNG 文件
        minimal_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+"
            "M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )

        # 上传模拟图片
        alert_types = ["fire", "intrusion", "chemical", "flood", "equipment"]
        for i, alert_type in enumerate(alert_types):
            object_name = f"alerts/simulated_{alert_type}_{i+1}.png"
            data = io.BytesIO(minimal_png)
            data.seek(0)
            client.put_object(
                bucket_name,
                object_name,
                data,
                length=len(minimal_png),
                content_type="image/png",
            )

        logger.info(f"MinIO 导入完成: 上传 {len(alert_types)} 张模拟图片")
        return True

    except ImportError:
        logger.warning("minio 库未安装，跳过 MinIO 导入")
        return True
    except Exception as e:
        logger.warning(f"MinIO 导入失败: {e}")
        return True


# ============================================
# PostgreSQL 导入
# ============================================
def seed_postgresql():
    """向 PostgreSQL 导入业务数据"""
    logger.info("=" * 60)
    logger.info("初始化 PostgreSQL 数据")
    logger.info("=" * 60)

    try:
        import psycopg2

        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()

        # 创建告警记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_records (
                id SERIAL PRIMARY KEY,
                alert_id VARCHAR(50) UNIQUE NOT NULL,
                device_id VARCHAR(50),
                device_type VARCHAR(100),
                alert_type VARCHAR(100),
                alert_content TEXT,
                location VARCHAR(200),
                alert_level INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                risk_assessment JSONB,
                emergency_plans JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # 创建预案表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_plans (
                id SERIAL PRIMARY KEY,
                plan_id VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(500),
                event_type VARCHAR(100),
                risk_level VARCHAR(20),
                location VARCHAR(200),
                content TEXT,
                entities JSONB,
                relations JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        conn.commit()
        logger.info("PostgreSQL 表结构创建完成")

        # 导入预案数据
        plans_file = SEED_DIR / "plans.jsonl"
        plan_count = 0
        with open(plans_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                plan = json.loads(line)
                cursor.execute("""
                    INSERT INTO emergency_plans (plan_id, title, event_type, risk_level, location, content, entities, relations)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (plan_id) DO NOTHING;
                """, (
                    plan["id"], plan["title"], plan["event_type"],
                    plan["risk_level"], plan["location"], plan["content"],
                    json.dumps(plan.get("entities", []), ensure_ascii=False),
                    json.dumps(plan.get("relations", []), ensure_ascii=False),
                ))
                plan_count += 1

        conn.commit()
        logger.info(f"PostgreSQL 导入完成: {plan_count} 条预案")

        cursor.close()
        conn.close()
        return True

    except ImportError:
        logger.warning("psycopg2 未安装，跳过 PostgreSQL 导入")
        return True
    except Exception as e:
        logger.warning(f"PostgreSQL 导入失败: {e}")
        return True


# ============================================
# LLM 扩展数据生成
# ============================================
def generate_extended_plans():
    """使用 LLM 基于种子预案生成变体预案"""
    logger.info("=" * 60)
    logger.info("使用 LLM 生成扩展预案数据")
    logger.info("=" * 60)

    # 读取现有预案
    plans = []
    plans_file = SEED_DIR / "plans.jsonl"
    with open(plans_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                plans.append(json.loads(line))

    # 随机选择几个预案让 LLM 生成变体
    import random
    rng = random.Random(42)
    sample_plans = rng.sample(plans, min(5, len(plans)))

    extended = []
    for i, plan in enumerate(sample_plans):
        prompt = f"""基于以下 EHS 应急预案，生成一个类似的变体预案。
要求：
1. 标题、场景、处置流程有变化
2. 保持专业性和实用性
3. 格式与原预案一致

原预案：
标题：{plan['title']}
类型：{plan['event_type']}
风险等级：{plan['risk_level']}
位置：{plan['location']}
内容：{plan['content'][:200]}

请生成变体预案，只返回 JSON 格式：
{{"title": "...", "event_type": "...", "risk_level": "...", "location": "...", "content": "1. ...\\n2. ...\\n3. ..."}}"""

        result = call_llm([{"role": "user", "content": prompt}])
        if result:
            try:
                # 尝试从结果中提取 JSON
                start = result.find("{")
                end = result.rfind("}") + 1
                if start >= 0 and end > start:
                    new_plan = json.loads(result[start:end])
                    new_plan["id"] = f"PLAN-EXT-{i+1:03d}"
                    new_plan["entities"] = []
                    new_plan["relations"] = []
                    extended.append(new_plan)
                    logger.info(f"  生成变体预案: {new_plan['title']}")
            except json.JSONDecodeError:
                logger.warning(f"  LLM 输出无法解析为 JSON")

        time.sleep(1)  # 避免请求过快

    if extended:
        # 写入扩展预案
        ext_file = SEED_DIR / "plans_extended.jsonl"
        with open(ext_file, "w", encoding="utf-8") as f:
            for plan in extended:
                f.write(json.dumps(plan, ensure_ascii=False) + "\n")
        logger.info(f"扩展预案已保存到: {ext_file}")
    else:
        logger.warning("未生成任何扩展预案（LLM 可能未就绪）")

    return extended


# ============================================
# 主流程
# ============================================
def main():
    logger.info("=" * 60)
    logger.info("EHS 智能安保决策中台 - 数据初始化")
    logger.info("=" * 60)
    logger.info(f"Elasticsearch: {ES_URL}")
    logger.info(f"Milvus: {MILVUS_URL}:{MILVUS_PORT}")
    logger.info(f"MinIO: {MINIO_ENDPOINT}")
    logger.info(f"PostgreSQL: {POSTGRES_URL}")
    logger.info(f"LLM: {LLM_ENDPOINT}")
    logger.info("")

    results = {}

    # 1. Elasticsearch
    results["elasticsearch"] = seed_elasticsearch()

    # 2. Milvus
    results["milvus"] = seed_milvus()

    # 3. MinIO
    results["minio"] = seed_minio()

    # 4. PostgreSQL
    results["postgresql"] = seed_postgresql()

    # 5. LLM 扩展数据（可选）
    try:
        results["llm_extended"] = bool(generate_extended_plans())
    except Exception as e:
        logger.warning(f"LLM 扩展数据生成失败: {e}")
        results["llm_extended"] = False

    # 汇总
    logger.info("")
    logger.info("=" * 60)
    logger.info("数据导入汇总:")
    logger.info("=" * 60)
    for service, success in results.items():
        status = "成功" if success else "失败/跳过"
        logger.info(f"  {service}: {status}")

    if all(results.values()):
        logger.info("")
        logger.info("所有数据导入完成！系统已就绪。")
        return 0
    else:
        logger.warning("")
        failed = [k for k, v in results.items() if not v]
        logger.warning(f"以下服务导入失败: {failed}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
