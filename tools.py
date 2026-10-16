import asyncio
import requests
import xml.etree.ElementTree as ET
from pydantic import BaseModel


class Report(BaseModel):
    topic : str
    summary : str
    findings : list[str]
    metrics : dict
    risks : list[str]
    recommendations : list[str]
    sources : list[str]
    
#1. Fetch recent news

async def scrape_news_articles(topic):
    def fetch():
        r = requests.get(
        "https://news.google.com/rss/search",
        params={"q":topic},
        timeout=10
        )
        r.raise_for_status()
        root = ET.fromstring(r.content)
        return[{
            "title" : i.findtext("title", ""),
            "url" : i.findtext("link", ""),
            "published" : i.findtext("pubDate", ""),
            "soruce" : i.findtext("source", "Unknown")
            }for i in root.findall(".//item")[:5]]
            
    return await asyncio.to_thread(fetch)
    
#2. Internal metrics via MCP

async def get_market_benchmarks(topic):
#Replacing with actual MCP server tool call
    return {"adoption":"unavailable","sentiement":"unknown","cost_index":None}
    
#3. Compliance check with MCP
async def check_compliance_risks(topic):
#Replacing with actual MCP server tool call
    return {"risks":["Compliance review required"], "recommendations":["Verify applicable reagulations"]}


#4. Structured insight synthesis
async def synthesize_insights(topic, news, metrics, compliance):
    report = Report(
        topic = topic,
        summary = f"Collected {len(news)} news articles about {topic}",
        findings = [n["title"] for n in news],
        metrics = metrics,
        risks = compliance.get("risks",[]),
            recommendations = compliance.get("recommendations",[]),
            sources = [n["url"] for n in news if n.get("url")])
    
    return report.model_dump()