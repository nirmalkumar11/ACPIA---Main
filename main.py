"""ACPIA CLI runner - same behavior as before, now backed by pipeline.run_pipeline
so the exact same logic also powers api_server.py for the dashboard.
"""

import asyncio

from pipeline import run_pipeline


async def main():
    sample_complaint = (
        "A 12-year-old girl has been missing for three days from Chennai. "
        "Neighbors last saw her near XYZ Street with a man named John."
    )
    result = await run_pipeline(sample_complaint)

    print("\n=== FINAL INVESTIGATION SUMMARY ===\n")
    print(result["final_summary"])
    print(f"\n[Disposition] priority={result['priority']} -> {result['disposition']}")


if __name__ == "__main__":
    asyncio.run(main())
