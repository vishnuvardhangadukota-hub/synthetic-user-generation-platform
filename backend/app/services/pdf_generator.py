"""
PDF Report Generator
====================
Generates a professional A4 PDF research report using ReportLab.

All data comes from the experiment's saved records — no hardcoding.
Scoring:  validation_score (0–100) = round((overall_score / 10) * 100, 1)
          where overall_score is on the 1–10 scale from UsageScoreReport.
"""
import io
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import KeepTogether

logger = logging.getLogger(__name__)

# ── Palette ────────────────────────────────────────────────────────────────────
PRIMARY       = colors.HexColor("#1A237E")   # deep indigo
ACCENT        = colors.HexColor("#283593")
LIGHT_BG      = colors.HexColor("#E8EAF6")
HIGHLIGHT     = colors.HexColor("#3949AB")
SUCCESS_GREEN = colors.HexColor("#2E7D32")
WARNING_AMBER = colors.HexColor("#E65100")
NEUTRAL_GRAY  = colors.HexColor("#546E7A")
TABLE_HDR_BG  = colors.HexColor("#283593")
TABLE_ALT_BG  = colors.HexColor("#F5F5F5")
WHITE         = colors.white
LIGHT_LINE    = colors.HexColor("#CFD8DC")

# ── Page dimensions ────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
USABLE_W = PAGE_W - 2 * MARGIN


class ReportPDFGenerator:
    """Builds the full research PDF from a dashboard payload dict."""

    def __init__(self, dashboard: Dict[str, Any]):
        self.dashboard = dashboard
        self.experiment = dashboard.get("experiment", {})
        self.cards = dashboard.get("summary_cards", {})
        self.themes = dashboard.get("theme_clusters", [])
        self.sentiment = dashboard.get("sentiment_breakdown", {})
        self.quotes = dashboard.get("key_quotes", [])
        self.validation = dashboard.get("validation_score", {})
        self.styles = self._build_styles()
        self._page_num = 0

    # ── Public API ─────────────────────────────────────────────────────────────
    def generate(self) -> bytes:
        buf = io.BytesIO()
        doc = self._build_doc(buf)
        story = self._build_story()
        doc.build(story)
        return buf.getvalue()

    # ── Document template ──────────────────────────────────────────────────────
    def _build_doc(self, buf: io.BytesIO) -> BaseDocTemplate:
        doc = BaseDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=2.5 * cm,
            bottomMargin=2.2 * cm,
        )
        frame = Frame(
            MARGIN, 2.2 * cm,
            USABLE_W, PAGE_H - 4.7 * cm,
            id="normal"
        )
        template = PageTemplate(id="main", frames=[frame], onPage=self._on_page)
        doc.addPageTemplates([template])
        return doc

    def _on_page(self, canvas, doc):
        """Draw header bar and footer on every page."""
        canvas.saveState()
        p = doc.page

        # ── top colour bar ──
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, PAGE_H - 1.5 * cm, PAGE_W, 1.5 * cm, fill=1, stroke=0)

        # ── header text ──
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 9)
        prod = self.experiment.get("product_name", "Research Report")
        canvas.drawString(MARGIN, PAGE_H - 1.0 * cm, prod)
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.0 * cm, "CONFIDENTIAL")

        # ── footer line ──
        canvas.setStrokeColor(LIGHT_LINE)
        canvas.line(MARGIN, 1.8 * cm, PAGE_W - MARGIN, 1.8 * cm)

        # ── page number ──
        canvas.setFillColor(NEUTRAL_GRAY)
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(PAGE_W / 2, 1.2 * cm, f"Page {p}")

        # ── disclaimer footer ──
        canvas.setFont("Helvetica-Oblique", 7)
        canvas.drawCentredString(
            PAGE_W / 2, 0.6 * cm,
            "Synthetic simulation research — results do not constitute real-world market evidence."
        )
        canvas.restoreState()

    # ── Styles ─────────────────────────────────────────────────────────────────
    def _build_styles(self):
        base = getSampleStyleSheet()
        s = {}

        def add(name, **kwargs):
            s[name] = ParagraphStyle(name, **kwargs)

        add("CoverTitle", fontName="Helvetica-Bold", fontSize=26, textColor=WHITE,
            alignment=TA_CENTER, leading=32, spaceAfter=6)
        add("CoverSubtitle", fontName="Helvetica", fontSize=13, textColor=LIGHT_BG,
            alignment=TA_CENTER, leading=16, spaceAfter=4)
        add("CoverMeta", fontName="Helvetica", fontSize=10, textColor=LIGHT_BG,
            alignment=TA_CENTER, leading=14)

        add("H1", fontName="Helvetica-Bold", fontSize=16, textColor=PRIMARY,
            spaceBefore=14, spaceAfter=6, leading=20)
        add("H2", fontName="Helvetica-Bold", fontSize=13, textColor=ACCENT,
            spaceBefore=10, spaceAfter=4, leading=16)
        add("H3", fontName="Helvetica-Bold", fontSize=11, textColor=HIGHLIGHT,
            spaceBefore=8, spaceAfter=3, leading=13)

        add("Body", fontName="Helvetica", fontSize=9.5, textColor=colors.black,
            leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
        add("BodySmall", fontName="Helvetica", fontSize=8.5, textColor=NEUTRAL_GRAY,
            leading=12, spaceAfter=3)
        add("BulletItem", fontName="Helvetica", fontSize=9, textColor=colors.black,
            leading=13, spaceAfter=3, leftIndent=12, bulletIndent=4)

        add("QuoteText", fontName="Helvetica-Oblique", fontSize=9, textColor=ACCENT,
            leading=13, spaceAfter=2, leftIndent=10, rightIndent=10)
        add("QuoteMeta", fontName="Helvetica", fontSize=8, textColor=NEUTRAL_GRAY,
            leading=11, spaceAfter=6, leftIndent=10)

        add("Disclaimer", fontName="Helvetica-Oblique", fontSize=8, textColor=NEUTRAL_GRAY,
            leading=11, spaceAfter=4, alignment=TA_JUSTIFY)

        add("TblHeader", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE,
            alignment=TA_CENTER, leading=12)
        add("TblCell", fontName="Helvetica", fontSize=8.5, textColor=colors.black,
            leading=11, alignment=TA_LEFT)
        add("TblCellC", fontName="Helvetica", fontSize=8.5, textColor=colors.black,
            leading=11, alignment=TA_CENTER)

        return s

    # ── Story builder ──────────────────────────────────────────────────────────
    def _build_story(self) -> list:
        story = []
        story += self._cover_page()
        story += self._exec_summary()
        story += self._persona_profiles()
        story += self._simulation_methodology()
        story += self._response_highlights()
        story += self._theme_analysis()
        story += self._sentiment_analysis()
        story += self._validation_results()
        story += self._recommendations()
        story += self._limitations_conclusion()
        return story

    # ── Section helpers ────────────────────────────────────────────────────────
    def _s(self, name: str) -> ParagraphStyle:
        return self.styles[name]

    def _hr(self):
        return HRFlowable(width="100%", thickness=1, color=LIGHT_LINE,
                          spaceAfter=6, spaceBefore=4)

    def _section_heading(self, title: str, icon: str = "●") -> list:
        return [
            Spacer(1, 0.3 * cm),
            Paragraph(f"{icon}  {title}", self._s("H1")),
            self._hr(),
        ]

    def _sub_heading(self, title: str) -> list:
        return [Paragraph(title, self._s("H2"))]

    def _bullet(self, text: str) -> Paragraph:
        safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return Paragraph(f"• {safe}", self._s("BulletItem"))

    def _body(self, text: str) -> Paragraph:
        safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return Paragraph(safe, self._s("Body"))

    def _small(self, text: str) -> Paragraph:
        safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return Paragraph(safe, self._s("BodySmall"))

    def _table(self, data, col_widths, style_extra=None) -> Table:
        base_style = [
            ("BACKGROUND", (0, 0), (-1, 0), TABLE_HDR_BG),
            ("TEXTCOLOR",  (0, 0), (-1, 0), WHITE),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, TABLE_ALT_BG]),
            ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",   (0, 1), (-1, -1), 8.5),
            ("GRID",       (0, 0), (-1, -1), 0.4, LIGHT_LINE),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ]
        if style_extra:
            base_style.extend(style_extra)
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle(base_style))
        return t

    # ── 1. Cover Page ──────────────────────────────────────────────────────────
    def _cover_page(self) -> list:
        story = []

        # full-page indigo background block
        cover_bg = Table(
            [[Paragraph("", ParagraphStyle("blank"))]],
            colWidths=[PAGE_W],
            rowHeights=[PAGE_H * 0.55],
        )
        cover_bg.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
            ("TOPPADDING", (0, 0), (-1, -1), 40),
        ]))
        story.append(cover_bg)

        # overlay text inside the block
        story.append(Spacer(1, -PAGE_H * 0.55 + 0.5 * cm))

        exp_name = self.experiment.get("name", "Research Experiment")
        prod_name = self.experiment.get("product_name", "")
        gen_date = datetime.now(timezone.utc).strftime("%B %d, %Y")
        exp_id = self.experiment.get("id", "N/A")

        cover_items = [
            Paragraph("SYNTHETIC USER RESEARCH REPORT", self._s("CoverSubtitle")),
            Spacer(1, 0.4 * cm),
            Paragraph(prod_name or exp_name, self._s("CoverTitle")),
            Spacer(1, 0.4 * cm),
            Paragraph(exp_name, self._s("CoverSubtitle")),
            Spacer(1, 0.8 * cm),
            Paragraph(f"Generated: {gen_date}", self._s("CoverMeta")),
            Paragraph(f"Experiment ID: {exp_id}", self._s("CoverMeta")),
        ]

        cover_tbl = Table([[c] for c in cover_items], colWidths=[PAGE_W - 2 * MARGIN])
        cover_tbl.setStyle(TableStyle([
            ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(cover_tbl)
        story.append(Spacer(1, 0.8 * cm))

        # Metadata summary box
        objectives = self.experiment.get("research_objectives", [])
        obj_text = "; ".join(objectives[:3]) if objectives else "Not specified"
        audience = self.experiment.get("target_audience", "Not specified")

        meta_data = [
            [Paragraph("Target Audience", self._s("TblHeader")),
             Paragraph("Research Objectives", self._s("TblHeader"))],
            [self._body(audience), self._body(obj_text)],
        ]
        story.append(self._table(meta_data, [USABLE_W * 0.35, USABLE_W * 0.65]))
        story.append(PageBreak())
        return story

    # ── 2. Executive Summary ───────────────────────────────────────────────────
    def _exec_summary(self) -> list:
        story = []
        story += self._section_heading("Executive Summary", "📋")

        prod = self.experiment.get("product_name", "the product")
        exp_name = self.experiment.get("name", "this experiment")
        desc = self.experiment.get("product_description", "")
        n_personas = self.cards.get("total_personas", 0)
        n_responses = self.cards.get("total_responses", 0)
        n_themes = self.cards.get("themes_discovered", 0)
        val_score = self.validation.get("score") if self.validation.get("available") else None
        pos_pct = self.cards.get("positive_sentiment_pct")

        story.append(self._body(
            f"This report presents the findings of <b>{exp_name}</b>, a synthetic user research "
            f"study conducted for <b>{prod}</b>. {n_personas} synthetic personas simulated real "
            f"user behaviour, generating {n_responses} total research responses across survey and "
            f"interview modalities. The analysis identified {n_themes} recurring theme(s)."
        ))
        if desc:
            story.append(Spacer(1, 0.2 * cm))
            story.append(self._body(f"<b>Product Overview:</b> {desc[:400]}"))

        story.append(Spacer(1, 0.3 * cm))
        story += self._sub_heading("Key Findings")

        if pos_pct is not None:
            story.append(self._bullet(
                f"Overall sentiment: {pos_pct:.1f}% positive, "
                f"{self.sentiment.get('neutral', {}).get('percentage', 0):.1f}% neutral, "
                f"{self.sentiment.get('negative', {}).get('percentage', 0):.1f}% negative."
            ))
        if val_score is not None:
            story.append(self._bullet(
                f"Product Validation Score: {val_score:.1f}/100 — "
                f"{self.validation.get('would_use_percentage', 0):.1f}% of personas indicated "
                f"they would adopt the product."
            ))
        for theme in self.themes[:3]:
            story.append(self._bullet(
                f"Theme — {theme.get('theme', '')}: {theme.get('description', '')[:120]}"
            ))

        story.append(Spacer(1, 0.2 * cm))
        story.append(self._body(
            "<b>Important Disclaimer:</b> All findings are derived from AI-simulated synthetic "
            "personas and serve as exploratory hypotheses for product development. They do not "
            "constitute real-world market validation or statistical evidence."
        ))
        story.append(PageBreak())
        return story

    # ── 3. Persona Profiles ────────────────────────────────────────────────────
    def _persona_profiles(self) -> list:
        story = []
        story += self._section_heading("Persona Profiles", "👥")

        personas_raw = self.dashboard.get("_personas_raw", [])
        if not personas_raw:
            story.append(self._body("No persona profiles were included in this dashboard snapshot."))
            story.append(PageBreak())
            return story

        for persona in personas_raw:
            name = persona.get("name", "Unknown")
            age = persona.get("age", "?")
            occ = persona.get("occupation", "?")
            loc = persona.get("location", "?")
            traits = persona.get("personality_traits", [])
            patterns = persona.get("behavioral_patterns", [])
            demo = persona.get("demographics", {})
            prefs = persona.get("preferences", {})
            psych = persona.get("psychological_profile", {})

            story.append(Paragraph(f"<b>{name}</b>  •  Age {age}  •  {occ}  •  {loc}", self._s("H3")))

            rows = []
            if demo:
                for k, v in list(demo.items())[:4]:
                    rows.append([Paragraph(str(k).replace("_", " ").title(), self._s("TblHeader")),
                                 Paragraph(str(v)[:80], self._s("TblCell"))])
            if psych:
                for k, v in list(psych.items())[:3]:
                    rows.append([Paragraph(str(k).replace("_", " ").title(), self._s("TblHeader")),
                                 Paragraph(str(v)[:80], self._s("TblCell"))])
            if rows:
                tbl = Table(rows, colWidths=[USABLE_W * 0.3, USABLE_W * 0.7])
                tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
                    ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE",   (0, 0), (-1, -1), 8.5),
                    ("GRID",       (0, 0), (-1, -1), 0.4, LIGHT_LINE),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ]))
                story.append(tbl)

            if traits:
                story.append(self._small(f"Personality: {', '.join(traits[:4])}"))
            if patterns:
                for pat in patterns[:3]:
                    story.append(self._bullet(pat))
            if prefs:
                pref_str = ", ".join(f"{k}: {v}" for k, v in list(prefs.items())[:4])
                story.append(self._small(f"Preferences: {pref_str}"))

            story.append(Spacer(1, 0.3 * cm))

        story.append(PageBreak())
        return story

    # ── 4. Simulation Methodology ──────────────────────────────────────────────
    def _simulation_methodology(self) -> list:
        story = []
        story += self._section_heading("Simulation Methodology", "⚙")

        surveys = self.dashboard.get("surveys", [])
        has_survey = self.cards.get("survey_responses", 0) > 0
        has_interview = self.cards.get("interview_responses", 0) > 0

        if has_survey:
            story.append(Paragraph("Mode 1: Survey Simulation", self._s("H2")))
            story.append(self._body(
                "Each synthetic persona answered the experiment's survey questions independently, "
                "drawing on their persona attributes, psychological profile, and established memory. "
                f"Total survey responses collected: {self.cards.get('survey_responses', 0)}."
            ))
            if surveys:
                story.append(self._small(f"Surveys run: {len(surveys)} — titles: " +
                                         ", ".join(s.get('title', '') for s in surveys[:5])))

        if has_interview:
            story.append(Paragraph("Mode 2: Interview / Conversation Simulation", self._s("H2")))
            story.append(self._body(
                "Interactive interview conversations were conducted with individual personas. "
                "Personas responded to researcher-driven questions while maintaining character "
                "consistency via the persona memory system. "
                f"Total interview turns collected: {self.cards.get('interview_responses', 0)}."
            ))

        story.append(Paragraph("General Constraints", self._s("H2")))
        constraints = [
            f"Total personas: {self.cards.get('total_personas', 0)}",
            f"Total responses: {self.cards.get('total_responses', 0)}",
            "LLM provider: Configurable (OpenAI GPT or deterministic fallback)",
            "All personas are AI-generated; results represent simulated behaviour only.",
        ]
        for c in constraints:
            story.append(self._bullet(c))

        story.append(Spacer(1, 0.3 * cm))
        story.append(self._body(
            "<b>Limitations:</b> Synthetic simulation cannot replicate real user diversity, "
            "cultural nuance, or actual purchasing behaviour. Use findings as directional "
            "hypotheses, not as statistically validated market research."
        ))
        story.append(PageBreak())
        return story

    # ── 5. Response Highlights ─────────────────────────────────────────────────
    def _response_highlights(self) -> list:
        story = []
        story += self._section_heading("Response Highlights", "💬")

        if not self.quotes:
            story.append(self._body("No response data available for this experiment."))
            story.append(PageBreak())
            return story

        for q in self.quotes[:10]:
            name = q.get("persona_name", "Unknown")
            quote = str(q.get("quote", "")).strip()
            src = q.get("source_type", "survey").upper()
            attrs = q.get("persona_attributes", {})
            age = attrs.get("age", "")
            occ = attrs.get("occupation", "")
            if not quote:
                continue

            meta = f"— {name}"
            if age or occ:
                meta += f"  ({occ}, Age {age})" if occ and age else f"  ({age or occ})"
            meta += f"  [{src}]"

            # clip very long quotes
            if len(quote) > 350:
                quote = quote[:347] + "…"

            story.append(KeepTogether([
                Paragraph(f'"{quote}"', self._s("QuoteText")),
                Paragraph(meta, self._s("QuoteMeta")),
            ]))

        story.append(PageBreak())
        return story

    # ── 6. Theme Analysis ──────────────────────────────────────────────────────
    def _theme_analysis(self) -> list:
        story = []
        story += self._section_heading("Theme Analysis", "🔍")

        if not self.themes:
            story.append(self._body(
                "No theme analysis is available. Please generate an insight report "
                "via POST /api/experiments/{id}/insights first."
            ))
            story.append(PageBreak())
            return story

        # Summary table
        tbl_data = [
            [
                Paragraph("Theme", self._s("TblHeader")),
                Paragraph("Description", self._s("TblHeader")),
                Paragraph("Quotes", self._s("TblHeader")),
                Paragraph("Share %", self._s("TblHeader")),
            ]
        ]
        for t in self.themes:
            tbl_data.append([
                Paragraph(str(t.get("theme", ""))[:60], self._s("TblCell")),
                Paragraph(str(t.get("description", ""))[:120], self._s("TblCell")),
                Paragraph(str(t.get("response_count", 0)), self._s("TblCellC")),
                Paragraph(f"{t.get('percentage', 0):.1f}%", self._s("TblCellC")),
            ])
        story.append(self._table(
            tbl_data,
            [USABLE_W * 0.22, USABLE_W * 0.48, USABLE_W * 0.14, USABLE_W * 0.16]
        ))
        story.append(Spacer(1, 0.4 * cm))

        # Per-theme detail
        story += self._sub_heading("Detailed Theme Breakdown")
        for t in self.themes:
            story.append(Paragraph(f"<b>{t.get('theme', '')}</b>", self._s("H3")))
            story.append(self._body(t.get("description", "")))
            for quote in t.get("representative_quotes", [])[:3]:
                story.append(Paragraph(f'"{quote}"', self._s("QuoteText")))

        story.append(PageBreak())
        return story

    # ── 7. Sentiment Analysis ──────────────────────────────────────────────────
    def _sentiment_analysis(self) -> list:
        story = []
        story += self._section_heading("Sentiment Analysis", "📊")

        sent = self.sentiment
        total = sent.get("total", 0)

        if total == 0:
            story.append(self._body("No sentiment data is available for this experiment."))
            story.append(PageBreak())
            return story

        pos = sent.get("positive", {})
        neu = sent.get("neutral", {})
        neg = sent.get("negative", {})

        tbl_data = [
            [
                Paragraph("Sentiment", self._s("TblHeader")),
                Paragraph("Count", self._s("TblHeader")),
                Paragraph("Percentage", self._s("TblHeader")),
                Paragraph("Interpretation", self._s("TblHeader")),
            ],
            [
                Paragraph("✅ Positive", self._s("TblCell")),
                Paragraph(str(pos.get("count", 0)), self._s("TblCellC")),
                Paragraph(f"{pos.get('percentage', 0):.1f}%", self._s("TblCellC")),
                Paragraph("Personas responded favourably to the product.", self._s("TblCell")),
            ],
            [
                Paragraph("⚪ Neutral", self._s("TblCell")),
                Paragraph(str(neu.get("count", 0)), self._s("TblCellC")),
                Paragraph(f"{neu.get('percentage', 0):.1f}%", self._s("TblCellC")),
                Paragraph("Mixed or indifferent responses observed.", self._s("TblCell")),
            ],
            [
                Paragraph("❌ Negative", self._s("TblCell")),
                Paragraph(str(neg.get("count", 0)), self._s("TblCellC")),
                Paragraph(f"{neg.get('percentage', 0):.1f}%", self._s("TblCellC")),
                Paragraph("Concerns or friction points surfaced.", self._s("TblCell")),
            ],
        ]
        story.append(self._table(
            tbl_data,
            [USABLE_W * 0.18, USABLE_W * 0.12, USABLE_W * 0.18, USABLE_W * 0.52]
        ))

        story.append(Spacer(1, 0.4 * cm))

        # Sentiment bar chart
        story += self._sub_heading("Sentiment Distribution (Visual)")
        story += self._sentiment_bar(pos, neu, neg)

        story.append(Spacer(1, 0.3 * cm))
        pos_pct = pos.get("percentage", 0)
        neg_pct = neg.get("percentage", 0)
        if pos_pct >= 60:
            interp = "The majority of personas expressed positive sentiment, indicating strong initial receptivity to the product."
        elif neg_pct >= 50:
            interp = "Negative sentiment predominates, suggesting significant barriers or misalignments with persona needs."
        else:
            interp = "Sentiment is mixed, with no single polarity dominating. This suggests the product addresses some needs but has notable areas for improvement."
        story.append(self._body(interp))

        story.append(PageBreak())
        return story

    def _sentiment_bar(self, pos, neu, neg) -> list:
        """Simple horizontal bar chart using Table cells."""
        total = max(pos.get("count", 0) + neu.get("count", 0) + neg.get("count", 0), 1)
        bar_w = USABLE_W - 4 * cm

        def bar_row(label, count, pct, fill_color):
            fill_w = max((count / total) * bar_w, 0.1)
            gap_w = bar_w - fill_w
            bar_cell = Table(
                [[" ", " "]],
                colWidths=[fill_w, gap_w],
                rowHeights=[14],
            )
            bar_cell.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, 0), fill_color),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#ECEFF1")),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ]))
            return [
                Paragraph(label, self._s("BodySmall")),
                bar_cell,
                Paragraph(f"{pct:.1f}%", self._s("BodySmall")),
            ]

        tbl = Table(
            [
                bar_row("Positive", pos.get("count", 0), pos.get("percentage", 0), SUCCESS_GREEN),
                bar_row("Neutral",  neu.get("count", 0), neu.get("percentage", 0), NEUTRAL_GRAY),
                bar_row("Negative", neg.get("count", 0), neg.get("percentage", 0), colors.HexColor("#C62828")),
            ],
            colWidths=[2.0 * cm, bar_w, 1.8 * cm],
            rowHeights=[20, 20, 20],
        )
        tbl.setStyle(TableStyle([
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",   (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
            ("LEFTPADDING",  (0, 0), (0, -1), 0),
        ]))
        return [tbl]

    # ── 8. Product Validation Results ──────────────────────────────────────────
    def _validation_results(self) -> list:
        story = []
        story += self._section_heading("Product Validation Results", "🎯")

        val = self.validation
        if not val.get("available"):
            story.append(self._body(
                "No usage score report available. Generate one via "
                "POST /api/experiments/{id}/usage-score."
            ))
            story.append(PageBreak())
            return story

        score = val.get("score", 0)
        raw = val.get("raw_score_1_10", 0)
        would_use_pct = val.get("would_use_percentage", 0)
        methodology = val.get("methodology", "")
        limitations = val.get("limitations", "")

        # Score banner
        story.append(Spacer(1, 0.2 * cm))
        score_tbl = Table(
            [[
                Paragraph(f"<b>Validation Score</b>", self._s("H2")),
                Paragraph(f"<b>{score:.1f}</b><br/>out of 100", ParagraphStyle(
                    "ScoreBig", fontName="Helvetica-Bold", fontSize=28,
                    textColor=SUCCESS_GREEN if score >= 60 else WARNING_AMBER,
                    alignment=TA_CENTER, leading=32)),
                Paragraph(f"<b>{would_use_pct:.1f}%</b><br/>would adopt", ParagraphStyle(
                    "WouldUse", fontName="Helvetica-Bold", fontSize=18,
                    textColor=HIGHLIGHT, alignment=TA_CENTER, leading=24)),
            ]],
            colWidths=[USABLE_W * 0.45, USABLE_W * 0.3, USABLE_W * 0.25],
        )
        score_tbl.setStyle(TableStyle([
            ("BACKGROUND", (1, 0), (1, 0), LIGHT_BG),
            ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#E8F5E9")),
            ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_LINE),
            ("ROUNDEDCORNERS", [4]),
        ]))
        story.append(score_tbl)
        story.append(Spacer(1, 0.3 * cm))

        # Methodology note
        story.append(self._small(
            f"<b>Scoring methodology:</b> {methodology[:350]}" if methodology else
            "Overall score = arithmetic mean of per-persona scores (1–10 scale). "
            "Validation score (0–100) = (overall_score / 10) × 100."
        ))

        # Per-persona breakdown
        persona_scores = val.get("persona_scores", [])
        if persona_scores:
            story += self._sub_heading("Per-Persona Breakdown")
            tbl_data = [[
                Paragraph("Persona", self._s("TblHeader")),
                Paragraph("Occupation", self._s("TblHeader")),
                Paragraph("Score (1–10)", self._s("TblHeader")),
                Paragraph("Would Use?", self._s("TblHeader")),
                Paragraph("Category", self._s("TblHeader")),
            ]]
            for ps in persona_scores:
                would = "✅ Yes" if ps.get("would_use") else "❌ No"
                tbl_data.append([
                    Paragraph(str(ps.get("persona_name", ""))[:25], self._s("TblCell")),
                    Paragraph(str(ps.get("occupation", ""))[:30], self._s("TblCell")),
                    Paragraph(f"{ps.get('score', 0):.1f}", self._s("TblCellC")),
                    Paragraph(would, self._s("TblCellC")),
                    Paragraph(str(ps.get("category", ""))[:15], self._s("TblCell")),
                ])
            story.append(self._table(
                tbl_data,
                [USABLE_W * 0.22, USABLE_W * 0.28, USABLE_W * 0.16, USABLE_W * 0.16, USABLE_W * 0.18]
            ))

        # Strengths & Weaknesses
        strengths = val.get("strengths", [])
        weaknesses = val.get("weaknesses", [])
        opportunities = val.get("opportunities", [])

        if strengths:
            story += self._sub_heading("✅ Strengths (Personas likely to adopt)")
            for s in strengths:
                story.append(self._bullet(s))

        if weaknesses:
            story += self._sub_heading("⚠ Weaknesses (Adoption barriers)")
            for w in weaknesses:
                story.append(self._bullet(w))

        if opportunities:
            story += self._sub_heading("💡 Opportunities")
            for o in opportunities:
                story.append(self._bullet(o))

        if limitations:
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph(
                f"<b>Limitations:</b> {limitations[:400]}", self._s("Disclaimer")
            ))

        story.append(PageBreak())
        return story

    # ── 9. Recommendations ─────────────────────────────────────────────────────
    def _recommendations(self) -> list:
        story = []
        story += self._section_heading("Recommendations & Next Steps", "🚀")

        insight_raw = self.dashboard.get("_insight_raw", {})
        agreement_patterns = insight_raw.get("agreement_patterns", [])
        disagreements = insight_raw.get("disagreements", [])
        behavioral_trends = insight_raw.get("behavioral_trends", [])

        if agreement_patterns:
            story += self._sub_heading("Areas of Strong Agreement")
            for a in agreement_patterns:
                story.append(self._bullet(str(a)))

        if disagreements:
            story += self._sub_heading("Points of Disagreement / Friction")
            for d in disagreements:
                story.append(self._bullet(str(d)))

        if behavioral_trends:
            story += self._sub_heading("Behavioural Trends Observed")
            for b in behavioral_trends:
                story.append(self._bullet(str(b)))

        story += self._sub_heading("Suggested Next Steps")
        next_steps = [
            "Validate findings with at least 20–30 real user interviews before making product decisions.",
            "Prioritise addressing barriers identified in the theme analysis.",
            "A/B test pricing tiers with actual target demographic segments.",
            "Conduct usability studies on features that received mixed or negative sentiment.",
            "Re-run simulation with updated product description after key improvements are made.",
        ]
        for step in next_steps:
            story.append(self._bullet(step))

        story.append(PageBreak())
        return story

    # ── 10. Limitations & Conclusion ───────────────────────────────────────────
    def _limitations_conclusion(self) -> list:
        story = []
        story += self._section_heading("Limitations & Conclusion", "⚠")

        story.append(self._body(
            "This research report is based entirely on AI-generated synthetic user personas. "
            "The personas simulate plausible human behaviour based on their configured attributes, "
            "but they cannot replicate the full range of real human diversity, irrationality, "
            "cultural context, or evolving market conditions."
        ))
        story.append(Spacer(1, 0.2 * cm))
        story.append(self._body(
            "Key limitations:"
        ))
        limitations = [
            "Synthetic personas are not real people and do not represent a statistically valid sample of any population.",
            "Results must not be presented as proof of real-world product-market fit or market demand.",
            "The sentiment and theme analysis reflects patterns in AI-generated text, not genuine user emotion.",
            "Adoption scores are directional estimates, not predictive market adoption rates.",
            "AI hallucination risk exists; treat all findings as hypotheses requiring real-world validation.",
        ]
        for lim in limitations:
            story.append(self._bullet(lim))

        story.append(Spacer(1, 0.4 * cm))
        story.append(self._body(
            "<b>Conclusion:</b> The findings in this report provide a useful starting point for "
            "product hypothesis generation and early-stage directional research. The next critical "
            "step is to validate these synthetic insights through real user research, market testing, "
            "and iterative product development."
        ))
        return story
