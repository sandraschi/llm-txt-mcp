import asyncio
import sys
from pathlib import Path

# Add llm-txt-mcp src to path
llm_txt_root = Path(r"D:\Dev\repos\llm-txt-mcp")
sys.path.append(str(llm_txt_root / "src"))

from llm_txt_mcp.models.service import LLMTextService


async def mass_generate(root_dir: str):
    service = LLMTextService()
    root = Path(root_dir)
    repos = [d for d in root.iterdir() if d.is_dir() and (d / ".git").exists()]

    print(f"Found {len(repos)} repositories in {root_dir}")

    for repo in repos:
        print(f"Processing {repo.name}...")
        try:
            result = await service.generate_project_llms_txt(project_path=str(repo), scan_depth=3)
            print(f"  [OK] Generated: {result.get('llms_txt_path')}")
        except Exception as e:
            print(f"  [ERROR] Failed {repo.name}: {e}")


if __name__ == "__main__":
    asyncio.run(mass_generate(r"D:\Dev\repos"))
