"""
岗位解析器 —— 解析 JD 文字/链接/截图，提取结构化岗位信息

输出: job_schema.json 格式的结构化数据
"""

from typing import Dict, List
import re


class JobParser:
    """岗位 JD 解析模块"""

    def parse(self, raw_text: str) -> Dict:
        """解析 JD 文本，输出结构化岗位数据"""
        job_data = {
            "job_info": self._extract_job_info(raw_text),
            "core_responsibilities": self._extract_responsibilities(raw_text),
            "requirements": self._extract_requirements(raw_text),
            "ats_keywords": [],
            "must_have_skills": [],
            "nice_to_have_skills": [],
            "real_requirements": "",
            "resume_signals": [],
            "candidate_profile": {"suitable_traits": [], "unsuitable_traits": []},
        }

        # 提取 ATS 关键词
        job_data["ats_keywords"] = self._extract_keywords(raw_text, job_data)

        # 分析必备 vs 加分技能
        must_have, nice_have = self._classify_skills(job_data)
        job_data["must_have_skills"] = must_have
        job_data["nice_to_have_skills"] = nice_have

        # 分析真正看重的能力
        job_data["real_requirements"] = self._analyze_real_requirements(job_data)

        # 分析简历筛选信号
        job_data["resume_signals"] = self._analyze_resume_signals(job_data)

        # 人才画像
        job_data["candidate_profile"] = self._build_candidate_profile(job_data)

        return job_data

    def _extract_job_info(self, text: str) -> Dict:
        """提取岗位基本信息"""
        info = {
            "title": "",
            "company": "",
            "industry": "",
            "department": "",
            "location": "",
            "salary_range": "",
            "experience_required": "",
            "education_required": "",
        }

        # 尝试匹配岗位名称（常见模式）
        title_patterns = [
            r"岗位[名称]?[：:]\s*(.+?)(?:\n|$)",
            r"职位[名称]?[：:]\s*(.+?)(?:\n|$)",
            r"招聘[：:]\s*(.+?)(?:\n|$)",
        ]
        for p in title_patterns:
            match = re.search(p, text)
            if match:
                info["title"] = match.group(1).strip()
                break

        # 匹配公司名
        company_patterns = [
            r"公司[：:]\s*(.+?)(?:\n|$)",
            r"企业[：:]\s*(.+?)(?:\n|$)",
        ]
        for p in company_patterns:
            match = re.search(p, text)
            if match:
                info["company"] = match.group(1).strip()
                break

        # 匹配地点
        loc_match = re.search(r"(?:地点|城市|base)[：:]\s*(.+?)(?:\n|$)", text)
        if loc_match:
            info["location"] = loc_match.group(1).strip()

        # 匹配薪资
        salary_match = re.search(r"(?:薪资|薪酬)[：:]\s*(.+?)(?:\n|$)", text)
        if salary_match:
            info["salary_range"] = salary_match.group(1).strip()

        # 匹配学历
        edu_match = re.search(r"(?:学历|教育)[要求]?[：:]\s*(.+?)(?:\n|$)", text)
        if edu_match:
            info["education_required"] = edu_match.group(1).strip()

        # 匹配经验
        exp_match = re.search(r"(?:经验|年限|工作年限)[要求]?[：:]\s*(.+?)(?:\n|$)", text)
        if exp_match:
            info["experience_required"] = exp_match.group(1).strip()

        return info

    def _extract_responsibilities(self, text: str) -> List[Dict]:
        """提取岗位职责"""
        responsibilities = []

        # 查找职责部分
        duty_section = self._find_section(text, ["岗位职责", "工作职责", "职责描述", "工作内容"])

        if duty_section:
            # 匹配数字编号或bullet point
            lines = [l.strip() for l in duty_section.split("\n") if l.strip()]
            for line in lines:
                # 清理编号
                cleaned = re.sub(r"^[\d\.\-\*\•\s]+", "", line).strip()
                if len(cleaned) > 5:
                    responsibilities.append({
                        "description": cleaned,
                        "type": "核心" if self._is_core_duty(cleaned) else "辅助",
                        "required_ability": self._infer_ability(cleaned),
                        "time_ratio": "",
                    })

        return responsibilities

    def _extract_requirements(self, text: str) -> Dict:
        """提取岗位要求，分为硬性/核心/隐性"""
        hard = []
        core = []
        hidden = []

        req_section = self._find_section(text, ["任职要求", "岗位要求", "职位要求", "要求"])

        if req_section:
            lines = [l.strip() for l in req_section.split("\n") if l.strip()]
            for line in lines:
                cleaned = re.sub(r"^[\d\.\-\*\•\s]+", "", line).strip()
                if len(cleaned) < 3:
                    continue

                if any(w in cleaned for w in ["学历", "本科", "硕士", "博士", "年限", "经验"]):
                    hard.append(cleaned)
                elif any(w in cleaned for w in ["优先", "加分", "plus"]):
                    core.append(cleaned)
                else:
                    core.append(cleaned)

        # 隐性偏好（行业惯例）
        hidden = self._infer_hidden_preferences(text)

        return {
            "hard_requirements": hard,
            "core_abilities": core,
            "hidden_preferences": hidden,
        }

    def _extract_keywords(self, text: str, job_data: Dict) -> List[str]:
        """提取 ATS 高频关键词"""
        # 常见技术关键词
        tech_keywords = [
            "Python", "SQL", "Excel", "Tableau", "Power BI", "R",
            "数据分析", "数据可视化", "机器学习", "统计学", "A/B测试",
            "用户研究", "需求分析", "项目管理", "产品设计",
            "Java", "JavaScript", "React", "Vue", "Node.js",
            "运营", "增长", "留存", "转化",
            "Pandas", "NumPy", "Scikit-learn", "TensorFlow",
        ]

        found = []
        for kw in tech_keywords:
            if kw.lower() in text.lower():
                found.append(kw)

        # 按出现频率排序
        return sorted(found, key=lambda k: text.lower().count(k.lower()), reverse=True)

    def _classify_skills(self, job_data: Dict) -> tuple:
        """分类必备技能和加分技能"""
        must_have = []
        nice_have = []

        keywords = job_data.get("ats_keywords", [])
        text = str(job_data)

        for kw in keywords:
            if any(w in text.lower() for w in ["熟练", "精通", "必须", "要求"]):
                must_have.append(kw)
            elif any(w in text.lower() for w in ["优先", "加分", "了解"]):
                nice_have.append(kw)
            else:
                # 默认前3个为必备
                if len(must_have) < 3:
                    must_have.append(kw)
                else:
                    nice_have.append(kw)

        return must_have, nice_have

    def _analyze_real_requirements(self, job_data: Dict) -> str:
        """分析岗位真正看重的能力"""
        title = job_data.get("job_info", {}).get("title", "该岗位")

        analysis_map = {
            "数据分析": "真正看重的是：(1) 能快速准确地把业务问题翻译成数据查询 (2) 能从不规律的数据中看出规律和异常 (3) 能做出业务方看得懂的图表和报告 (4) 愿意深入理解业务，而不是只做取数工具人",
            "产品": "真正看重的是：(1) 用户洞察和需求挖掘能力 (2) 逻辑清晰的方案设计能力 (3) 跨部门推动落地的执行力 (4) 数据驱动的决策思维",
            "运营": "真正看重的是：(1) 对数据的敏感度和分析能力 (2) 快速试错和迭代的执行力 (3) 内容敏感度和用户心理把握 (4) 跨团队资源协调能力",
            "开发": "真正看重的是：(1) 扎实的计算机基础 (2) 独立解决问题的能力 (3) 代码质量和工程规范 (4) 快速学习新技术栈的能力",
        }

        for key, analysis in analysis_map.items():
            if key in title:
                return analysis

        return f"{title}岗位真正看重的是：(1) 专业基础扎实 (2) 独立解决问题的能力 (3) 快速学习和适应能力 (4) 团队协作和沟通能力"

    def _analyze_resume_signals(self, job_data: Dict) -> List[str]:
        """分析简历筛选的关键信号"""
        signals = ["相关实习/工作经验", "核心技能关键词出现", "量化成果数据"]

        requirements = job_data.get("requirements", {})
        hard = requirements.get("hard_requirements", [])
        core = requirements.get("core_abilities", [])

        if hard:
            signals.insert(0, "学历/年限等硬性条件满足")
        if core:
            signals.append("项目经验与岗位方向匹配")

        return signals

    def _build_candidate_profile(self, job_data: Dict) -> Dict:
        """构建岗位人才画像"""
        title = job_data.get("job_info", {}).get("title", "")

        suitable = [
            "专业背景匹配或相关",
            "有相关工作/项目经验",
            "学习能力强，愿意深入业务",
            "逻辑清晰，表达有条理",
        ]

        unsuitable = [
            "期望纯技术不想碰业务",
            "缺乏主动学习意愿",
            "沟通协作能力较弱",
            "专业完全不相关且无相关经验",
        ]

        return {
            "suitable_traits": suitable,
            "unsuitable_traits": unsuitable,
        }

    def format_summary(self, job_data: Dict) -> str:
        """格式化输出岗位摘要"""
        info = job_data.get("job_info", {})
        lines = []

        if info.get("title"):
            lines.append(f"**岗位**：{info['title']}")
        if info.get("company"):
            lines.append(f"**公司**：{info['company']}")
        if info.get("location"):
            lines.append(f"**地点**：{info['location']}")

        keywords = job_data.get("ats_keywords", [])
        if keywords:
            lines.append(f"**关键词**：{' | '.join(keywords[:8])}")

        responsibilities = job_data.get("core_responsibilities", [])
        if responsibilities:
            lines.append(f"\n**核心职责**（共{len(responsibilities)}条）：")
            for i, r in enumerate(responsibilities[:5], 1):
                lines.append(f"  {i}. {r['description'][:60]}...")

        return "\n".join(lines)

    # ===== 辅助方法 =====

    def _find_section(self, text: str, headers: List[str]) -> str:
        """查找指定标题下的文本内容"""
        for header in headers:
            pattern = rf"{header}[：:]*\s*\n?(.*?)(?=\n\s*(?:{'|'.join(headers)}|#|【|\Z))"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def _is_core_duty(self, duty: str) -> bool:
        """判断是否是核心职责"""
        core_keywords = ["负责", "主导", "独立", "搭建", "设计", "核心", "主要"]
        return any(w in duty for w in core_keywords)

    def _infer_ability(self, duty: str) -> str:
        """从职责描述推断所需能力"""
        ability_map = {
            "数据": "数据处理与分析能力",
            "报表": "数据可视化与报表制作能力",
            "分析": "业务分析能力",
            "产品": "产品思维与需求理解",
            "用户": "用户研究与洞察力",
            "运营": "运营策划与执行能力",
            "开发": "编程与系统设计能力",
            "管理": "项目管理与协调能力",
            "设计": "视觉设计能力",
        }
        for keyword, ability in ability_map.items():
            if keyword in duty:
                return ability
        return "综合能力"

    def _infer_hidden_preferences(self, text: str) -> List[str]:
        """推断隐性偏好"""
        hidden = [
            "能够主动发现和解决问题，而非被动等待任务分配",
            "对业务有好奇心，愿意深入理解行业和用户",
            "能够在压力下保持产出质量和效率",
            "具备跨部门沟通和推进能力",
        ]

        # 根据行业补充
        if any(w in text for w in ["电商", "零售"]):
            hidden.append("有电商大促（双11/618）期间高强度工作的心理准备")
        if any(w in text for w in ["互联网", "科技"]):
            hidden.append("适应快速迭代和变化的工作节奏")

        return hidden
