"""
岗位研究员 —— 分析岗位真实技能要求、行业背景、客观利弊

输出 6.3 节的岗位客观评价内容
"""

from typing import Dict


class JobResearcher:
    """岗位研究分析模块"""

    def analyze(self, job_data: Dict) -> Dict:
        """分析岗位客观利弊"""
        title = job_data.get("job_info", {}).get("title", "未知岗位")
        industry = job_data.get("job_info", {}).get("industry", "未知行业")

        return {
            "pros_cons": self._analyze_pros_cons(title),
            "growth_potential": self._analyze_growth(title),
            "workload": self._analyze_workload(title),
            "ai_risk": self._analyze_ai_risk(title),
            "newcomer_friendliness": self._analyze_newcomer(title),
            "long_term": self._analyze_long_term(title),
            "industry_risk": self._analyze_industry_risk(industry),
        }

    def _analyze_pros_cons(self, title: str) -> Dict:
        """分析岗位优缺点"""
        analysis = {
            "数据分析": {
                "pros": ["入门门槛适中，成长路径清晰", "技能通用性强，可跨行业", "数据驱动决策越来越受重视"],
                "cons": ["初期取数等重复性工作较多", "需要持续学习新工具", "业务理解深度决定天花板"],
            },
            "产品": {
                "pros": ["锻炼综合能力（战略+执行）", "职业发展上限高", "创业转型优势明显"],
                "cons": ["初期杂活多", "需要强大的沟通协调能力", "责任大、压力大"],
            },
            "运营": {
                "pros": ["入门门槛低，转行容易", "快速积累实战经验", "接触业务面广"],
                "cons": ["工作强度大", "初期薪资偏低", "容易被替代感强"],
            },
            "开发": {
                "pros": ["薪资天花板高", "技术壁垒强", "远程工作可能性大"],
                "cons": ["技术更新快需要持续学习", "加班文化普遍", "35岁危机感较强"],
            },
        }

        for key, result in analysis.items():
            if key in title:
                return result

        return {
            "pros": ["积累专业能力", "行业需求稳定"],
            "cons": ["需要持续学习", "竞争激烈"],
        }

    def _analyze_growth(self, title: str) -> str:
        """分析成长空间和薪资"""
        if "数据分析" in title:
            return "成长路径清晰：数据分析师→高级分析师→数据科学家/分析总监。应届8-15K，3-5年经验20-35K，资深可达40K+"
        elif "产品" in title:
            return "成长空间大：产品助理→产品经理→高级PM→产品总监/CPO。应届8-15K，3-5年15-30K，资深30-60K+"
        elif "开发" in title:
            return "技术路线薪资高速增长：初级10-18K，中级20-35K，高级35-60K，架构师60K+"
        return "有持续成长空间，但需要主动学习和项目积累"

    def _analyze_workload(self, title: str) -> str:
        """分析工作强度"""
        if "开发" in title:
            return "强度偏高，项目上线期常需加班，996文化在部分公司存在"
        elif "运营" in title:
            return "强度偏高，活动和内容有时效性要求，大促/热点期压力大"
        elif "数据分析" in title:
            return "强度中等，日常节奏较规律，但月末/季度末报表高峰期压力增大"
        return "工作强度因公司和阶段而异"

    def _analyze_ai_risk(self, title: str) -> str:
        """分析AI替代风险"""
        high_risk = ["基础数据录入", "简单报表制作", "初级翻译", "客服"]
        medium_risk = ["基础数据分析", "初级编程", "简单设计"]
        low_risk = ["战略决策", "复杂业务分析", "高级系统架构", "创意设计"]

        for risk_title in high_risk:
            if risk_title in title:
                return "⚠️ 高风险：该岗位的基础工作容易被AI工具替代，建议向策略分析和业务理解方向发展"

        for risk_title in medium_risk:
            if risk_title in title:
                return "⚠️ 中等风险：部分重复性工作可被AI替代，但业务理解和策略性工作短期内难以替代"

        return "✅ 低风险：需要深度业务理解和人际沟通的工作短期内难以被AI替代"

    def _analyze_newcomer(self, title: str) -> str:
        """分析新人友好度"""
        if "初级" in title or "应届" in title or "实习" in title:
            return "✅ 高：明确面向新人的岗位，有培训体系和 mentor 指导"
        if any(w in title for w in ["数据分析", "运营"]):
            return "✅ 中高：入门相对容易，有清晰的学习路径"
        return "中等：需要一定基础，但有成长空间"

    def _analyze_long_term(self, title: str) -> str:
        """分析是否适合长期发展"""
        if "数据分析" in title:
            return "适合长期发展。数据能力在各行业通用，可向数据科学、AI、产品等方向拓展"
        elif "开发" in title:
            return "适合长期发展但需要持续学习。技术更新快，建议同时积累架构能力和业务理解"
        return "取决于个人规划。建议每2-3年评估一次职业方向"

    def _analyze_industry_risk(self, industry: str) -> str:
        """分析行业风险"""
        if "电商" in industry:
            return "电商行业竞争激烈，中小公司经营压力大，但头部公司稳定性较好。大促期间工作强度显著增加"
        elif "互联网" in industry:
            return "互联网行业增速放缓，部分赛道进入存量竞争。建议关注有稳定盈利模式的公司"
        elif "金融" in industry:
            return "金融科技处于监管趋严阶段，合规成本上升。但金融行业整体稳定性较好"
        return "行业整体风险可控，建议关注公司的商业模式和盈利情况"
