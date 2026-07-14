#!/usr/bin/env python3
"""Render the LunaSeis manuscript as a clean single-column preprint PDF."""

from __future__ import annotations
import re
from html import escape
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate,Frame,Image,PageTemplate,Paragraph,Spacer,PageBreak,KeepTogether

ROOT=Path(__file__).resolve().parents[1];OUTPUT=ROOT/"output/pdf/lunaseis_1_manuscript_preprint.pdf"


def markup(text:str)->str:
    text=escape(text);text=re.sub(r"\*\*(.+?)\*\*",r"<b>\1</b>",text);text=re.sub(r"\*(.+?)\*",r"<i>\1</i>",text);text=re.sub(r"`(.+?)`",r"<font name='Courier'>\1</font>",text);return text


def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor("#CBD2D9"));canvas.line(22*mm,15*mm,188*mm,15*mm);canvas.setFont("Helvetica",7.5);canvas.setFillColor(colors.HexColor("#52606D"));canvas.drawString(22*mm,10*mm,"LunaSeis-1 - Advaith Praveen (APRK) - pre-release manuscript");canvas.drawRightString(188*mm,10*mm,str(doc.page));canvas.restoreState()


def main()->None:
    OUTPUT.parent.mkdir(parents=True,exist_ok=True);styles=getSampleStyleSheet();body=ParagraphStyle("Body",parent=styles["BodyText"],fontName="Helvetica",fontSize=9.3,leading=13.2,alignment=TA_JUSTIFY,spaceAfter=5);h1=ParagraphStyle("H1",parent=styles["Heading1"],fontName="Helvetica-Bold",fontSize=14,leading=17,spaceBefore=10,spaceAfter=6,textColor=colors.HexColor("#17324D"));h2=ParagraphStyle("H2",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=11,leading=14,spaceBefore=8,spaceAfter=4,textColor=colors.HexColor("#17324D"));title=ParagraphStyle("Title",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=20,leading=24,alignment=TA_CENTER,textColor=colors.HexColor("#102A43"));center=ParagraphStyle("Center",parent=body,alignment=TA_CENTER);caption=ParagraphStyle("Caption",parent=body,fontSize=8,leading=10.5,textColor=colors.HexColor("#52606D"),spaceAfter=10)
    doc=BaseDocTemplate(str(OUTPUT),pagesize=A4,rightMargin=22*mm,leftMargin=22*mm,topMargin=20*mm,bottomMargin=20*mm,title="LunaSeis-1",author="Advaith Praveen (APRK)");frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id="normal");doc.addPageTemplates(PageTemplate(id="paper",frames=frame,onPage=footer))
    lines=(ROOT/"paper/manuscript.md").read_text().splitlines();story=[];paragraph=[];figure_captions=[];collecting_figures=False
    def flush():
        nonlocal paragraph
        if paragraph:story.append(Paragraph(markup(" ".join(paragraph)),body));paragraph=[]
    for line in lines:
        line=line.strip()
        if not line:flush();continue
        if collecting_figures and line.startswith("**Figure "):
            figure_captions.append(line);continue
        if collecting_figures and not line.startswith("## "):continue
        if collecting_figures and line.startswith("## "):collecting_figures=False
        if line.startswith("# "):
            flush();story.extend([Spacer(1,22*mm),Paragraph(markup(line[2:]),title),Spacer(1,8*mm)])
        elif line.startswith("**Advaith") or line=="Archeum Studios" or line.startswith("Copyright"):
            flush();story.append(Paragraph(markup(line.replace("**","")),center))
        elif line.startswith("## Figure captions"):
            flush();collecting_figures=True
        elif line.startswith("## "):
            flush();story.append(Paragraph(markup(line[3:]),h1))
        elif line.startswith("### "):
            flush();story.append(Paragraph(markup(line[4:]),h2))
        elif line.startswith("- "):
            flush();story.append(Paragraph("&#8226; "+markup(line[2:]),body))
        elif line.startswith("**Figure "):
            flush();figure_captions.append(line)
        elif line.startswith("|"):
            continue
        else:paragraph.append(line)
    flush()
    story.append(Spacer(1,8*mm));story.append(Paragraph("Figures",h1))
    for index,caption_text in enumerate(figure_captions,1):
        image=ROOT/f"paper/figures/figure_{index}_";matches=sorted(image.parent.glob(image.name+"*.png"));
        if not matches:continue
        img=Image(str(matches[0]));maxw,maxh=doc.width,105*mm;scale=min(maxw/img.imageWidth,maxh/img.imageHeight);img.drawWidth*=scale;img.drawHeight*=scale;story.append(KeepTogether([img,Paragraph(markup(caption_text),caption)]))
    doc.build(story);print(OUTPUT)


if __name__=="__main__":main()
