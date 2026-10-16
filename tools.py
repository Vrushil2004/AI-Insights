
import asyncio
import os
import json
import requests
import xml.etree.ElementTree as ET
from pydantic import BaseModel
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


# Structured report schema
class Report(BaseModel):
    topic: str
    summary: str
    findings: list[str]
    metrics: dict
    risks: list[str]
    recommendations: list[str]
    sources: list[str]


# 1. Fetch recent news
async def scrape_news_articles(topic):
    if not topic.strip():
        raise ValueError("Topic cannot be empty.")

    def fetch():
        response = requests.get(
            "https://news.google.com/rss/search",
            params={"q": topic, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
            timeout=15,
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)

        return [
            {
                "title": item.findtext("title", ""),
                "url": item.findtext("link", ""),
                "published": item.findtext("pubDate", ""),
                "source": (
                    item.find("source").text
                    if item.find("source") is not None
                    and item.find("source").text
                    else "Unknown"
                ),
            }
            for item in root.findall(".//item")[:5]
        ]

    return await asyncio.to_thread(fetch)


# Shared MCP caller
async def call_mcp(url, tool, topic):
    async with streamable_http_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, {"topic": topic})

            if result.isError:
                raise RuntimeError(f"MCP tool failed: {tool}")

            data = getattr(result, "structuredContent", None)
            if data is not None:
                return data

            if result.content and hasattr(result.content[0], "text"):
                return json.loads(result.content[0].text)

            raise ValueError(f"MCP tool returned no usable data: {tool}")


# 2. Market benchmarks through MCP or labelled demo data
async def get_market_benchmarks(topic):
    url = os.getenv("MCP_MARKET_URL")

    if url:
        return await call_mcp(
            url,
            os.getenv("MCP_MARKET_TOOL", "get_market_benchmarks"),
            topic,
        )

    return {
        "data_status": "DEMO DATA - MCP not connected",
        "topic": topic,
        "adoption": "Unavailable",
        "sentiment": "Unknown",
        "cost_index": None,
    }


# 3. Compliance risks through MCP or labelled demo data
async def check_compliance_risks(topic):
    url = os.getenv("MCP_COMPLIANCE_URL")

    if url:
        return await call_mcp(
            url,
            os.getenv("MCP_COMPLIANCE_TOOL", "check_compliance_risks"),
            topic,
        )

    return {
        "data_status": "DEMO DATA - MCP not connected",
        "risks": [
            "Live compliance data is unavailable; review is required."
        ],
        "recommendations": [
            "Verify applicable regulations with authoritative sources."
        ],
    }


# 4. Python-based structured synthesis (no LLM required)
async def synthesize_insights(topic, news, metrics, compliance):
    findings = [
        article["title"]
        for article in news
        if article.get("title")
    ]

    summary = (
        f"Retrieved {len(findings)} news articles about '{topic}'. "
        "Review the findings with the available market and compliance data."
        if findings
        else f"No news articles were retrieved for '{topic}'."
    )

    if metrics.get("data_status", "").startswith("DEMO"):
        summary += " Market benchmarks are demo data, not verified metrics."

    if compliance.get("data_status", "").startswith("DEMO"):
        summary += " Compliance results are demo data, not a live assessment."

    report = Report(
        topic=topic,
        summary=summary,
        findings=findings,
        metrics=metrics,
        risks=compliance.get("risks", []),
        recommendations=compliance.get("recommendations", []),
        sources=[
            article["url"]
            for article in news
            if article.get("url")
        ],
    )

    return report.model_dump()


