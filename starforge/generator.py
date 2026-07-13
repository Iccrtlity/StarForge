"""README generator using LLM providers and project scanning."""

from typing import Optional
from datetime import datetime, timezone
from .scanner import ProjectScanner
from .providers import LLMProvider
from .prompts import PromptTemplates


class ReadmeGenerator:
    """Generate professional READMEs using LLM providers and project analysis."""

    def __init__(
        self,
        project_path: str = ".",
        provider: LLMProvider = None,
        tone: str = "professional",
    ):
        """Initialize README generator.

        Args:
            project_path: Path to the project
            provider: LLM provider instance
            tone: Tone for README ('viral', 'professional', 'minimal')

        Raises:
            ValueError: If tone is unsupported or provider is not available
        """
        self.project_path = project_path
        self.provider = provider
        self.tone = tone

        if tone not in PromptTemplates.SYSTEM_PROMPTS:
            raise ValueError(f"Unsupported tone: {tone}")

        if provider and not provider.is_available():
            raise RuntimeError(
                f"LLM provider is not available. "
                "Make sure it's properly configured and running."
            )

        self.scanner = ProjectScanner(project_path)

    def generate(self) -> str:
        """Generate a complete README for the project.

        Returns:
            Generated README content as a string
        """
        # Scan the project
        scan_info = self.scanner.scan()

        # Generate project summary
        if self.provider:
            system_prompt = PromptTemplates.get_system_prompt(self.tone)
            project_summary = self._generate_section(
                "project_summary", scan_info, system_prompt
            )
        else:
            project_summary = self._generate_fallback_summary(scan_info)

        # Build README structure
        readme_parts = []

        # 1. Header
        readme_parts.append(self._generate_header(scan_info, project_summary))

        # 2. Features
        if self.provider:
            features = self._generate_section("features", scan_info, system_prompt)
            readme_parts.append(f"## 🎯 Features\n\n{features}\n")
        else:
            features = self._generate_fallback_features(scan_info)
            readme_parts.append(f"## 🎯 Features\n\n{features}\n")

        # 3. Tech Stack
        readme_parts.append(self._generate_tech_stack(scan_info))

        # 4. Quick Start
        readme_parts.append(self._generate_quick_start(scan_info))

        # 5. Usage
        if self.provider:
            usage = self._generate_section("usage", scan_info, system_prompt)
            readme_parts.append(f"## 📖 Usage\n\n{usage}\n")
        else:
            readme_parts.append(
                """## 📖 Usage

See the [examples](./examples) directory or documentation for detailed usage instructions.
"""
            )

        # 6. Architecture
        readme_parts.append(self._generate_architecture(scan_info))

        # 7. Screenshots placeholder
        readme_parts.append(self._generate_screenshots_section())

        # 8. Contributing
        readme_parts.append(self._generate_contributing_section())

        # 9. License
        readme_parts.append(self._generate_license_section())

        # 10. Footer
        readme_parts.append(self._generate_footer())

        return "".join(readme_parts)

    def _generate_section(self, section_type: str, scan_info: dict, system_prompt: str) -> str:
        """Generate a section using the LLM provider.

        Args:
            section_type: Type of section ('project_summary', 'features', 'usage')
            scan_info: Project scan information
            system_prompt: System prompt for the LLM

        Returns:
            Generated section content
        """
        if section_type == "project_summary":
            prompt = PromptTemplates.get_project_summary_prompt(
                name=scan_info["name"],
                tech_stack=scan_info["tech_stack"],
                loc=scan_info["lines_of_code"],
                file_count=scan_info["file_count"],
                file_types=scan_info["file_types"],
                purpose=scan_info["purpose"],
            )
        elif section_type == "features":
            prompt = PromptTemplates.get_feature_prompt(
                name=scan_info["name"],
                purpose=scan_info["purpose"],
                tech_stack=scan_info["tech_stack"],
            )
        elif section_type == "usage":
            prompt = (
                f"Generate concise usage examples for a {', '.join(scan_info['tech_stack'])} "
                f"project called '{scan_info['name']}'. Include 2-3 practical examples."
            )
        else:
            return ""

        try:
            return self.provider.generate(prompt, system_prompt)
        except Exception:
            # Gracefully handle generation errors by returning placeholder
            return f"<!-- Could not generate {section_type} -->"

    def _generate_header(self, scan_info: dict, description: str) -> str:
        """Generate the README header with title and description.

        Args:
            scan_info: Project scan information
            description: Project description

        Returns:
            Formatted header section
        """
        name = scan_info["name"]
        badges = self._generate_badges(scan_info)

        header = f"""# {name} 🚀

{badges}

{description}

"""
        return header

    def _generate_badges(self, scan_info: dict) -> str:
        """Generate technology badges.

        Args:
            scan_info: Project scan information

        Returns:
            Badge markdown
        """
        tech_stack = scan_info["tech_stack"]

        # Map technologies to badge colors
        badge_colors = {
            "Python": "3776AB",
            "JavaScript": "F7DF1E",
            "TypeScript": "3178C6",
            "Go": "00ADD8",
            "Rust": "CE422B",
            "Java": "007396",
            "React": "61DAFB",
            "Node.js": "339933",
            "Docker": "2496ED",
        }

        badges = []
        for tech in tech_stack[:6]:  # Limit to 6 badges
            color = badge_colors.get(tech, "gray")
            badge = f"![{tech}](https://img.shields.io/badge/{tech}-{color}?style=flat&logo={tech.lower()}&logoColor=white)"
            badges.append(badge)

        return " ".join(badges) if badges else ""

    def _generate_tech_stack(self, scan_info: dict) -> str:
        """Generate tech stack section.

        Args:
            scan_info: Project scan information

        Returns:
            Formatted tech stack section
        """
        tech_stack = scan_info["tech_stack"]

        if not tech_stack:
            tech_section = "- Undetermined"
        else:
            tech_section = "\n".join(f"- {tech}" for tech in tech_stack)

        return f"""## 🛠️ Tech Stack

{tech_section}

"""

    def _generate_quick_start(self, scan_info: dict) -> str:
        """Generate quick start section.

        Args:
            scan_info: Project scan information

        Returns:
            Formatted quick start section
        """
        tech_stack = scan_info["tech_stack"]

        # Generate installation instructions based on tech stack
        install_instructions = []

        if "Python" in tech_stack:
            install_instructions.append(
                """```bash
pip install -r requirements.txt
```"""
            )

        if "Node.js" in tech_stack or "JavaScript" in tech_stack:
            install_instructions.append(
                """```bash
npm install
npm start
```"""
            )

        if not install_instructions:
            install_instructions.append(
                """```bash
# Clone the repository
git clone <repository-url>

# Follow the setup instructions in the documentation
```"""
            )

        install_text = "\n\n".join(install_instructions)

        return f"""## ⚡ Quick Start

### Installation

{install_text}

"""

    def _generate_architecture(self, scan_info: dict) -> str:
        """Generate architecture section.

        Args:
            scan_info: Project scan information

        Returns:
            Formatted architecture section
        """
        return f"""## 🏗️ Architecture

This project is built with {', '.join(scan_info['tech_stack']) if scan_info['tech_stack'] else 'multiple technologies'}.

For detailed architecture documentation, see [ARCHITECTURE.md](./ARCHITECTURE.md).

"""

    def _generate_screenshots_section(self) -> str:
        """Generate screenshots placeholder section.

        Returns:
            Formatted screenshots section
        """
        return """## 📸 Screenshots & Demo

[Add screenshots here to showcase the project]

"""

    def _generate_contributing_section(self) -> str:
        """Generate contributing section.

        Returns:
            Formatted contributing section
        """
        return """## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](./CONTRIBUTING.md) for more details.

"""

    def _generate_license_section(self) -> str:
        """Generate license section.

        Returns:
            Formatted license section
        """
        return """## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

"""

    def _generate_footer(self) -> str:
        """Generate footer section.

        Returns:
            Formatted footer section
        """
        year = datetime.now(timezone.utc).year
        return f"""---

Built with ❤️ | {year}

"""

    def _generate_fallback_summary(self, scan_info: dict) -> str:
        """Generate a fallback summary without LLM.

        Args:
            scan_info: Project scan information

        Returns:
            Simple summary
        """
        purpose = scan_info["purpose"]
        tech_str = (
            ", ".join(scan_info["tech_stack"])
            if scan_info["tech_stack"]
            else "multiple technologies"
        )

        return f"""{purpose}

Built with {tech_str}."""

    def _generate_fallback_features(self, scan_info: dict) -> str:
        """Generate fallback features without LLM.

        Args:
            scan_info: Project scan information

        Returns:
            Basic feature list
        """
        features = [
            "✨ Full-featured implementation",
            "🔧 Easy to configure and extend",
            "📚 Well-documented codebase",
            "🧪 Comprehensive testing",
            "🚀 Production-ready",
        ]

        return "\n".join(f"- {feature}" for feature in features)
