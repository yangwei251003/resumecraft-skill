"""
状态管理器 —— 维护四阶段状态机，执行状态流转规则

状态流转:
    collecting → self_check → job_matching → generating
    任意阶段 → collecting（更新知识库时）
    job_matching → generating（匹配完成后）
"""

from typing import Optional
import json


class StateManager:
    """四阶段状态机管理器"""

    VALID_STAGES = ["collecting", "self_check", "job_matching", "generating"]

    def __init__(self):
        self._stage = "collecting"
        self._profile_loaded = False
        self._self_check_passed = False
        self._job_provided = False
        self._matching_complete = False

    def get_stage(self) -> str:
        """获取当前阶段"""
        return self._stage

    def set_stage(self, stage: str) -> None:
        """手动设置阶段（需验证合法性）"""
        if stage not in self.VALID_STAGES:
            raise ValueError(f"无效阶段: {stage}，有效值: {self.VALID_STAGES}")
        self._stage = stage

    def set_profile_loaded(self) -> None:
        """标记知识库已加载"""
        self._profile_loaded = True
        # 判断知识库是否完整
        if self._profile_loaded and self._self_check_passed:
            if self._job_provided:
                self._stage = "job_matching"
            else:
                self._stage = "self_check"
        elif self._profile_loaded:
            self._stage = "self_check"

    def can_advance(self) -> bool:
        """判断当前阶段是否可以推进"""
        if self._stage == "collecting":
            return self._profile_loaded and self._self_check_passed
        elif self._stage == "self_check":
            return self._self_check_passed and self._job_provided
        elif self._stage == "job_matching":
            return self._matching_complete
        elif self._stage == "generating":
            return False  # 已到达终点
        return False

    def advance(self) -> Optional[str]:
        """推进到下一阶段，返回新阶段名"""
        order = self.VALID_STAGES
        current_idx = order.index(self._stage)
        if current_idx < len(order) - 1:
            self._stage = order[current_idx + 1]
            return self._stage
        return None

    def force_advance(self, target_stage: str) -> str:
        """强制跳转到指定阶段（用于降级例外）"""
        if target_stage not in self.VALID_STAGES:
            raise ValueError(f"无效阶段: {target_stage}")
        self._stage = target_stage
        return self._stage

    def rollback_to_collecting(self) -> str:
        """回退到收集阶段（用户更新知识库时）"""
        self._stage = "collecting"
        self._self_check_passed = False
        self._job_provided = False
        self._matching_complete = False
        return self._stage

    def set_self_check_result(self, passed: bool) -> None:
        """设置自检结果"""
        self._self_check_passed = passed
        if passed:
            if self._job_provided:
                self._stage = "job_matching"
            else:
                self._stage = "self_check"
        else:
            self._stage = "collecting"

    def set_job_provided(self) -> None:
        """标记用户已提供岗位信息"""
        self._job_provided = True
        if self._self_check_passed:
            self._stage = "job_matching"

    def set_matching_complete(self) -> None:
        """标记匹配分析完成"""
        self._matching_complete = True
        self._stage = "generating"

    def is_degraded_mode(self) -> bool:
        """判断是否处于降级模式（跳过了阶段）"""
        order = self.VALID_STAGES
        current_idx = order.index(self._stage)
        # 如果在 generating 但前面的阶段未完成 = 降级模式
        if self._stage == "generating":
            return not (self._profile_loaded and self._self_check_passed and self._matching_complete)
        return False

    def to_dict(self) -> dict:
        """导出状态字典"""
        return {
            "stage": self._stage,
            "profile_loaded": self._profile_loaded,
            "self_check_passed": self._self_check_passed,
            "job_provided": self._job_provided,
            "matching_complete": self._matching_complete,
        }

    def from_dict(self, state: dict) -> None:
        """从字典恢复状态"""
        self._stage = state.get("stage", "collecting")
        self._profile_loaded = state.get("profile_loaded", False)
        self._self_check_passed = state.get("self_check_passed", False)
        self._job_provided = state.get("job_provided", False)
        self._matching_complete = state.get("matching_complete", False)
