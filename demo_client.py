"""
===============================================================================
Research Assistant with Persistent Memory - Interactive Demonstration & Test Client
===============================================================================

This script demonstrates the full end-to-end capabilities:
1. Health check & Vector database verification
2. Ingestion of documentation URLs
3. Cross-source semantic query execution
4. Verification of citation attribution & hallucination prevention
5. PDF Intelligence Report generation
"""

import sys
import os
import time
import asyncio
import httpx


BASE_URL = "http://127.0.0.1:8000"


def print_banner(text: str):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


async def run_demo():
    print_banner("1. SYSTEM HEALTH CHECK & VECTORSTORE DIAGNOSTICS")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        try:
            resp = await client.get("/health")
            if resp.status_code == 200:
                data = resp.json()["data"]
                print(f"[OK] Backend Status: {data['status']}")
                print(f"[OK] Vectorstore Status: {data['vectorstore_status']}")
                print(f"[OK] Primary LLM: {data['active_primary_llm']}")
                print(f"[OK] Fallback LLMs: {', '.join(data['fallback_llms'])}")
                print(f"[OK] Indexed Sources: {data['indexed_sources_count']}")
                print(f"[OK] Indexed Chunks: {data['indexed_chunks_count']}")
            else:
                print(f"[FAIL] Health check returned status {resp.status_code}")
                return
        except Exception as e:
            print(f"[ERROR] Could not connect to backend at {BASE_URL}. Ensure uvicorn is running: {e}")
            return

        print_banner("2. BATCH URL INGESTION (n8n Webhook / API Ingestion)")
        test_urls = [
            "https://fastapi.tiangolo.com/tutorial/first-steps/",
            "https://docs.pydantic.dev/latest/",
        ]
        print(f"Submitting {len(test_urls)} URLs for scraping, chunking, and embedding...")

        ingest_payload = {
            "urls": test_urls,
            "force_refresh": False
        }
        
        start_ingest = time.perf_counter()
        ingest_resp = await client.post("/api/v1/ingest", json=ingest_payload)
        elapsed_ingest = round(time.perf_counter() - start_ingest, 2)

        if ingest_resp.status_code == 200:
            summary = ingest_resp.json()["data"]
            print(f"[SUCCESS] Ingestion completed in {elapsed_ingest}s")
            print(f" - Indexed: {summary['successful_count']}")
            print(f" - Cached/Duplicate: {summary['duplicate_count']}")
            print(f" - Failed: {summary['failed_count']}")
            for item in summary["results"]:
                print(f"   * [{item['status'].upper()}] '{item['title'][:40]}' | Chunks: {item['chunk_count']} | URL: {item['url']}")
        else:
            print(f"[FAIL] Ingestion error: {ingest_resp.text}")

        print_banner("3. KNOWLEDGE BASE STATISTICS")
        stats_resp = await client.get("/api/v1/sources/statistics")
        if stats_resp.status_code == 200:
            stats = stats_resp.json()["data"]
            print(f"Total Sources: {stats['total_sources']}")
            print(f"Total Chunks: {stats['total_chunks']}")
            print(f"Total Characters: {stats['total_characters']}")
            print("Domain Breakdown:")
            for d in stats["domain_breakdown"]:
                print(f" - {d['domain']}: {d['source_count']} sources, {d['chunk_count']} chunks")

        print_banner("4. GROUNDED QUESTION ANSWERING & CITATION ATTRIBUTION")
        session_id = f"demo_session_{int(time.time())}"
        
        sample_questions = [
            "What is FastAPI and how do you define a first step route?",
            "What is the capital of Mars?",  # Unrelated question to test anti-hallucination rule
        ]

        for q in sample_questions:
            print(f"\n[QUERY]: '{q}'")
            chat_payload = {
                "question": q,
                "session_id": session_id,
                "top_k": 4,
                "similarity_threshold": 0.30
            }
            
            chat_resp = await client.post("/api/v1/chat", json=chat_payload)
            if chat_resp.status_code == 200:
                res = chat_resp.json()["data"]
                print(f"[MODEL USED]: {res['model_used']} (Latency: {res['execution_time_ms']}ms)")
                print(f"[IS GROUNDED]: {res['is_grounded']}")
                print(f"[ANSWER]:\n{res['answer']}")
                
                if res["citations"]:
                    print("\n[RESOLVED CITATIONS]:")
                    for c in res["citations"]:
                        print(f" - [Source {c['citation_index']}] {c['title']} -> {c['url']}")
                else:
                    print("\n[NO CITATIONS] (Grounded Fallback Triggered)")
            else:
                print(f"[FAIL] Chat error: {chat_resp.text}")

        print_banner("5. PDF REPORT GENERATION & EXPORT")
        export_payload = {
            "session_id": session_id,
            "report_title": "Enterprise Research Intelligence Report - Capstone Demo",
            "include_sources_summary": True,
            "include_full_citations": True
        }

        export_resp = await client.post("/api/v1/export/pdf", json=export_payload)
        if export_resp.status_code == 200:
            export_data = export_resp.json()["data"]
            print(f"[SUCCESS] PDF Report Generated!")
            print(f" - File Name: {export_data['file_name']}")
            print(f" - File Size: {export_data['file_size_bytes']} bytes")
            print(f" - Download URL: {BASE_URL}{export_data['download_url']}")
        else:
            print(f"[FAIL] PDF export error: {export_resp.text}")

    print_banner("DEMO COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_demo())
