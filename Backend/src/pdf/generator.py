"""
PDF Report Generation Service.
Generates research intelligence documents containing session Q&As, citations,
referenced sources, and verification timestamps.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.units import inch
from src.models.domain import ChatMessage, ChatSession, Source
from src.config.settings import settings
from src.utils.logger import logger


class PDFReportGenerator:
    def __init__(self, export_dir: str = settings.PDF_EXPORT_DIR):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)

    def generate_research_report(
        self,
        session: ChatSession,
        sources: List[Dict[str, Any]],
        report_title: str = "Research Assistant - Intelligence Report"
    ) -> str:
        """
        Build a PDF report from a chat session and referenced sources.
        Returns the absolute file path of the generated PDF.
        """
        filename = f"report_{session.session_id}_{int(datetime.utcnow().timestamp())}.pdf"
        filepath = os.path.join(self.export_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Modern Styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=15
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=12,
            spaceAfter=6
        )

        question_style = ParagraphStyle(
            "QuestionStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#1E40AF"),
            spaceBefore=8,
            spaceAfter=4
        )

        answer_style = ParagraphStyle(
            "AnswerStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=8
        )

        citation_style = ParagraphStyle(
            "CitationStyle",
            parent=styles["Italic"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#475569"),
            leftIndent=10
        )

        story = []

        # 1. Header & Metadata
        story.append(Paragraph(report_title, title_style))
        gen_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        meta_text = (
            f"<b>Session ID:</b> {session.session_id} | "
            f"<b>Generated:</b> {gen_time} | "
            f"<b>Total Q&As:</b> {len([m for m in session.messages if m.role == 'user'])}"
        )
        story.append(Paragraph(meta_text, subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E1"), spaceAfter=15))

        # 2. Executive Summary Table of Sources
        if sources:
            story.append(Paragraph("1. Referenced Sources in Knowledge Base", section_heading))
            table_data = [["#", "Title", "Domain", "Source URL"]]
            for i, s in enumerate(sources, 1):
                title = (s.get("title") or "Document")[:35]
                dom = s.get("domain") or ""
                url = (s.get("url") or "")[:45]
                table_data.append([str(i), title, dom, url])

            table = Table(table_data, colWidths=[0.4 * inch, 2.3 * inch, 1.3 * inch, 3.2 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
            ]))
            story.append(table)
            story.append(Spacer(1, 15))

        # 3. Questions, Grounded Answers & Citations
        story.append(Paragraph("2. Research Q&A Transcript with Citations", section_heading))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=10))

        # Group messages by Q&A pairs
        user_msgs = [m for m in session.messages if m.role == "user"]
        assistant_msgs = [m for m in session.messages if m.role == "assistant"]

        for idx in range(len(user_msgs)):
            u_msg = user_msgs[idx]
            a_msg = assistant_msgs[idx] if idx < len(assistant_msgs) else None

            qa_elements = []
            qa_elements.append(Paragraph(f"Q{idx + 1}: {u_msg.content}", question_style))

            if a_msg:
                # Format model badge
                model_tag = f"<i>(Answered by {a_msg.model_used or 'RAG Engine'})</i>"
                qa_elements.append(Paragraph(f"{a_msg.content} {model_tag}", answer_style))

                # Citations
                if a_msg.citations:
                    qa_elements.append(Paragraph("<b>Citations:</b>", ParagraphStyle("CitHead", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold", textColor=colors.HexColor("#334155"))))
                    for cit in a_msg.citations:
                        cit_obj = cit if isinstance(cit, dict) else (cit.__dict__ if hasattr(cit, "__dict__") else {})
                        c_idx = cit_obj.get("citation_index", 1)
                        c_title = cit_obj.get("title", "Source")
                        c_url = cit_obj.get("url", "")
                        c_snip = cit_obj.get("snippet", "")
                        snip_str = f' - "{c_snip[:120]}..."' if c_snip else ""
                        qa_elements.append(Paragraph(f"[Source {c_idx}] {c_title} ({c_url}){snip_str}", citation_style))
            else:
                qa_elements.append(Paragraph("<i>No answer recorded.</i>", answer_style))

            qa_elements.append(Spacer(1, 10))
            story.append(KeepTogether(qa_elements))

        # Build PDF document
        doc.build(story)
        logger.info(f"Generated PDF Research Report at: {filepath}")
        return filepath
