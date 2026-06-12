"""
Agents package - chứa các Skill implementation, nhóm theo agent chuyên biệt.

build_registry(): tạo một SkillRegistry mới và đăng ký toàn bộ skill của
5 agent (Vision, Classification, Localization, Advisory, Scoring).
"""

from app.agents import advisory_agent, classification_agent, localization_agent, scoring_agent, vision_agent
from app.harness.registry import SkillRegistry


def build_registry() -> SkillRegistry:
    """Tạo SkillRegistry và đăng ký toàn bộ skill của 5 agent."""
    registry = SkillRegistry()
    vision_agent.register(registry)
    classification_agent.register(registry)
    localization_agent.register(registry)
    advisory_agent.register(registry)
    scoring_agent.register(registry)
    return registry
