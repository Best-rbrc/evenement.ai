"""Professional PDF report generator for event planning proposals.

Generates branded PDF reports with:
- Executive summary
- Timeline visualization (Gantt chart style)
- Budget breakdown tables
- Recommendations by category
- Risk assessment
- Action items checklist
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import json
from typing import Dict, Any, List
import os


class EventProposalReport:
    """Generate professional PDF reports for event planning proposals."""
    
    def __init__(self, output_dir: str = "event_outputs"):
        """Initialize report generator.
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Define color scheme (professional blue/gray)
        self.primary_color = colors.HexColor('#2C3E50')
        self.secondary_color = colors.HexColor('#3498DB')
        self.accent_color = colors.HexColor('#E74C3C')
        self.success_color = colors.HexColor('#27AE60')
        self.light_gray = colors.HexColor('#ECF0F1')
        
    def generate_report(
        self,
        event_details: Dict[str, Any],
        final_plan: Dict[str, Any],
        specialist_outputs: Dict[str, Any] = None
    ) -> str:
        """Generate complete PDF report.
        
        Args:
            event_details: Original event requirements
            final_plan: Final planning output from coordinator
            specialist_outputs: Optional detailed specialist outputs
            
        Returns:
            Path to generated PDF file
        """
        # Generate filename
        event_name = event_details.get('event_name', 'Event').replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{event_name}_Proposal_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        self._add_custom_styles(styles)
        
        # Cover page
        story.extend(self._create_cover_page(event_details, styles))
        story.append(PageBreak())
        
        # Table of contents
        story.extend(self._create_table_of_contents(styles))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(final_plan, styles))
        story.append(PageBreak())
        
        # Event overview
        story.extend(self._create_event_overview(event_details, styles))
        story.append(Spacer(1, 0.3*inch))
        
        # Timeline/Schedule
        story.extend(self._create_timeline_section(final_plan, styles))
        story.append(PageBreak())
        
        # Budget breakdown
        story.extend(self._create_budget_section(final_plan, styles))
        story.append(PageBreak())
        
        # Recommendations by category
        if 'recommendations' in final_plan:
            story.extend(self._create_recommendations_section(final_plan, styles))
            story.append(PageBreak())
        
        # Schedule (if scheduling agent was used)
        if 'schedule' in final_plan and final_plan['schedule'].get('optimized'):
            story.extend(self._create_schedule_section(final_plan, styles))
            story.append(PageBreak())
        
        # Risk assessment
        if 'risks' in final_plan:
            story.extend(self._create_risk_section(final_plan, styles))
            story.append(Spacer(1, 0.3*inch))
        
        # Action items
        if 'action_items' in final_plan:
            story.extend(self._create_action_items_section(final_plan, styles))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return filepath
    
    def _add_custom_styles(self, styles):
        """Add custom paragraph styles."""
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            textColor=self.primary_color,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=self.primary_color,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.secondary_color,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def _create_cover_page(self, event_details: Dict[str, Any], styles) -> List:
        """Create cover page."""
        story = []
        
        # Add vertical spacing
        story.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph(
            f"<b>{event_details.get('event_name', 'Event Planning Proposal')}</b>",
            styles['CustomTitle']
        )
        story.append(title)
        
        # Subtitle
        subtitle = Paragraph(
            f"{event_details.get('event_type', 'Event').title()} Planning Proposal",
            styles['Subtitle']
        )
        story.append(subtitle)
        
        story.append(Spacer(1, 0.5*inch))
        
        # Key details box
        details_data = [
            ['Event Date:', event_details.get('event_date', 'TBD')],
            ['Location:', event_details.get('location_preference', 'TBD')],
            ['Expected Guests:', event_details.get('guest_count', 'TBD')],
            ['Budget Range:', event_details.get('budget_range', 'TBD')],
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 3.5*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.light_gray),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.primary_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 1*inch))
        
        # Generated date
        gen_date = Paragraph(
            f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>",
            styles['Subtitle']
        )
        story.append(gen_date)
        
        # Footer
        story.append(Spacer(1, 1.5*inch))
        footer = Paragraph(
            "<b>AI Event Planner</b><br/>Comprehensive Event Planning Solutions",
            styles['Subtitle']
        )
        story.append(footer)
        
        return story
    
    def _create_table_of_contents(self, styles) -> List:
        """Create table of contents."""
        story = []
        
        story.append(Paragraph("<b>Table of Contents</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            "1. Executive Summary",
            "2. Event Overview",
            "3. Timeline & Schedule",
            "4. Budget Breakdown",
            "5. Detailed Recommendations",
            "6. Risk Assessment",
            "7. Action Items & Next Steps",
        ]
        
        for item in toc_items:
            p = Paragraph(item, styles['CustomBodyText'])
            story.append(p)
        
        return story
    
    def _create_executive_summary(self, final_plan: Dict[str, Any], styles) -> List:
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("<b>1. Executive Summary</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        summary_text = final_plan.get('executive_summary', 'No executive summary available.')
        
        # Split into paragraphs if needed
        paragraphs = summary_text.split('\n\n') if '\n\n' in summary_text else [summary_text]
        
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.strip(), styles['CustomBodyText'])
                story.append(p)
        
        return story
    
    def _create_event_overview(self, event_details: Dict[str, Any], styles) -> List:
        """Create event overview section."""
        story = []
        
        story.append(Paragraph("<b>2. Event Overview</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Create overview table
        overview_data = [
            ['Event Name', event_details.get('event_name', 'N/A')],
            ['Event Type', event_details.get('event_type', 'N/A').title()],
            ['Date', event_details.get('event_date', 'TBD')],
            ['Location', event_details.get('location_preference', 'TBD')],
            ['Expected Attendance', event_details.get('guest_count', 'TBD')],
            ['Budget', event_details.get('budget_range', 'TBD')],
        ]
        
        if event_details.get('special_requirements'):
            overview_data.append(['Special Requirements', event_details['special_requirements']])
        
        overview_table = Table(overview_data, colWidths=[2*inch, 4.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.light_gray),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.primary_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.light_gray]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(overview_table)
        
        return story
    
    def _create_timeline_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create timeline section with Gantt-style visualization."""
        story = []
        
        story.append(Paragraph("<b>3. Timeline & Schedule</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        timeline = final_plan.get('timeline', [])
        
        if not timeline:
            story.append(Paragraph("Timeline information not available.", styles['CustomBodyText']))
            return story
        
        # Create timeline table
        timeline_data = [['Phase', 'Tasks', 'Deadline']]
        
        for phase in timeline:
            phase_name = phase.get('phase', 'N/A')
            tasks = phase.get('tasks', [])
            deadline = phase.get('deadline', 'TBD')
            
            # Format tasks as bullet list
            if isinstance(tasks, list):
                tasks_text = '<br/>'.join([f"• {task}" for task in tasks[:5]])  # Limit to 5 tasks
                if len(tasks) > 5:
                    tasks_text += f"<br/>• ... and {len(tasks) - 5} more"
            else:
                tasks_text = str(tasks)
            
            timeline_data.append([
                phase_name,
                Paragraph(tasks_text, styles['Normal']),
                deadline
            ])
        
        timeline_table = Table(timeline_data, colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.primary_color),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
            ('GRID', (0, 0), (-1, -1), 1, colors.gray),
        ]))
        
        story.append(timeline_table)
        
        return story
    
    def _create_budget_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create budget breakdown section."""
        story = []
        
        story.append(Paragraph("<b>4. Budget Breakdown</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        budget = final_plan.get('budget', {})
        
        if not budget:
            story.append(Paragraph("Budget information not available.", styles['CustomBodyText']))
            return story
        
        # Budget summary
        summary_data = [
            ['Total Available Budget', budget.get('total_available', 'N/A')],
            ['Total Allocated', budget.get('total_allocated', 'N/A')],
            ['Status', budget.get('status', 'Unknown').replace('_', ' ').title()],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.light_gray),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.primary_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.gray),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Category breakdown
        by_category = budget.get('by_category', {})
        
        if by_category:
            story.append(Paragraph("<b>Budget by Category</b>", styles['CustomHeading2']))
            story.append(Spacer(1, 0.1*inch))
            
            category_data = [['Category', 'Allocation', 'Percentage']]
            
            # Calculate total for percentages
            total = 0
            category_amounts = {}
            for category, amount in by_category.items():
                # Extract numeric value from string like "$5,000"
                if isinstance(amount, str):
                    numeric = amount.replace('$', '').replace(',', '')
                    try:
                        category_amounts[category] = float(numeric)
                        total += float(numeric)
                    except:
                        category_amounts[category] = 0
                else:
                    category_amounts[category] = amount
                    total += amount
            
            for category, amount in by_category.items():
                percentage = (category_amounts[category] / total * 100) if total > 0 else 0
                category_data.append([
                    category.replace('_', ' ').title(),
                    amount if isinstance(amount, str) else f"${amount:,.2f}",
                    f"{percentage:.1f}%"
                ])
            
            # Add total row
            total_str = budget.get('total_allocated', f"${total:,.2f}")
            category_data.append(['TOTAL', total_str, '100%'])
            
            category_table = Table(category_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, -1), (-1, -1), self.primary_color),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (0, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, self.light_gray]),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
            ]))
            
            story.append(category_table)
        
        return story
    
    def _create_recommendations_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create detailed recommendations section."""
        story = []
        
        story.append(Paragraph("<b>5. Detailed Recommendations</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        recommendations = final_plan.get('recommendations', {})
        
        for category, details in recommendations.items():
            # Category heading
            story.append(Paragraph(
                f"<b>{category.replace('_', ' ').title()}</b>",
                styles['CustomHeading2']
            ))
            
            # Format details
            if isinstance(details, dict):
                details_text = json.dumps(details, indent=2)
            elif isinstance(details, str):
                details_text = details
            else:
                details_text = str(details)
            
            # Truncate if too long
            if len(details_text) > 500:
                details_text = details_text[:500] + "..."
            
            p = Paragraph(
                details_text.replace('\n', '<br/>'),
                styles['Normal']
            )
            story.append(p)
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_schedule_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create optimized schedule section."""
        story = []
        
        story.append(Paragraph("<b>Optimized Event Schedule</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        schedule = final_plan.get('schedule', {})
        sessions = schedule.get('sessions', [])
        metrics = schedule.get('metrics', {})
        
        # Metrics summary
        if metrics:
            story.append(Paragraph("<b>Schedule Optimization Metrics</b>", styles['CustomHeading2']))
            
            metrics_data = [
                ['Total Duration', metrics.get('total_duration', 'N/A')],
                ['Event Ends At', metrics.get('event_ends_at', 'N/A')],
                ['Conflicts Resolved', metrics.get('conflicts_resolved', 'N/A')],
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.light_gray),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Session schedule
        if sessions:
            story.append(Paragraph("<b>Session Schedule</b>", styles['CustomHeading2']))
            
            session_data = [['Time', 'Session', 'Room', 'Speaker']]
            
            for session in sessions:
                session_data.append([
                    f"{session.get('start_time', '')} - {session.get('end_time', '')}",
                    session.get('session_name', 'N/A'),
                    session.get('room', 'N/A'),
                    session.get('speaker', 'N/A')
                ])
            
            session_table = Table(session_data, colWidths=[1.2*inch, 2.3*inch, 1.5*inch, 1.5*inch])
            session_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ]))
            
            story.append(session_table)
        
        return story
    
    def _create_risk_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create risk assessment section."""
        story = []
        
        story.append(Paragraph("<b>6. Risk Assessment</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        risks = final_plan.get('risks', [])
        
        if not risks:
            story.append(Paragraph("No significant risks identified.", styles['CustomBodyText']))
            return story
        
        risk_data = [['Risk', 'Severity', 'Mitigation Strategy']]
        
        for risk in risks:
            severity = risk.get('severity', 'medium')
            severity_color = {
                'high': self.accent_color,
                'medium': colors.orange,
                'low': self.success_color
            }.get(severity, colors.gray)
            
            risk_data.append([
                risk.get('risk', 'N/A'),
                Paragraph(f"<font color='{severity_color.hexval()}'><b>{severity.upper()}</b></font>", styles['Normal']),
                risk.get('mitigation', 'N/A')
            ])
        
        risk_table = Table(risk_data, colWidths=[2*inch, 1*inch, 3.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(risk_table)
        
        return story
    
    def _create_action_items_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create action items checklist section."""
        story = []
        
        story.append(Paragraph("<b>7. Action Items & Next Steps</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        action_items = final_plan.get('action_items', [])
        
        if not action_items:
            story.append(Paragraph("No action items specified.", styles['CustomBodyText']))
            return story
        
        action_data = [['Priority', 'Action', 'Owner', 'Deadline']]
        
        for item in action_items:
            priority = item.get('priority', 'medium')
            priority_symbol = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority, '⚪')
            
            action_data.append([
                f"{priority_symbol} {priority.upper()}",
                item.get('action', 'N/A'),
                item.get('owner', 'TBD'),
                item.get('deadline', 'TBD')
            ])
        
        action_table = Table(action_data, colWidths=[1*inch, 3*inch, 1.25*inch, 1.25*inch])
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ]))
        
        story.append(action_table)
        
        return story
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.gray)
        canvas.drawString(0.75*inch, doc.height + doc.topMargin + 0.5*inch, "AI Event Planner")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        page_num = canvas.getPageNumber()
        footer_text = f"Page {page_num}"
        canvas.drawRightString(doc.width + doc.leftMargin + 0.75*inch, 0.5*inch, footer_text)
        
        canvas.restoreState()


def generate_event_proposal_pdf(
    event_details: Dict[str, Any],
    final_plan: Dict[str, Any],
    specialist_outputs: Dict[str, Any] = None,
    output_dir: str = "event_outputs"
) -> str:
    """Convenience function to generate PDF report.
    
    Args:
        event_details: Original event requirements
        final_plan: Final planning output from coordinator
        specialist_outputs: Optional detailed specialist outputs
        output_dir: Directory to save PDF
        
    Returns:
        Path to generated PDF file
    """
    generator = EventProposalReport(output_dir=output_dir)
    return generator.generate_report(event_details, final_plan, specialist_outputs)
