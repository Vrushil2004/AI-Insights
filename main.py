import asyncio
from tools import *
from pdf_genrator import render_pdf_report

async def main():
    topic = input("Enter topic:")
    news, metrics, risks = await asyncio.gather(
        scrape_news_articles(topic),
		get_market_benchmarks(topic),
		check_compliance_risks(topic))
		
    report = await synthesize_insights(topic, news, metrics, risks)
    print(render_pdf_report(report, "report.pdf"))
    print("Report generated sucessfully")
	
if __name__ == "__main__":
    asyncio.run(main())