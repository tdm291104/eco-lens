"""
SkillRegistry - nơi đăng ký và tra cứu skill theo tên.

- register(skill): thêm một Skill instance vào registry
- get(name): trả về Skill instance theo tên, lỗi nếu không tồn tại
- list_skills(): trả về danh sách tất cả skill đã đăng ký (cho dashboard/debug)

Thêm skill mới = tạo class mới implement Skill + gọi register(),
không cần sửa Orchestrator hay Router.
"""

from app.harness.skill import Skill


class SkillRegistry:
    """Đăng ký và tra cứu skill theo tên."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Đăng ký một skill. Lỗi nếu tên skill đã tồn tại."""
        if not skill.name:
            raise ValueError("Skill phải có 'name' khác rỗng")
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' đã được đăng ký")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        """Trả về Skill instance theo tên. Lỗi nếu không tồn tại."""
        try:
            return self._skills[name]
        except KeyError:
            raise KeyError(f"Skill '{name}' không tồn tại trong registry") from None

    def has(self, name: str) -> bool:
        return name in self._skills

    def list_skills(self) -> list[dict[str, str]]:
        """Danh sách {name, description} của mọi skill đã đăng ký."""
        return [
            {"name": skill.name, "description": skill.description}
            for skill in self._skills.values()
        ]
