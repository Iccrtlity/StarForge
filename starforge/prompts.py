"""Prompt templates for README generation with different tones."""


class PromptTemplates:
    """Templates for generating different types of README sections."""

    # System prompts for different tones
    SYSTEM_PROMPTS = {
        "viral": """You are an expert at writing engaging, viral README files that make developers excited to try a project. 
Your writing should be:
- Bold and confident
- Include emojis and visual appeal
- Highlight what makes this project unique and cool
- Use compelling language that creates FOMO (fear of missing out)
- Focus on benefits and "wow" factors
- Make it sound like everyone should try this project

Keep responses concise but impactful. Use markdown formatting effectively.""",
        "professional": """You are an expert technical writer creating professional README documentation.
Your writing should be:
- Clear and well-structured
- Focused on accuracy and completeness
- Professional but approachable tone
- Include all necessary technical details
- Well-organized with clear sections
- Easy to navigate and understand
- Suitable for enterprise and academic contexts

Provide thorough, accurate information in well-formatted markdown.""",
        "minimal": """You are an expert at writing concise, minimal README files that get straight to the point.
Your writing should be:
- Brief and to the point
- Only include essential information
- Avoid unnecessary fluff or decoration
- Clear and direct language
- Minimal use of emojis or fancy formatting
- Easy to scan quickly

Focus on clarity and brevity.""",
    }

    # Project summary prompt
    PROJECT_SUMMARY_PROMPT = """Based on the following project information, write a 2-3 sentence summary describing what this project is and does:

Project Name: {name}
Tech Stack: {tech_stack}
Lines of Code: {loc}
File Count: {file_count}
File Types: {file_types}
Purpose: {purpose}

Write a concise, engaging summary in one paragraph."""

    # Readme generation prompt templates
    README_GENERATION_PROMPT = """Generate a professional README.md for a project with these details:

Project Name: {name}
Description: {description}
Tech Stack: {tech_stack}
Purpose: {purpose}

Create a comprehensive README with these sections (in order):
1. **Title and Badge Section**: Include the project title with emojis, and relevant badges (tech stack, license, etc.)
2. **Quick Description**: A brief paragraph about what the project does
3. **Features**: A bulleted list of key features
4. **Tech Stack**: List of technologies used
5. **Installation**: Quick start installation instructions
6. **Usage**: Basic usage examples
7. **Architecture**: Brief description of how the project is structured
8. **Contributing**: Information about how to contribute
9. **License**: License information
10. **Screenshots/Demo Section**: A placeholder section for screenshots

Format the README with proper markdown syntax, including:
- Proper heading levels (#, ##, ###)
- Bullet points and numbering where appropriate
- Code blocks with language specification
- Tables if useful
- Clear section dividers

Make it professional, well-organized, and easy to navigate."""

    # Tech detection prompt
    TECH_SUMMARY_PROMPT = """Analyze this tech stack and project metrics, then provide a brief technical summary:

Tech Stack: {tech_stack}
Languages: {languages}
Frameworks: {frameworks}
Tools: {tools}

Write 2-3 sentences explaining the technical foundation and approach of this project."""

    # Feature generation prompt
    FEATURE_PROMPT = """Based on a project with the following characteristics:

Name: {name}
Purpose: {purpose}
Tech Stack: {tech_stack}

Generate a list of 5-8 key features or capabilities this project likely provides.
Format as a markdown bullet list with brief descriptions."""

    @staticmethod
    def get_system_prompt(tone: str) -> str:
        """Get the system prompt for a specific tone.

        Args:
            tone: Tone name ('viral', 'professional', 'minimal')

        Returns:
            System prompt string

        Raises:
            ValueError: If tone is unknown
        """
        if tone not in PromptTemplates.SYSTEM_PROMPTS:
            raise ValueError(
                f"Unknown tone: {tone}. "
                f"Supported: {', '.join(PromptTemplates.SYSTEM_PROMPTS.keys())}"
            )
        return PromptTemplates.SYSTEM_PROMPTS[tone]

    @staticmethod
    def get_project_summary_prompt(
        name: str, tech_stack: list, loc: int, file_count: int, file_types: dict, purpose: str
    ) -> str:
        """Generate a project summary prompt.

        Args:
            name: Project name
            tech_stack: List of technologies
            loc: Lines of code
            file_count: Number of files
            file_types: Dictionary of file types and counts
            purpose: Project purpose/description

        Returns:
            Formatted prompt string
        """
        tech_str = ", ".join(tech_stack) if tech_stack else "Unknown"
        file_types_str = ", ".join(f"{k} ({v})" for k, v in list(file_types.items())[:5])

        return PromptTemplates.PROJECT_SUMMARY_PROMPT.format(
            name=name,
            tech_stack=tech_str,
            loc=loc,
            file_count=file_count,
            file_types=file_types_str,
            purpose=purpose,
        )

    @staticmethod
    def get_readme_generation_prompt(
        name: str, description: str, tech_stack: list, purpose: str
    ) -> str:
        """Generate a README generation prompt.

        Args:
            name: Project name
            description: Project description
            tech_stack: List of technologies
            purpose: Project purpose

        Returns:
            Formatted prompt string
        """
        tech_str = ", ".join(tech_stack) if tech_stack else "Unknown"

        return PromptTemplates.README_GENERATION_PROMPT.format(
            name=name, description=description, tech_stack=tech_str, purpose=purpose
        )

    @staticmethod
    def get_feature_prompt(name: str, purpose: str, tech_stack: list) -> str:
        """Generate a feature generation prompt.

        Args:
            name: Project name
            purpose: Project purpose
            tech_stack: List of technologies

        Returns:
            Formatted prompt string
        """
        tech_str = ", ".join(tech_stack) if tech_stack else "Unknown"

        return PromptTemplates.FEATURE_PROMPT.format(name=name, purpose=purpose, tech_stack=tech_str)
