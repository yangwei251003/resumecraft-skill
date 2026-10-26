"""
面试教练 —— 生成面试准备建议

输出:
- 面试官可能关注的问题预测
- 针对待补强项的解释话术
- 回答思路建议
"""

from typing import Dict, List


class InterviewCoach:
    """面试辅导模块"""

    def generate(self, profile: Dict, matching_result: Dict) -> str:
        """生成面试准备建议"""
        lines = []
        lines.append("# 面试准备建议\n")

        # 一、可能的问题预测
        lines.append("## 一、面试官可能关注的问题\n")

        # A. 基于简历内容
        lines.append("### A. 针对简历内容的必问题\n")
        internships = profile.get("internships_jobs", [])
        projects = profile.get("projects", [])

        for i, job in enumerate(internships[:2], 1):
            company = job.get("company", "该公司")
            role = job.get("role", "该岗位")
            lines.append(f"**Q{i}：你在 {company} 做 {role} 期间的经历，能详细讲讲吗？**\n")
            lines.append("建议回答要点：")
            lines.append("1. 先讲背景（为什么做这件事）")
            lines.append("2. 再说过程（具体做了什么，用了什么方法）")
            lines.append("3. 然后说结果（带来了什么影响，有数据说话）")
            lines.append("4. 最后说收获（学会了什么，对后续有什么帮助）")
            lines.append("")
            lines.append("⚠️ 注意事项：")
            lines.append("- 不要只复述简历上已有的内容")
            lines.append("- 用STAR法则组织回答")
            lines.append("- 准备好「如果重新做会怎么改进」的回答\n")

        for i, proj in enumerate(projects[:2], len(internships) + 1):
            proj_name = proj.get("name", "该项目")
            lines.append(f"**Q{i}：能介绍一下你做的「{proj_name}」吗？你遇到的最大挑战是什么？**\n")
            lines.append("建议回答：先说项目背景和目标→再说自己具体负责什么→然后说遇到了什么困难→怎么解决的→最后说学到了什么\n")

        # B. 基于待补强项
        gaps = matching_result.get("gaps", [])
        must_fix = [g for g in gaps if g.get("importance") == "必须补"]

        if must_fix:
            lines.append("### B. 针对欠缺能力的提问（重点准备！）\n")
            for gap in must_fix:
                skill = gap.get("ability", "")
                lines.append(f"**可能的提问**：「你对{skill}的掌握程度怎么样？」\n")
                lines.append("**建议回答框架**：\n")
                lines.append(f"「我目前的{skill}水平处于学习阶段。基础操作可以独立完成，")
                lines.append(f"我正在通过[具体学习方式]系统学习，目前已完成了[具体进度]。")
                lines.append(f"我预计在[时间]内可以达到独立完成日常任务的水平。")
                lines.append(f"另外我在[相邻能力]方面有实践经验，可以弥补一些{skill}暂时覆盖不到的场景。」\n")
                lines.append("**关键策略**：")
                lines.append("- 不回避、不假装")
                lines.append("- 明确当前水平和学习进度")
                lines.append("- 给出弥补方案（时间+方法+当前成果）")
                lines.append("- 展示相邻能力作为缓冲\n")

        # C. 行为面试
        lines.append("### C. 常见行为面试题\n")
        behavioral = [
            ("举一个你解决过的难题", "用STAR法讲一个真实案例，重点展示你的思考过程和行动"),
            ("说一次你与团队合作的经历", "选一个体现协作的案例，说明你的角色和贡献"),
            ("你有没有失败的经历，从中学到了什么？", "选一个真实的失败案例，重点放在「学到了什么」和「后续怎么改进的」"),
            ("你如何快速学习一个新技能？", "用实际例子说明你的学习方法和效率"),
            ("你为什么觉得自己适合这个岗位？", "用匹配分析中的直接匹配项来回答，数据+事实支撑"),
        ]

        for q, tips in behavioral:
            lines.append(f"**{q}**")
            lines.append(f"→ {tips}\n")

        # 二、自我介绍模板
        lines.append("## 二、自我介绍模板（1-2分钟）\n")
        basic = profile.get("basic_info", {})
        education = profile.get("education", [])
        edu_str = f"{education[0].get('school', '')} {education[0].get('major', '')}" if education else "某高校相关专业"

        lines.append("【框架】\n")
        lines.append(f"「面试官你好，我是{basic.get('name', '')}，{edu_str}{education[0].get('degree', '') if education else ''}。")
        lines.append("")

        # 最相关的经历
        if internships:
            job = internships[0]
            lines.append(f"我曾在{job.get('company', '某公司')}做过{job.get('role', '')}，"
                        f"期间{job.get('quantified_impact', '完成了相关工作')}。")
        elif projects:
            proj = projects[0]
            lines.append(f"我独立完成过{proj.get('name', '')}，{proj.get('quantified_metrics', '取得了不错的成果')}。")
        lines.append("")

        lines.append("我对这个岗位的理解是[简述岗位核心职责]，我的经历和能力与岗位要求比较匹配，")
        lines.append("特别是[最匹配的2-3项能力]方面。目前我正在[学习/提升的方向]，希望能在贵公司获得成长机会。」\n")

        # 三、反问环节
        lines.append("## 三、反问环节建议\n")
        lines.append("可以向面试官提的好问题：")
        lines.append("1. 这个岗位的日常工作大概是怎样的？典型的一天会做什么？")
        lines.append("2. 团队目前最需要解决的数据/业务问题是什么？")
        lines.append("3. 公司对这个岗位的新人有什么期望和培养计划？")
        lines.append("4. 团队的技术栈和协作方式是怎样的？")
        lines.append("5. 这个岗位的晋升路径是怎样的？")
        lines.append("")
        lines.append("⚠️ 避免在技术面问薪资福利（HR面再问）\n")

        # 四、面试前检查清单
        lines.append("## 四、面试前检查清单\n")
        checklist = [
            "复习简历上每一段经历，确保每句话都能展开讲3分钟",
            "准备3个STAR故事（技术难题、团队合作、快速学习各一个）",
            "研究公司业务和岗位背景（至少花1小时）",
            "准备对待补强项的应对话术",
            "练习自我介绍（录下来听听，控制在2分钟内）",
            "准备3-5个反问环节的问题",
            "确认面试时间和形式（线上/线下、视频工具）",
            "测试设备（视频面试需要！摄像头、麦克风、网络）",
            "准备好纸笔记录面试中的关键信息",
        ]
        for item in checklist:
            lines.append(f"- [ ] {item}")

        return "\n".join(lines)
