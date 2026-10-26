"""
用户职业画像分析器 —— 分析用户优势、短板、可迁移能力

输出内容包括:
- 最适合的岗位方向
- 核心优势
- 可迁移能力
- 经历亮点
- 当前素材不足
- 后续更新建议
"""

from typing import Dict


class ProfileAnalyzer:
    """职业画像分析模块"""

    def analyze(self, profile: Dict) -> str:
        """分析用户知识库，生成职业画像"""
        lines = []
        lines.append("\n## 📊 个人职业画像")
        lines.append("")

        # 1. 最适合的岗位方向
        direction = profile.get("basic_info", {}).get("target_direction", "未指定")
        skills = profile.get("skills", [])
        internships = profile.get("internships_jobs", [])
        projects = profile.get("projects", [])

        lines.append("### 🎯 最适合的岗位方向")
        lines.append(f"意向方向：{direction}")
        lines.append("")

        # 根据技能和经验匹配方向
        skill_categories = set(s.get("category", "") for s in skills)
        if "数据分析" in skill_categories:
            lines.append("- ✅ 数据分析/商业分析方向（技能匹配度高）")
        if "编程技术" in skill_categories:
            lines.append("- ✅ 技术/开发方向（具备编程基础）")
        if "设计内容运营" in skill_categories:
            lines.append("- ✅ 运营/内容方向（有相关经验）")

        lines.append("")

        # 2. 核心优势
        lines.append("### 💪 核心优势")
        strengths = profile.get("self_reflection", {}).get("strengths", [])
        for s in strengths[:3]:
            lines.append(f"- {s}")

        # 从技能中提取
        familiar_skills = [s["name"] for s in skills if s.get("level") in ["熟悉", "熟练"]]
        if familiar_skills:
            lines.append(f"- 熟练技能：{'、'.join(familiar_skills[:5])}")

        lines.append("")

        # 3. 可迁移能力
        lines.append("### 🔄 可迁移能力")
        transferable = self._extract_transferable(profile)
        for t in transferable:
            lines.append(f"- {t}")
        lines.append("")

        # 4. 经历亮点
        lines.append("### ⭐ 经历亮点")
        total_experiences = len(internships) + len(projects)
        if internships:
            lines.append(f"- {len(internships)}段实习/工作经历")
        if projects:
            lines.append(f"- {len(projects)}个项目经历")
        lines.append(f"- 共{total_experiences}条可用的经历素材")
        lines.append("")

        # 5. 当前素材不足
        lines.append("### ⚠️ 当前素材不足")
        missing = []
        if not profile.get("core_experiences"):
            missing.append("缺少核心经历描述（最重要的能力展示素材）")
        if not profile.get("certificates_honors"):
            missing.append("缺少证书/荣誉信息")
        if not profile.get("portfolio"):
            missing.append("缺少作品/案例链接（建议补充GitHub或个人作品集）")
        if not missing:
            missing.append("当前素材较为完整，可以在后续使用中持续丰富")

        for m in missing:
            lines.append(f"- {m}")
        lines.append("")

        # 6. 后续更新建议
        lines.append("### 💡 后续更新知识库建议")
        suggestions = []
        if not profile.get("portfolio"):
            suggestions.append("建议整理1-2个可对外展示的作品/项目链接")
        if not any(s.get("level") == "精通" for s in skills):
            suggestions.append("建议识别并重点发展1-2项可以深入精通的技能")
        if not profile.get("internships_jobs"):
            suggestions.append("如果有新的实习/工作经历，记得及时更新")
        for s in suggestions:
            lines.append(f"- {s}")
        lines.append("")

        lines.append("---")
        lines.append("✅ 自检通过！请发送目标岗位 JD（文字/链接/截图均可），我将进入岗位匹配分析阶段。")

        return "\n".join(lines)

    def _extract_transferable(self, profile: Dict) -> list:
        """提取可迁移能力"""
        transferable = set()

        skills = profile.get("skills", [])
        internships = profile.get("internships_jobs", [])
        projects = profile.get("projects", [])

        # 从技能类别推断
        categories = set(s.get("category", "") for s in skills)
        if "数据分析" in categories:
            transferable.add("数据处理与分析能力")
        if "编程技术" in categories:
            transferable.add("编程与自动化能力")
        if "沟通协作" in categories:
            transferable.add("团队协作与沟通能力")

        # 从经历推断
        if internships:
            transferable.add("职场基本素养与执行力")
        if len(projects) >= 2:
            transferable.add("项目管理与独立推进能力")

        # 通用能力
        transferable.add("自学与快速上手新工具的能力")

        return sorted(transferable)
