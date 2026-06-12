"""
Harness package - lớp trung gian định tuyến, chuẩn hóa I/O và logging cho mọi skill.

Re-export các class chính để import gọn:
    from app.harness import Skill, SkillRegistry, SkillRouter, SkillNormalizer, HarnessLogger
"""

from app.harness.logger import HarnessLogger
from app.harness.normalizer import SkillNormalizer
from app.harness.registry import SkillRegistry
from app.harness.router import SkillRouter
from app.harness.skill import Skill

__all__ = [
    "Skill",
    "SkillRegistry",
    "SkillRouter",
    "SkillNormalizer",
    "HarnessLogger",
]
