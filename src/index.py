"""
ResumeCraft —— 岗位匹配型简历生成智能体
主入口模块

用法:
    python index.py --mode interactive
    python index.py --profile <profile.json> --jd <jd.md>
    python index.py --stage <stage_name>
"""

import json
import os
import sys
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from stateManager import StateManager
from profileCollector import ProfileCollector
from profileSelfChecker import ProfileSelfChecker
from profileAnalyzer import ProfileAnalyzer
from jobParser import JobParser
from jobResearcher import JobResearcher
from matcher import Matcher
from resumeWriter import ResumeWriter
from resumeFormatter import ResumeFormatter
from traceabilityChecker import TraceabilityChecker
from ethicsGuard import EthicsGuard
from learningAdvisor import LearningAdvisor
from interviewCoach import InterviewCoach


class ResumeCraft:
    """ResumeCraft 主控制器 —— 协调各模块按状态机流转"""

    def __init__(self, profile_path=None, jd_path=None, output_dir="./output"):
        self.state_manager = StateManager()
        self.profile_collector = ProfileCollector()
        self.profile_self_checker = ProfileSelfChecker()
        self.profile_analyzer = ProfileAnalyzer()
        self.job_parser = JobParser()
        self.job_researcher = JobResearcher()
        self.matcher = Matcher()
        self.resume_writer = ResumeWriter()
        self.resume_formatter = ResumeFormatter(output_dir=output_dir)
        self.traceability_checker = TraceabilityChecker()
        self.ethics_guard = EthicsGuard()
        self.learning_advisor = LearningAdvisor()
        self.interview_coach = InterviewCoach()

        # Load existing profile if provided
        self.profile = None
        self.job_data = None
        self.matching_result = None

        if profile_path:
            with open(profile_path, "r", encoding="utf-8") as f:
                self.profile = json.load(f)
            self.state_manager.set_profile_loaded()

        if jd_path and self.profile:
            with open(jd_path, "r", encoding="utf-8") as f:
                jd_raw = f.read()
            self.job_data = self.job_parser.parse(jd_raw)

    def run_interactive(self):
        """交互式运行模式"""
        print("=" * 60)
        print("  🎯 ResumeCraft —— 岗位匹配型简历生成智能体")
        print("=" * 60)
        print()
        print("我会引导你完成四个阶段：")
        print("  ① 知识库收集 → ② 完整性自检 → ③ 岗位匹配 → ④ 简历生成")
        print()
        print("随时输入 /help 查看命令，/quit 退出，/skip 跳阶段")
        print("-" * 60)

        while True:
            stage = self.state_manager.get_stage()
            prompt = self._get_stage_prompt(stage)
            user_input = input(f"\n[{stage.upper()}] {prompt}\n> ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                self._handle_command(user_input)
                continue

            # Route to appropriate stage handler
            self._handle_stage_input(stage, user_input)

            # Check if we can advance
            if self.state_manager.can_advance():
                self.state_manager.advance()

    def _get_stage_prompt(self, stage):
        prompts = {
            "collecting": "请提供你的信息（从基本信息开始），或输入 /skip 先出基础版简历：",
            "self_check": "知识库收集完成！正在进行完整性自检...\n输入 /check 执行自检，或发送目标岗位 JD：",
            "job_matching": "请发送目标岗位 JD（文字/链接），或上传 JD 截图：",
            "generating": "匹配分析完成！输入 /generate 生成简历：",
        }
        return prompts.get(stage, "请输入：")

    def _handle_command(self, cmd):
        if cmd == "/quit":
            print("👋 再见！随时回来继续完善简历～")
            sys.exit(0)
        elif cmd == "/help":
            self._print_help()
        elif cmd == "/skip":
            if self.state_manager.get_stage() == "collecting":
                print("⚠️  降级模式：将基于当前已收集的信息生成基础版简历")
                print("以下模块信息不足，可能影响简历质量：")
                missing = self.profile_collector.get_missing_modules()
                for m in missing:
                    print(f"  - {m}")
                self.state_manager.force_advance("generating")
        elif cmd == "/check":
            if self.state_manager.get_stage() == "self_check":
                self._run_self_check()
        elif cmd == "/generate":
            if self.state_manager.get_stage() == "generating":
                self._generate_resume()
        elif cmd == "/status":
            self._print_status()

    def _handle_stage_input(self, stage, user_input):
        if stage == "collecting":
            result = self.profile_collector.process_input(user_input)
            print(result)
        elif stage == "job_matching":
            self.job_data = self.job_parser.parse(user_input)
            print("\n📋 岗位解析完成！")
            print(self.job_parser.format_summary(self.job_data))
            print("\n🔍 开始执行三分组匹配分析...")
            self.matching_result = self.matcher.match(self.profile, self.job_data)
            print(self.matcher.format_result(self.matching_result))
        elif stage == "generating":
            self._generate_resume()

    def _run_self_check(self):
        print("\n🔍 执行完整性自检...")
        results = self.profile_self_checker.check(self.profile)

        all_pass = True
        for item in results:
            status = "✅" if item["pass"] else "❌"
            print(f"  {status} {item['name']}")
            if not item["pass"]:
                all_pass = False
                print(f"      → {item['reason']}")

        if all_pass:
            print("\n🎉 自检全部通过！")
            portrait = self.profile_analyzer.analyze(self.profile)
            print(portrait)
            print("\n💡 请发送目标岗位 JD（文字/链接/截图均可）以进入匹配阶段。")
        else:
            print("\n⚠️  自检未通过，需要补充信息。")
            print("请针对上述 ❌ 项提供更多细节。")

    def _generate_resume(self):
        print("\n📝 生成简历中...")

        # Ethics check
        issues = self.ethics_guard.check(self.profile, self.matching_result)
        if issues:
            print("⚠️  伦理检查发现问题：")
            for issue in issues:
                print(f"  - {issue}")

        # Generate resume content
        resume_content = self.resume_writer.write(self.profile, self.matching_result)

        # Traceability check
        trace_issues = self.traceability_checker.check(resume_content, self.profile)
        if trace_issues:
            print("⚠️  可追溯性检查发现问题：")
            for issue in trace_issues:
                print(f"  - {issue}")
            print("正在自动修正...")
            resume_content = self.traceability_checker.fix(resume_content, self.profile)

        # Format to docx
        docx_path = self.resume_formatter.format(resume_content)
        print(f"\n✅ 简历已生成：{docx_path}")

        # Generate supporting documents
        matching_report = self.matcher.generate_report(self.matching_result)
        learning_path = self.learning_advisor.generate(self.matching_result)
        interview_guide = self.interview_coach.generate(
            self.profile, self.matching_result
        )

        # Save all outputs
        output_dir = Path(docx_path).parent
        with open(output_dir / "匹配分析报告.md", "w", encoding="utf-8") as f:
            f.write(matching_report)
        with open(output_dir / "学习提升路径.md", "w", encoding="utf-8") as f:
            f.write(learning_path)
        with open(output_dir / "面试准备建议.md", "w", encoding="utf-8") as f:
            f.write(interview_guide)

        print(f"📊 匹配分析报告：{output_dir / '匹配分析报告.md'}")
        print(f"📚 学习提升路径：{output_dir / '学习提升路径.md'}")
        print(f"🎤 面试准备建议：{output_dir / '面试准备建议.md'}")

    def _print_help(self):
        print("""
命令列表：
  /help    - 显示帮助
  /quit    - 退出
  /skip    - 跳过当前阶段，先生成基础版简历
  /check   - 执行知识库完整性自检
  /generate- 生成最终简历
  /status  - 查看当前进度

阶段说明：
  collecting   - 知识库收集（逐模块引导）
  self_check   - 完整性自检
  job_matching - 岗位解析与三分组匹配
  generating   - 简历生成与输出
        """)

    def _print_status(self):
        stage = self.state_manager.get_stage()
        progress = {
            "collecting": "📝 阶段一：知识库收集（25%）",
            "self_check": "🔍 阶段二：完整性自检（50%）",
            "job_matching": "🎯 阶段三：岗位解析与匹配（75%）",
            "generating": "✨ 阶段四：简历生成（100%）",
        }
        print(f"\n当前阶段：{progress.get(stage, stage)}")


def main():
    parser = argparse.ArgumentParser(
        description="ResumeCraft —— 岗位匹配型简历生成智能体"
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "batch"],
        default="interactive",
        help="运行模式：interactive（交互式）/ batch（批量处理）",
    )
    parser.add_argument("--profile", help="知识库 JSON 文件路径")
    parser.add_argument("--jd", help="岗位描述文件路径")
    parser.add_argument("--stage", help="从指定阶段开始")
    parser.add_argument("--output", default="./output", help="输出目录")

    args = parser.parse_args()

    app = ResumeCraft(profile_path=args.profile, jd_path=args.jd, output_dir=args.output)

    if args.mode == "interactive":
        app.run_interactive()
    elif args.mode == "batch":
        if not args.profile or not args.jd:
            print("❌ 批量模式需要 --profile 和 --jd 参数")
            sys.exit(1)
        # Batch mode: direct generation
        app.matching_result = app.matcher.match(app.profile, app.job_data)
        app._generate_resume()


if __name__ == "__main__":
    main()
