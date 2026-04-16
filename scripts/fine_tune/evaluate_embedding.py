#!/usr/bin/env python3
"""
Embedding 相似度评估脚本

评估术语 Embedding 模型的相似度计算能力，包括：
- Top-1/Top-5 准确率评估
- 同义词/上下位词验证
- 相似度分布分析
- 生成评估报告
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field

import numpy as np

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ehs_ai.models.embedding_model import EmbeddingModel, EmbeddingConfig


@dataclass
class EvaluationArguments:
    """评估参数"""
    model_path: str = field(
        default="outputs/embedding_tuning/final_model",
        metadata={"help": "模型路径"}
    )
    data_path: str = field(
        default="data/processed/embedding_terms.json",
        metadata={"help": "评估数据路径"}
    )
    output_dir: str = field(
        default="outputs/embedding_evaluation",
        metadata={"help": "评估输出目录"}
    )
    batch_size: int = field(
        default=32,
        metadata={"help": "批大小"}
    )
    top_k: int = field(
        default=5,
        metadata={"help": "Top-K 准确率"}
    )
    similarity_threshold: float = field(
        default=0.5,
        metadata={"help": "相似度阈值"}
    )


class EmbeddingEvaluator:
    """Embedding 评估器"""

    def __init__(
        self,
        model: EmbeddingModel,
        evaluation_data: List[Dict[str, Any]],
        args: EvaluationArguments,
    ):
        self.model = model
        self.evaluation_data = evaluation_data
        self.args = args

    def evaluate_similarity_ranking(self) -> Dict[str, float]:
        """
        评估相似度排序准确率

        Returns:
            评估指标 {top-1 accuracy, top-5 accuracy, mrr}
        """
        # 构建评估样本：(query, positive_term, negative_terms)
        query_term_pairs = []

        for item in self.evaluation_data:
            anchor = item.get("anchor", item.get("term1", ""))
            positive = item.get("positive", item.get("term2", ""))
            negatives = item.get("negatives", [])

            if negatives:
                query_term_pairs.append((anchor, positive, negatives))

        # 使用模型的评估方法
        metrics = self.model.evaluate_similarity_ranking(query_term_pairs)

        return metrics

    def evaluate_term_pairs(self) -> Dict[str, Any]:
        """
        评估术语对数据质量

        Returns:
            评估报告
        """
        # 按关系类型分组
        synonym_pairs = []
        hypernym_pairs = []
        hyponym_pairs = []
        related_pairs = []

        for item in self.evaluation_data:
            term1 = item.get("anchor", item.get("term1", ""))
            term2 = item.get("positive", item.get("term2", ""))
            relation = item.get("relation", "unknown")

            if relation == "synonym":
                synonym_pairs.append((term1, term2, relation))
            elif relation in ["hypernym", "hyponym"]:
                hypernym_pairs.append((term1, term2, relation))
            elif relation == "related":
                related_pairs.append((term1, term2, relation))

        # 验证各类术语对
        reports = {}

        if synonym_pairs:
            reports["synonym"] = self.model.validate_term_pairs(synonym_pairs, "synonym")

        if hypernym_pairs:
            reports["hypernym/hyponym"] = self.model.validate_term_pairs(hypernym_pairs, "hypernym")

        if related_pairs:
            reports["related"] = self.model.validate_term_pairs(related_pairs, "related")

        return reports

    def analyze_similarity_distribution(self) -> Dict[str, Any]:
        """
        分析相似度分布

        Returns:
            分布统计信息
        """
        similarities = []

        for item in self.evaluation_data:
            term1 = item.get("anchor", item.get("term1", ""))
            term2 = item.get("positive", item.get("term2", ""))

            sim = self.model.compute_similarity_score(term1, term2)
            similarities.append(sim)

        similarities = np.array(similarities)

        # 计算分布统计
        distribution = {
            "mean": float(np.mean(similarities)),
            "std": float(np.std(similarities)),
            "min": float(np.min(similarities)),
            "max": float(np.max(similarities)),
            "median": float(np.median(similarities)),
            "percentile_25": float(np.percentile(similarities, 25)),
            "percentile_75": float(np.percentile(similarities, 75)),
            "below_threshold_count": int(np.sum(similarities < self.args.similarity_threshold)),
            "below_threshold_ratio": float(np.sum(similarities < self.args.similarity_threshold) / len(similarities)),
        }

        # 直方图数据
        hist, bin_edges = np.histogram(similarities, bins=10, range=(0, 1))
        distribution["histogram"] = {
            "bins": bin_edges.tolist(),
            "counts": hist.tolist(),
        }

        return distribution

    def generate_report(self) -> str:
        """
        生成完整评估报告

        Returns:
            报告文本
        """
        print("\n" + "=" * 60)
        print("Embedding 相似度评估报告")
        print("=" * 60)

        # 1. 相似度排序准确率
        print("\n1. 相似度排序准确率")
        print("-" * 40)
        ranking_metrics = self.evaluate_similarity_ranking()
        print(f"Top-1 Accuracy: {ranking_metrics['top_1_accuracy']:.4f}")
        print(f"Top-5 Accuracy: {ranking_metrics['top_5_accuracy']:.4f}")
        print(f"MRR (Mean Reciprocal Rank): {ranking_metrics['mrr']:.4f}")

        # 2. 术语对数据质量验证
        print("\n2. 术语对数据质量验证")
        print("-" * 40)
        pair_reports = self.evaluate_term_pairs()

        for pair_type, report in pair_reports.items():
            print(f"\n{pair_type}:")
            print(f"  总对数：{report['total_pairs']}")
            print(f"  平均相似度：{report['average_similarity']:.4f}")
            print(f"  标准差：{report['std_similarity']:.4f}")
            print(f"  最小相似度：{report['min_similarity']:.4f}")
            print(f"  最大相似度：{report['max_similarity']:.4f}")
            print(f"  低于阈值数量：{report['below_threshold_count']}")

            if report['below_threshold_pairs']:
                print(f"  低于阈值的术语对示例:")
                for pair in report['below_threshold_pairs'][:3]:
                    print(f"    - {pair['term1']} <-> {pair['term2']}: {pair['similarity']:.4f}")

        # 3. 相似度分布分析
        print("\n3. 相似度分布分析")
        print("-" * 40)
        distribution = self.analyze_similarity_distribution()
        print(f"平均值：{distribution['mean']:.4f}")
        print(f"标准差：{distribution['std']:.4f}")
        print(f"中位数：{distribution['median']:.4f}")
        print(f"最小值：{distribution['min']:.4f}")
        print(f"最大值：{distribution['max']:.4f}")
        print(f"低于阈值 ({self.args.similarity_threshold}) 比例：{distribution['below_threshold_ratio']:.4f}")

        print("\n相似度分布直方图:")
        hist = distribution["histogram"]
        for i, count in enumerate(hist["counts"]):
            bar = "#" * (count // max(hist["counts"]) * 30 + 1)
            bin_range = f"{hist['bins'][i]:.2f}-{hist['bins'][i + 1]:.2f}"
            print(f"  {bin_range}: {bar} ({count})")

        # 4. 综合评估
        print("\n4. 综合评估")
        print("-" * 40)

        # 计算综合评分
        overall_score = (
            ranking_metrics['top_1_accuracy'] * 0.4 +
            ranking_metrics['top_5_accuracy'] * 0.3 +
            ranking_metrics['mrr'] * 0.3
        )

        if overall_score >= 0.8:
            rating = "优秀 (Excellent)"
        elif overall_score >= 0.6:
            rating = "良好 (Good)"
        elif overall_score >= 0.4:
            rating = "中等 (Fair)"
        else:
            rating = "需要改进 (Needs Improvement)"

        print(f"综合评分：{overall_score:.4f}")
        print(f"评级：{rating}")

        # 5. 建议
        print("\n5. 改进建议")
        print("-" * 40)

        if ranking_metrics['top_1_accuracy'] < 0.7:
            print("- Top-1 准确率较低，建议增加训练数据或调整温度参数")

        if distribution['below_threshold_ratio'] > 0.3:
            print("- 较多术语对相似度低于阈值，建议检查数据质量或降低阈值")

        if distribution['std'] < 0.1:
            print("- 相似度分布过于集中，建议增强对比学习信号")

        if ranking_metrics['top_5_accuracy'] - ranking_metrics['top_1_accuracy'] > 0.3:
            print("- Top-1 和 Top-5 差距较大，建议优化模型区分能力")

        print("\n" + "=" * 60)

        # 生成 JSON 报告
        report_data = {
            "ranking_metrics": ranking_metrics,
            "pair_reports": pair_reports,
            "similarity_distribution": distribution,
            "overall_score": overall_score,
            "rating": rating,
        }

        return json.dumps(report_data, ensure_ascii=False, indent=2)


def load_evaluation_data(data_path: str) -> List[Dict[str, Any]]:
    """加载评估数据"""
    print(f"加载评估数据：{data_path}")

    if not os.path.exists(data_path):
        # 创建示例评估数据
        print(f"评估数据不存在，创建示例数据...")
        sample_data = [
            # 同义词
            {"anchor": "火灾", "positive": "火情", "relation": "synonym", "negatives": ["水灾", "地震"]},
            {"anchor": "泄漏", "positive": "泄露", "relation": "synonym", "negatives": ["爆炸", "燃烧"]},
            {"anchor": "危险", "positive": "风险", "relation": "synonym", "negatives": ["安全", "防护"]},
            {"anchor": "事故", "positive": "事件", "relation": "synonym", "negatives": ["预防", "应急"]},
            {"anchor": "烟雾", "positive": "烟尘", "relation": "synonym", "negatives": ["火焰", "高温"]},

            # 上下位词
            {"anchor": "气体泄漏", "positive": "氯气泄漏", "relation": "hypernym", "negatives": ["固体泄漏", "液体泄漏"]},
            {"anchor": "火灾", "positive": "电气火灾", "relation": "hypernym", "negatives": ["水灾", "地震"]},
            {"anchor": "化学品事故", "positive": "硫酸泄漏", "relation": "hypernym", "negatives": ["机械事故", "电气事故"]},
            {"anchor": "中毒", "positive": "一氧化碳中毒", "relation": "hypernym", "negatives": ["烧伤", "割伤"]},
            {"anchor": "爆炸", "positive": "气体爆炸", "relation": "hypernym", "negatives": ["火灾", "泄漏"]},

            # 相关术语
            {"anchor": "灭火器", "positive": "干粉灭火器", "relation": "related", "negatives": ["消防栓", "水带"]},
            {"anchor": "防护服", "positive": "防化服", "relation": "related", "negatives": ["安全帽", "手套"]},
            {"anchor": "应急预案", "positive": "疏散预案", "relation": "related", "negatives": ["培训计划", "检查记录"]},
            {"anchor": "风险评估", "positive": "隐患排查", "relation": "related", "negatives": ["事故报告", "整改通知"]},
            {"anchor": "安全培训", "positive": "应急演练", "relation": "related", "negatives": ["设备维护", "定期检查"]},
        ]

        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        return sample_data

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"加载 {len(data)} 条评估数据")
    return data


def main():
    parser = argparse.ArgumentParser(description="Embedding 相似度评估")

    parser.add_argument("--model-path", type=str, default="outputs/embedding_tuning/final_model")
    parser.add_argument("--data-path", type=str, default="data/processed/embedding_terms.json")
    parser.add_argument("--output-dir", type=str, default="outputs/embedding_evaluation")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--similarity-threshold", type=float, default=0.5)

    args = parser.parse_args()

    eval_args = EvaluationArguments(
        model_path=args.model_path,
        data_path=args.data_path,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        top_k=args.top_k,
        similarity_threshold=args.similarity_threshold,
    )

    # 创建输出目录
    os.makedirs(eval_args.output_dir, exist_ok=True)

    # 1. 加载模型
    print("\n" + "=" * 60)
    print("加载 Embedding 模型")
    print("=" * 60)

    config = EmbeddingConfig(
        model_name="BAAI/bge-base-zh-v1.5",
        similarity_threshold=eval_args.similarity_threshold,
    )
    model = EmbeddingModel(config)

    # 尝试加载微调后的模型，如果不存在则使用预训练模型
    if os.path.exists(eval_args.model_path):
        print(f"加载微调模型：{eval_args.model_path}")
        model.load_pretrained(eval_args.model_path)
    else:
        print(f"微调模型不存在，使用预训练模型：{config.model_name}")
        model.load_model()

    # 2. 加载评估数据
    evaluation_data = load_evaluation_data(eval_args.data_path)

    # 3. 创建评估器
    evaluator = EmbeddingEvaluator(
        model=model,
        evaluation_data=evaluation_data,
        args=eval_args,
    )

    # 4. 生成评估报告
    report_json = evaluator.generate_report()

    # 5. 保存报告
    report_path = os.path.join(eval_args.output_dir, "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_json)
    print(f"\n评估报告已保存至：{report_path}")

    # 保存文本报告
    text_report_path = os.path.join(eval_args.output_dir, "evaluation_report.txt")
    with open(text_report_path, "w", encoding="utf-8") as f:
        f.write("EHS 术语 Embedding 相似度评估报告\n")
        f.write("=" * 60 + "\n\n")
        report_data = json.loads(report_json)
        f.write(f"Top-1 Accuracy: {report_data['ranking_metrics']['top_1_accuracy']:.4f}\n")
        f.write(f"Top-5 Accuracy: {report_data['ranking_metrics']['top_5_accuracy']:.4f}\n")
        f.write(f"MRR: {report_data['ranking_metrics']['mrr']:.4f}\n")
        f.write(f"综合评分：{report_data['overall_score']:.4f}\n")
        f.write(f"评级：{report_data['rating']}\n")
    print(f"文本报告已保存至：{text_report_path}")

    print("\n评估完成!")


if __name__ == "__main__":
    main()
