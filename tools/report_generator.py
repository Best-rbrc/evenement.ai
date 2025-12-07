"""Professional PDF report generator for event planning proposals.

Generates branded PDF reports matching the frontend design with:
- Executive summary
- Timeline visualization
- Budget breakdown tables
- Recommendations by category
- Risk assessment
- Action items checklist
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import json
from typing import Dict, Any, List, Union
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
        
        # Warm, elegant color scheme matching frontend
        # Primary: Soft coral (hsl(15, 75%, 55%)) ≈ #E67E5A
        self.primary_color = colors.HexColor('#E67E5A')
        # Secondary: Soft cream (hsl(35, 40%, 94%)) ≈ #F5E6D3
        self.secondary_color = colors.HexColor('#F5E6D3')
        # Accent: Teal (hsl(175, 50%, 40%)) ≈ #2D9B8A
        self.accent_color = colors.HexColor('#2D9B8A')
        # Success: Sage green (hsl(140, 25%, 75%)) ≈ #8FC4A3
        self.success_color = colors.HexColor('#8FC4A3')
        # Background: Warm cream (hsl(30, 20%, 98%)) ≈ #FAF8F5
        self.background_color = colors.HexColor('#FAF8F5')
        # Light gray: Muted warm gray (hsl(30, 15%, 92%)) ≈ #EBE8E3
        self.light_gray = colors.HexColor('#EBE8E3')
        # Champagne: (hsl(35, 60%, 92%)) ≈ #F5EBD8
        self.champagne = colors.HexColor('#F5EBD8')
        # Text: Dark warm gray (hsl(20, 25%, 15%)) ≈ #2A2520
        self.text_color = colors.HexColor('#2A2520')
        # Muted text: (hsl(20, 15%, 45%)) ≈ #6B6560
        self.muted_text = colors.HexColor('#6B6560')
        
    def generate_report(
        self,
        event_details: Dict[str, Any],
        final_plan: Dict[str, Any],
        specialist_outputs: Dict[str, Any] = None
    ) -> str:
        """Generate complete PDF report.
        
        Args:
            event_details: Original event requirements
            final_plan: Final planning output from coordinator (parsed JSON)
            specialist_outputs: Optional detailed specialist outputs
            
        Returns:
            Path to generated PDF file
        """
        # Ensure final_plan is a dict (might be string)
        if isinstance(final_plan, str):
            try:
                final_plan = json.loads(final_plan)
            except:
                final_plan = {"executive_summary": final_plan[:1000]}
        
        if not isinstance(final_plan, dict):
            final_plan = {}
        
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
        
        # Executive summary
        story.extend(self._create_executive_summary(final_plan, styles))
        story.append(PageBreak())
        
        # Event overview
        story.extend(self._create_event_overview(event_details, final_plan, styles))
        story.append(Spacer(1, 0.3*inch))
        
        # Timeline
        story.extend(self._create_timeline_section(final_plan, styles))
        story.append(PageBreak())
        
        # Budget breakdown
        story.extend(self._create_budget_section(final_plan, specialist_outputs, styles))
        story.append(PageBreak())
        
        # Recommendations by category
        story.extend(self._create_recommendations_section(final_plan, specialist_outputs, styles))
        story.append(PageBreak())
        
        # Schedule (if scheduling agent was used)
        schedule_story = self._create_schedule_section(final_plan, styles)
        if schedule_story:  # Only add page break if schedule section has content
            story.extend(schedule_story)
            story.append(PageBreak())
        
        # Logo section (if logo was generated)
        logo_story = self._create_logo_section(final_plan, specialist_outputs, styles)
        if logo_story:
            story.extend(logo_story)
            story.append(PageBreak())
        
        # Risk assessment
        story.extend(self._create_risk_section(final_plan, styles))
        story.append(Spacer(1, 0.3*inch))
        
        # Action items
        story.extend(self._create_action_items_section(final_plan, styles))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return filepath
    
    def _add_custom_styles(self, styles):
        """Add custom paragraph styles matching frontend design."""
        # Title style - elegant, warm
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=32,
            textColor=self.text_color,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        ))
        
        # Heading 1 - warm coral accent
        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=self.primary_color,
            spaceAfter=16,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            leading=24
        ))
        
        # Heading 2 - teal accent
        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.accent_color,
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            leading=20
        ))
        
        # Subtitle - muted warm gray
        styles.add(ParagraphStyle(
            name='Subtitle',
            parent=styles['Normal'],
            fontSize=13,
            textColor=self.muted_text,
            alignment=TA_CENTER,
            spaceAfter=24,
            leading=18
        ))
        
        # Body text - readable, warm
        styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            alignment=TA_JUSTIFY,
            spaceAfter=14,
            leading=16
        ))
        
        # Bullet list style
        styles.add(ParagraphStyle(
            name='BulletText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            leftIndent=20,
            spaceAfter=8,
            leading=14
        ))
    
    def _create_cover_page(self, event_details: Dict[str, Any], styles) -> List:
        """Create elegant cover page matching frontend design."""
        story = []
        
        # Add vertical spacing
        story.append(Spacer(1, 1.5*inch))
        
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
        
        story.append(Spacer(1, 0.6*inch))
        
        # Key details box with warm styling
        details_data = [
            ['Event Date:', event_details.get('event_date', event_details.get('date', 'TBD'))],
            ['Location:', event_details.get('location_preference', event_details.get('location', 'TBD'))],
            ['Expected Guests:', str(event_details.get('guest_count', event_details.get('guestCount', 'TBD')))],
            ['Budget Range:', event_details.get('budget_range', event_details.get('budget', 'TBD'))],
        ]
        
        details_table = Table(details_data, colWidths=[2.2*inch, 3.3*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.champagne),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (0, -1), self.text_color),
            ('TEXTCOLOR', (1, 0), (1, -1), self.text_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 14),
            ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, self.light_gray]),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 1.2*inch))
        
        # Generated date
        gen_date = Paragraph(
            f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>",
            styles['Subtitle']
        )
        story.append(gen_date)
        
        # Footer with accent color
        story.append(Spacer(1, 1.5*inch))
        footer = Paragraph(
            f"<font color='{self.accent_color.hexval()}'><b>Évènement.ai</b></font><br/>"
            f"<font color='{self.muted_text.hexval()}'>Comprehensive Event Planning Solutions</font>",
            styles['Subtitle']
        )
        story.append(footer)
        
        return story
    
    def _create_executive_summary(self, final_plan: Dict[str, Any], styles) -> List:
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("<b>Executive Summary</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        summary_text = final_plan.get('executive_summary', 'No executive summary available.')
        
        # Split into paragraphs if needed
        if isinstance(summary_text, str):
            paragraphs = summary_text.split('\n\n') if '\n\n' in summary_text else [summary_text]
        else:
            paragraphs = [str(summary_text)]
        
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.strip().replace('\n', '<br/>'), styles['CustomBodyText'])
                story.append(p)
        
        return story
    
    def _create_event_overview(self, event_details: Dict[str, Any], final_plan: Dict[str, Any], styles) -> List:
        """Create event overview section."""
        story = []
        
        story.append(Paragraph("<b>Event Overview</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Create overview table - extract from both event_details and final_plan
        overview_data = [
            ['Event Name', event_details.get('event_name', final_plan.get('event_name', 'N/A'))],
            ['Event Type', str(event_details.get('event_type', final_plan.get('event_type', 'N/A'))).title()],
            ['Date', event_details.get('event_date', event_details.get('date', final_plan.get('event_date', 'TBD')))],
            ['Location', event_details.get('location_preference', event_details.get('location', final_plan.get('location', 'TBD')))],
            ['Expected Attendance', str(event_details.get('guest_count', event_details.get('guestCount', final_plan.get('guest_count', 'TBD'))))],
            ['Budget', event_details.get('budget_range', event_details.get('budget', final_plan.get('budget', {}).get('total_available', 'TBD')))],
        ]
        
        if event_details.get('special_requirements'):
            overview_data.append(['Special Requirements', event_details['special_requirements']])
        
        overview_table = Table(overview_data, colWidths=[2.2*inch, 4.3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.champagne),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (0, -1), self.text_color),
            ('TEXTCOLOR', (1, 0), (1, -1), self.text_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.white, self.light_gray]),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
        ]))
        
        story.append(overview_table)
        
        return story
    
    def _create_timeline_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create timeline section."""
        story = []
        
        story.append(Paragraph("<b>Timeline & Schedule</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        timeline = final_plan.get('timeline', [])
        
        if not timeline or not isinstance(timeline, list):
            story.append(Paragraph("Timeline information not available.", styles['CustomBodyText']))
            return story
        
        # Create timeline table
        timeline_data = [['Phase', 'Tasks', 'Deadline']]
        
        for phase in timeline:
            if not isinstance(phase, dict):
                continue
                
            phase_name = phase.get('phase', 'N/A')
            tasks = phase.get('tasks', [])
            deadline = phase.get('deadline', 'TBD')
            
            # Format tasks as bullet list
            if isinstance(tasks, list) and tasks:
                tasks_list = []
                for task in tasks[:8]:  # Limit to 8 tasks per phase
                    if task:
                        tasks_list.append(f"• {str(task)}")
                if len(tasks) > 8:
                    tasks_list.append(f"• ... and {len(tasks) - 8} more tasks")
                tasks_text = '<br/>'.join(tasks_list)
            else:
                tasks_text = str(tasks) if tasks else 'No tasks specified'
            
            timeline_data.append([
                Paragraph(phase_name.replace('\n', '<br/>'), styles['Normal']),
                Paragraph(tasks_text, styles['Normal']),
                Paragraph(str(deadline).replace('\n', '<br/>'), styles['Normal'])
            ])
        
        if len(timeline_data) > 1:  # Has data beyond header
            timeline_table = Table(timeline_data, colWidths=[1.6*inch, 3.4*inch, 1.5*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                ('TOPPADDING', (0, 0), (-1, 0), 14),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.text_color),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
                ('FONTNAME', (2, 1), (2, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('PADDING', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
            ]))
            
            story.append(timeline_table)
        else:
            story.append(Paragraph("No timeline phases defined.", styles['CustomBodyText']))
        
        return story
    
    def _create_budget_section(self, final_plan: Dict[str, Any], specialist_outputs: Dict[str, Any], styles) -> List:
        """Create budget breakdown section."""
        story = []
        
        story.append(Paragraph("<b>Budget Breakdown</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        budget = final_plan.get('budget', {})
        if not isinstance(budget, dict):
            budget = {}
        
        # Try to get budget from specialist outputs if not in final_plan
        if not budget and specialist_outputs:
            budgeting_data = specialist_outputs.get('budgeting', {})
            if isinstance(budgeting_data, str):
                try:
                    budgeting_data = json.loads(budgeting_data)
                except:
                    budgeting_data = {}
            
            if budgeting_data:
                # Extract from budgeting agent output
                major_breakdowns = budgeting_data.get('major_category_breakdowns', {})
                if major_breakdowns:
                    budget = {
                        'by_category': {k: v.get('recommended_spend', 0) if isinstance(v, dict) else v 
                                       for k, v in major_breakdowns.items()},
                        'total_allocated': sum(v.get('recommended_spend', 0) if isinstance(v, dict) else (v if isinstance(v, (int, float)) else 0)
                                             for v in major_breakdowns.values()),
                    }
        
        if not budget:
            story.append(Paragraph("Budget information not available.", styles['CustomBodyText']))
            return story
        
        # Budget summary
        total_available = budget.get('total_available', 0)
        total_allocated = budget.get('total_allocated', 0)
        status = budget.get('status', 'unknown')
        
        # Format numbers
        def format_currency(value):
            if isinstance(value, (int, float)):
                return f"${value:,.2f}"
            elif isinstance(value, str):
                # Try to extract number
                import re
                numbers = re.findall(r'[\d,]+\.?\d*', value)
                if numbers:
                    try:
                        num = float(numbers[0].replace(',', ''))
                        return f"${num:,.2f}"
                    except:
                        pass
                return value
            return str(value)
        
        summary_data = [
            ['Total Available Budget', format_currency(total_available)],
            ['Total Allocated', format_currency(total_allocated)],
            ['Status', status.replace('_', ' ').title()],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.champagne),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Category breakdown
        by_category = budget.get('by_category', {})
        
        if by_category and isinstance(by_category, dict):
            story.append(Paragraph("<b>Budget by Category</b>", styles['CustomHeading2']))
            story.append(Spacer(1, 0.1*inch))
            
            category_data = [['Category', 'Allocation', 'Percentage']]
            
            # Calculate total for percentages
            total = 0
            category_amounts = {}
            for category, amount in by_category.items():
                # Extract numeric value
                if isinstance(amount, (int, float)):
                    category_amounts[category] = float(amount)
                    total += float(amount)
                elif isinstance(amount, str):
                    import re
                    numbers = re.findall(r'[\d,]+\.?\d*', amount)
                    if numbers:
                        try:
                            num = float(numbers[0].replace(',', ''))
                            category_amounts[category] = num
                            total += num
                        except:
                            category_amounts[category] = 0
                    else:
                        category_amounts[category] = 0
                else:
                    category_amounts[category] = 0
            
            for category, amount in by_category.items():
                percentage = (category_amounts[category] / total * 100) if total > 0 else 0
                category_data.append([
                    category.replace('_', ' ').title(),
                    format_currency(amount),
                    f"{percentage:.1f}%"
                ])
            
            # Add total row
            category_data.append(['TOTAL', format_currency(total_allocated or total), '100%'])
            
            category_table = Table(category_data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.accent_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), self.primary_color),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 1), (0, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('PADDING', (0, 1), (-1, -2), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, self.light_gray]),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
            ]))
            
            story.append(category_table)
        
        return story
    
    def _create_recommendations_section(self, final_plan: Dict[str, Any], specialist_outputs: Dict[str, Any], styles) -> List:
        """Create detailed recommendations section."""
        story = []
        
        story.append(Paragraph("<b>Detailed Recommendations</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        recommendations = final_plan.get('recommendations', {})
        if not isinstance(recommendations, dict):
            recommendations = {}
        
        # Also check specialist outputs for more detailed recommendations
        if specialist_outputs:
            for agent_name, output in specialist_outputs.items():
                if isinstance(output, str):
                    try:
                        output = json.loads(output)
                    except:
                        continue
                
                if not isinstance(output, dict):
                    continue
                
                # Extract recommendations from specialist outputs
                if agent_name == 'venue' and 'venues' in output:
                    if 'venue' not in recommendations:
                        recommendations['venue'] = {}
                    recommendations['venue']['venues'] = output.get('venues', [])
                    recommendations['venue']['summary'] = output.get('summary', '')
                
                elif agent_name == 'catering' and 'menu_overview' in output:
                    if 'catering' not in recommendations:
                        recommendations['catering'] = {}
                    recommendations['catering']['menu_overview'] = output.get('menu_overview', [])
                    recommendations['catering']['summary'] = output.get('summary', '')
        
        if not recommendations:
            story.append(Paragraph("No detailed recommendations available.", styles['CustomBodyText']))
            return story
        
        for category, details in recommendations.items():
            if not details:
                continue
                
            # Category heading
            story.append(Paragraph(
                f"<b>{category.replace('_', ' ').title()}</b>",
                styles['CustomHeading2']
            ))
            story.append(Spacer(1, 0.1*inch))
            
            # Format details based on structure
            if isinstance(details, dict):
                # Handle structured recommendations
                if 'summary' in details:
                    story.append(Paragraph(details['summary'], styles['CustomBodyText']))
                    story.append(Spacer(1, 0.1*inch))
                
                # Handle venues list
                if 'venues' in details and isinstance(details['venues'], list):
                    for venue in details['venues'][:3]:  # Limit to top 3
                        if isinstance(venue, dict):
                            venue_text = f"<b>{venue.get('name', 'Venue')}</b>"
                            if venue.get('location'):
                                venue_text += f" - {venue.get('location')}"
                            if venue.get('estimated_cost'):
                                venue_text += f" ({venue.get('estimated_cost')})"
                            story.append(Paragraph(venue_text, styles['Normal']))
                            if venue.get('amenities'):
                                amenities = ', '.join(venue.get('amenities', [])[:5])
                                story.append(Paragraph(f"<i>Features: {amenities}</i>", styles['Normal']))
                            story.append(Spacer(1, 0.1*inch))
                
                # Handle menu overview
                elif 'menu_overview' in details and isinstance(details['menu_overview'], list):
                    for item in details['menu_overview'][:5]:
                        story.append(Paragraph(f"• {item}", styles['BulletText']))
                
                # Handle other structured data
                else:
                    # Format as key-value pairs
                    for key, value in list(details.items())[:8]:  # Limit to 8 items
                        if key not in ['summary', 'venues', 'menu_overview']:
                            if isinstance(value, list):
                                value_str = ', '.join(str(v) for v in value[:5])
                            elif isinstance(value, dict):
                                value_str = ', '.join(f"{k}: {v}" for k, v in list(value.items())[:3])
                            else:
                                value_str = str(value)
                            
                            if len(value_str) > 100:
                                value_str = value_str[:100] + "..."
                            
                            story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value_str}", styles['Normal']))
                            story.append(Spacer(1, 0.05*inch))
                
            elif isinstance(details, str):
                # Simple string recommendation
                if len(details) > 500:
                    details = details[:500] + "..."
                story.append(Paragraph(details.replace('\n', '<br/>'), styles['CustomBodyText']))
            else:
                # Fallback
                details_str = str(details)
                if len(details_str) > 500:
                    details_str = details_str[:500] + "..."
                story.append(Paragraph(details_str.replace('\n', '<br/>'), styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_schedule_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create optimized schedule section."""
        story = []
        
        schedule = final_plan.get('schedule', {})
        if not isinstance(schedule, dict):
            return story
        
        sessions = schedule.get('sessions', [])
        metrics = schedule.get('metrics', {})
        
        if not sessions and not metrics:
            return story  # Skip if no schedule data
        
        story.append(Paragraph("<b>Optimized Event Schedule</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metrics summary
        if metrics and isinstance(metrics, dict):
            story.append(Paragraph("<b>Schedule Optimization Metrics</b>", styles['CustomHeading2']))
            
            metrics_data = [
                ['Total Duration', str(metrics.get('total_duration', 'N/A'))],
                ['Event Ends At', str(metrics.get('event_ends_at', 'N/A'))],
                ['Conflicts Resolved', str(metrics.get('conflicts_resolved', 'N/A'))],
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.champagne),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Session schedule
        if sessions and isinstance(sessions, list):
            story.append(Paragraph("<b>Session Schedule</b>", styles['CustomHeading2']))
            
            # Build session data with Paragraphs for proper text wrapping
            session_data = [
                [Paragraph('<b>Time</b>', styles['Normal']), 
                 Paragraph('<b>Session</b>', styles['Normal']), 
                 Paragraph('<b>Room</b>', styles['Normal']), 
                 Paragraph('<b>Speaker</b>', styles['Normal'])]
            ]
            
            for session in sessions[:20]:  # Limit to 20 sessions
                if not isinstance(session, dict):
                    continue
                    
                # Format time with date if available
                start_time = session.get('start_time', '')
                end_time = session.get('end_time', '')
                date = session.get('date', '')
                
                time_str = f"{start_time} - {end_time}" if start_time and end_time else 'TBD'
                if date:
                    time_str = f"{date}<br/>{time_str}"
                
                session_name = str(session.get('name', session.get('session_name', 'N/A')))
                room = str(session.get('room', 'N/A'))
                speaker = str(session.get('speaker', 'N/A'))
                
                # Truncate long text to prevent overflow, but use Paragraph for multi-line support
                time_para = Paragraph(time_str, styles['Normal'])
                session_para = Paragraph(session_name[:60] + ('...' if len(session_name) > 60 else ''), styles['Normal'])
                room_para = Paragraph(room[:30] + ('...' if len(room) > 30 else ''), styles['Normal'])
                speaker_para = Paragraph(speaker[:30] + ('...' if len(speaker) > 30 else ''), styles['Normal'])
                
                session_data.append([
                    time_para,
                    session_para,
                    room_para,
                    speaker_para
                ])
            
            if len(session_data) > 1:  # Has data beyond header
                session_table = Table(session_data, colWidths=[1.3*inch, 2.5*inch, 1.3*inch, 1.4*inch])
                session_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.accent_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.text_color),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('PADDING', (0, 1), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
                    ('GRID', (0, 0), (-1, -1), 0, colors.white),
                    ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
                ]))
                
                story.append(session_table)
        
        return story
    
    def _create_logo_section(self, final_plan: Dict[str, Any], specialist_outputs: Dict[str, Any], styles) -> List:
        """Create logo section if logo was generated."""
        story = []
        
        # Check for logo in specialist outputs
        logo_path = None
        logo_info = None
        
        if specialist_outputs:
            logo_data = specialist_outputs.get('logo', {})
            if isinstance(logo_data, str):
                try:
                    logo_data = json.loads(logo_data)
                except:
                    logo_data = {}
            
            if isinstance(logo_data, dict):
                logo_path = logo_data.get('logo_file_path') or logo_data.get('logo_url')
                logo_info = logo_data
        
        if not logo_path:
            return story  # No logo, return empty story
        
        story.append(Paragraph("<b>Event Logo</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Try to add logo image if file exists
        if logo_path and os.path.exists(logo_path):
            try:
                from reportlab.platypus import Image
                img = Image(logo_path, width=3*inch, height=3*inch, kind='proportional')
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            except Exception as e:
                # If image loading fails, just show the path
                story.append(Paragraph(f"Logo file: {logo_path}", styles['CustomBodyText']))
        
        # Add logo information if available
        if logo_info:
            if logo_info.get('design_rationale'):
                story.append(Paragraph("<b>Design Rationale</b>", styles['CustomHeading2']))
                story.append(Paragraph(str(logo_info['design_rationale']), styles['CustomBodyText']))
                story.append(Spacer(1, 0.1*inch))
            
            if logo_info.get('color_palette'):
                story.append(Paragraph("<b>Color Palette</b>", styles['CustomHeading2']))
                palette = logo_info['color_palette']
                if isinstance(palette, list):
                    palette_text = ', '.join(str(c) for c in palette)
                else:
                    palette_text = str(palette)
                story.append(Paragraph(palette_text, styles['CustomBodyText']))
        
        return story
    
    def _create_risk_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create risk assessment section."""
        story = []
        
        story.append(Paragraph("<b>Risk Assessment</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        risks = final_plan.get('risks', [])
        
        if not risks or not isinstance(risks, list):
            story.append(Paragraph("No significant risks identified.", styles['CustomBodyText']))
            return story
        
        risk_data = [['Risk', 'Severity', 'Mitigation Strategy']]
        
        for risk in risks:
            if not isinstance(risk, dict):
                continue
                
            severity = risk.get('severity', 'medium')
            severity_color = {
                'high': self.primary_color,
                'medium': colors.HexColor('#F39C12'),  # Orange
                'low': self.success_color
            }.get(severity.lower(), colors.gray)
            
            risk_text = risk.get('risk', 'N/A')
            mitigation = risk.get('mitigation', 'N/A')
            
            # Truncate if too long
            if len(risk_text) > 80:
                risk_text = risk_text[:77] + "..."
            if len(mitigation) > 120:
                mitigation = mitigation[:117] + "..."
            
            # Wrap mitigation text in Paragraph for proper formatting
            mitigation_para = Paragraph(mitigation.replace('\n', '<br/>'), styles['Normal'])
            
            risk_data.append([
                Paragraph(risk_text.replace('\n', '<br/>'), styles['Normal']),
                Paragraph(f"<font color='{severity_color.hexval()}'><b>{severity.upper()}</b></font>", styles['Normal']),
                mitigation_para
            ])
        
        if len(risk_data) > 1:  # Has data beyond header
            risk_table = Table(risk_data, colWidths=[2*inch, 1*inch, 3.5*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.text_color),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('PADDING', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
            ]))
            
            story.append(risk_table)
        
        return story
    
    def _create_action_items_section(self, final_plan: Dict[str, Any], styles) -> List:
        """Create action items checklist section."""
        story = []
        
        story.append(Paragraph("<b>Action Items & Next Steps</b>", styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        action_items = final_plan.get('action_items', [])
        
        if not action_items or not isinstance(action_items, list):
            story.append(Paragraph("No action items specified.", styles['CustomBodyText']))
            return story
        
        action_data = [['Priority', 'Action', 'Owner', 'Deadline']]
        
        for item in action_items:
            if not isinstance(item, dict):
                continue
                
            priority = item.get('priority', 'medium')
            priority_color = {
                'high': self.primary_color,
                'medium': self.accent_color,
                'low': self.success_color
            }.get(priority.lower(), colors.gray)
            
            # Use colored text instead of emoji for better PDF compatibility
            priority_text = f"<font color='{priority_color.hexval()}'><b>{priority.upper()}</b></font>"
            
            action = item.get('action', 'N/A')
            if len(action) > 100:
                action = action[:97] + "..."
            
            # Wrap action text in Paragraph for proper formatting
            action_para = Paragraph(action.replace('\n', '<br/>'), styles['Normal'])
            
            action_data.append([
                Paragraph(priority_text, styles['Normal']),
                action_para,
                Paragraph(str(item.get('owner', 'TBD')).replace('\n', '<br/>'), styles['Normal']),
                Paragraph(str(item.get('deadline', 'TBD')).replace('\n', '<br/>'), styles['Normal'])
            ])
        
        if len(action_data) > 1:  # Has data beyond header
            action_table = Table(action_data, colWidths=[1*inch, 2.8*inch, 1.3*inch, 1.4*inch])
            action_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.accent_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.text_color),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('PADDING', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),
                ('GRID', (0, 0), (-1, -1), 0, colors.white),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.light_gray),
            ]))
            
            story.append(action_table)
        
        return story
    
    def _add_header_footer(self, canvas, doc):
        """Add elegant header and footer to each page."""
        canvas.saveState()
        
        # Draw subtle background gradient effect (top)
        canvas.setFillColor(self.background_color)
        canvas.rect(0, doc.height + doc.topMargin - 0.2*inch, doc.width + doc.leftMargin + doc.rightMargin, 0.3*inch, fill=1, stroke=0)
        
        # Header with accent color
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(self.accent_color)
        canvas.drawString(0.75*inch, doc.height + doc.topMargin + 0.3*inch, "Évènement.ai")
        
        # Subtle line separator
        canvas.setStrokeColor(self.light_gray)
        canvas.setLineWidth(0.5)
        canvas.line(0.75*inch, doc.height + doc.topMargin - 0.1*inch, 
                   doc.width + doc.leftMargin + 0.75*inch, doc.height + doc.topMargin - 0.1*inch)
        
        # Footer with page number
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(self.muted_text)
        page_num = canvas.getPageNumber()
        footer_text = f"Page {page_num}"
        canvas.drawRightString(doc.width + doc.leftMargin + 0.75*inch, 0.5*inch, footer_text)
        
        # Footer line
        canvas.setStrokeColor(self.light_gray)
        canvas.line(0.75*inch, 0.7*inch, 
                   doc.width + doc.leftMargin + 0.75*inch, 0.7*inch)
        
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
        final_plan: Final planning output from coordinator (may be string or dict)
        specialist_outputs: Optional detailed specialist outputs
        output_dir: Directory to save PDF
        
    Returns:
        Path to generated PDF file
    """
    generator = EventProposalReport(output_dir=output_dir)
    return generator.generate_report(event_details, final_plan, specialist_outputs)
