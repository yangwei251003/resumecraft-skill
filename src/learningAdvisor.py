"""
学习顾问 —— 基于待补强项生成学习提升路径

输出内容:
- 优先学习顺序
- 7天快速补强计划
- 30天系统提升计划
- 推荐资源
- 面试核心概念
- 作品集方向
"""

from typing import Dict, List


class LearningAdvisor:
    """学习提升路径生成模块"""

    def generate(self, matching_result: Dict) -> str:
        """生成完整学习提升路径"""
        gaps = matching_result.get("gaps", [])
        lines = []

        lines.append("# 学习提升路径建议\n")

        # 一、优先学习顺序
        lines.append("## 一、当前欠缺能力及优先学习顺序\n")
        lines.append("| 优先级 | 能力 | 重要程度 | 预估时间 |")
        lines.append("|--------|------|----------|----------|")

        must_fix = [g for g in gaps if g.get("importance") == "必须补"]
        suggest = [g for g in gaps if g.get("importance") == "建议补"]
        optional = [g for g in gaps if g.get("importance") == "可选补"]

        all_gaps = must_fix + suggest + optional
        for i, gap in enumerate(all_gaps, 1):
            lines.append(
                f"| {i} | {gap.get('ability', '')} | "
                f"{gap.get('importance', '')} | "
                f"{gap.get('estimated_time', '')} |"
            )
        lines.append("")

        # 二、7天快速补强计划
        lines.append("## 二、7 天快速补强计划\n")

        if must_fix:
            main_gap = must_fix[0]
            skill = main_gap.get("ability", "")

            lines.append(f"### 核心目标：{skill} 从入门到能独立完成日常任务\n")

            daily_plan = [
                (f"Day 1-2：{skill}基础", f"学习{skill}的基础语法和核心概念，跟着教程完成5个基础练习"),
                (f"Day 3-4：{skill}实战", f"在练习平台完成10道练习题，重点掌握常用的业务场景"),
                (f"Day 5：综合练习", f"用自己的数据或公开数据集，完成一个完整的分析流程"),
                (f"Day 6：查漏补缺", f"回顾薄弱环节，重点突破之前卡壳的题型"),
                (f"Day 7：复习+总结", f"整理学习笔记，梳理常见业务问题的解决方案模板"),
            ]

            for title, content in daily_plan:
                lines.append(f"### {title}")
                lines.append(f"{content}\n")
        else:
            lines.append("当前无需紧急补强的核心技能。建议利用这7天时间：\n")
            lines.append("- Day 1-3：学习1个对目标岗位有帮助的新工具/概念")
            lines.append("- Day 4-6：完成1个小型实战项目")
            lines.append("- Day 7：更新简历和作品集\n")

        # 三、30天系统提升计划
        lines.append("## 三、30 天系统提升计划\n")

        weeks = [
            ("第1周（基础期）", f"目标：掌握{all_gaps[0]['ability'] if all_gaps else '核心技能'}的基础操作\n- 具体内容：每天投入2-3小时学习基础知识和练习\n- 检验标准：能独立完成基础任务"),
            ("第2周（进阶期）", "目标：能够处理较复杂的业务场景\n- 具体内容：进阶练习+案例分析\n- 检验标准：完成3个真实业务场景的练习"),
            ("第3周（实战期）", "目标：完成1个完整的项目作品\n- 具体内容：从数据采集到成果展示的全流程\n- 检验标准：产出一个可对外展示的作品"),
            ("第4周（巩固准备期）", "目标：查漏补缺+面试准备\n- 具体内容：复习薄弱点+模拟面试\n- 检验标准：能流利回答相关面试问题"),
        ]

        for title, content in weeks:
            lines.append(f"### {title}")
            lines.append(f"{content}\n")

        # 四、推荐资源
        lines.append("## 四、推荐学习资源\n")
        lines.append("### 免费资源")
        lines.append("- LeetCode / 牛客网：刷题练习")
        lines.append("- B站 / YouTube：搜索相关教程")
        lines.append("- 官方文档：最权威的学习资料")
        lines.append("")

        lines.append("### 推荐 AI 工具")
        lines.append("- ChatGPT/Claude：学习问答、代码纠错、概念解释")
        lines.append("- GitHub Copilot：智能代码补全")
        lines.append("")

        lines.append("### 推荐练手项目")
        lines.append("- 用公开数据集做一个完整的分析报告")
        lines.append("- 搭建一个自动化的数据看板")
        lines.append("- 参与 Kaggle 的入门级比赛")
        lines.append("")

        # 五、面试核心概念
        lines.append("## 五、面试前必须掌握的核心概念\n")
        lines.append("| 概念 | 一句话解释 | 面试可能问法 |")
        lines.append("|------|-----------|-------------|")
        lines.append("| 核心技能原理 | 能解释基本工作原理 | 你能简单介绍一下X是如何工作的吗？ |")
        lines.append("| 常见业务场景 | 知道典型应用场景 | 在什么情况下你会用X而不是Y？ |")
        lines.append("| 最佳实践 | 了解行业通用做法 | 你做X的时候一般遵循什么原则？ |")
        lines.append("")

        # 六、作品集方向
        lines.append("## 六、可以快速产出的作品集方向\n")
        lines.append("### 方向1：数据分析项目")
        lines.append("- 用公开数据集完成从数据清洗到可视化的完整分析")
        lines.append("- 产出形式：GitHub 仓库 + Jupyter Notebook + 分析报告")
        lines.append("- 时间预估：1-2周")
        lines.append("")

        lines.append("### 方向2：自动化工具")
        lines.append("- 开发一个解决实际小问题的自动化脚本/工具")
        lines.append("- 产出形式：GitHub 仓库 + 使用文档")
        lines.append("- 时间预估：1周")
        lines.append("")

        # 七、成长成果
        lines.append("## 七、适合写进下一版简历的成长成果\n")
        for i, gap in enumerate(all_gaps[:3], 1):
            lines.append(f"- [ ] 掌握了 {gap.get('ability', '')}，可以标注为「熟悉」水平")
        lines.append("- [ ] 完成了1个可对外展示的数据分析/技术项目")
        lines.append("- [ ] 在练习平台完成了30+道练习题")
        lines.append("")

        return "\n".join(lines)
