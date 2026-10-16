
import asyncio
from tools import (
    scrape_news_articles,
    get_market_benchmarks,
    check_compliance_risks,
    synthesize_insights,
)
from pdf_genrator import render_pdf_report


async def main():
    topic = input("Enter topic: ").strip()

    if not topic:
        print("Please enter a topic.")
        return

    try:
        news, metrics, compliance = await asyncio.gather(
            scrape_news_articles(topic),
            get_market_benchmarks(topic),
            check_compliance_risks(topic),
        )

        report = await synthesize_insights(
            topic, news, metrics, compliance
        )

        filename = render_pdf_report(report, "report.pdf")
        print(f"Report generated successfully: {filename}")

    except Exception as e:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
