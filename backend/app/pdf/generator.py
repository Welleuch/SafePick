from fpdf import FPDF
from datetime import datetime
from typing import Optional


class TechnicalAuditReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'Internes Technisches Audit: Pre-Engineering Validierung', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(128)
        self.cell(0, 6, f'Datum: {datetime.now().strftime("%d.%m.%Y")}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_text_color(0)
        self.ln(5)

    def section_title(self, title: str):
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, title, fill=True, new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def section_content(self, content: str):
        self.set_font('Helvetica', '', 9)
        self.multi_cell(0, 5, content)
        self.ln(2)

    def table_row(self, label: str, value: str, status: Optional[str] = None):
        self.set_font('Helvetica', 'B', 9)
        self.cell(50, 6, label)
        self.set_font('Helvetica', '', 9)
        self.cell(80, 6, value)
        if status:
            if status in ['GRÜN', 'PASS']:
                self.set_text_color(34, 197, 94)
            elif status in ['KRITISCH', 'FAIL']:
                self.set_text_color(239, 68, 68)
            else:
                self.set_text_color(234, 179, 8)
            self.cell(20, 6, status, align='R')
            self.set_text_color(0)
        self.ln()

    def footer(self):
        self.set_y(-25)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(128)
        self.cell(0, 4, 'Haftungsausschluss: Dieses Dokument dient als interne Entscheidungshilfe.', align='C', new_x='LMARGIN', new_y='NEXT')
        self.cell(0, 4, 'Die finale technische Verantwortung liegt beim Projektingenieur.', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(4)
        self.set_font('Helvetica', '', 8)
        self.cell(0, 6, 'Unterschrift Senior Engineer: _____________  Datum: _______', align='C')


def generate_audit_pdf(
    project_name: str,
    robot: dict,
    gripper: dict,
    workpiece_mass: float,
    distance: float,
    inertia_result: dict,
    cycle_result: dict,
    interface_result: dict,
    assumption_confirmed: bool,
    warning: Optional[str] = None
) -> bytes:
    """
    Generate a Technical Audit Report PDF.
    """
    pdf = TechnicalAuditReport()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, f'Projekt: {project_name}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.section_title('1. Systemkonfiguration')
    pdf.table_row('Robot:', f'{robot["brand"]} {robot["model_name"]}')
    pdf.table_row('Greifer:', f'{gripper["manufacturer"]} {gripper["model_name"]}')
    pdf.table_row('Werkstück:', f'{workpiece_mass} kg')
    pdf.table_row('Taktweg:', f'{distance} m')
    pdf.ln(5)

    pdf.section_title('2. Validierungsergebnisse')
    pdf.table_row(
        'Inertia-Guard:',
        f'{inertia_result["calculated_inertia"]} kgm² ({inertia_result["utilization_percent"]}% der Nennkapazität)',
        inertia_result["status"]
    )
    pdf.table_row(
        'Cycle-Time-Realist:',
        f'{cycle_result["estimated_seconds"]} s',
        cycle_result["status"]
    )
    pdf.table_row(
      'Interface-Checker:',
      'Kompatibel' if interface_result["overall_compatible"] else 'Nicht kompatibel',
      'PASS' if interface_result["overall_compatible"] else 'FAIL'
    )
    pdf.ln(5)

    pdf.section_title('3. Interface Details')
    pdf.table_row('Mechanisch:', interface_result["mechanical"]["details"], interface_result["mechanical"]["status"])
    pdf.table_row('Elektrisch:', interface_result["electrical"]["details"], interface_result["electrical"]["status"])
    pdf.table_row('Digital:', interface_result["digital"]["details"], interface_result["digital"]["status"])
    pdf.ln(5)

    pdf.section_title('4. Kritische Annahmen')
    pdf.section_content('Dieses Dokument basiert auf folgenden Annahmen:')
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 5, '1) Werkstueck trocken und sauber', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, '2) Greifer CoM-Abweichung < 5mm', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, '3) Umgebungstemperatur < 40C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 5, '4) Pick-up Zeit <= 100ms', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    if not assumption_confirmed and warning:
        pdf.set_text_color(234, 179, 8)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, f'WARNUNG: {warning}', new_x='LMARGIN', new_y='NEXT')
        pdf.set_text_color(0)
    elif assumption_confirmed:
        pdf.set_text_color(34, 197, 94)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, 'Anwendungsgültigkeit bestätigt.', new_x='LMARGIN', new_y='NEXT')
        pdf.set_text_color(0)
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 9)
    if inertia_result["status"] == "GRÜN" and interface_result["overall_compatible"]:
        pdf.set_fill_color(34, 197, 94)
        pdf.cell(0, 8, 'Ergebnis: VALIDIERUNG ERFOLGREICH', fill=True, align='C')
    else:
        pdf.set_fill_color(239, 68, 68)
        pdf.cell(0, 8, 'Ergebnis: VALIDIERUNG FEHLGESCHLAGEN', fill=True, align='C')

    pdf_output = pdf.output()
    return bytes(pdf_output)


def generate_simple_pdf(project_name: str, robot: dict, gripper: dict, results: dict) -> bytes:
    """Simpler PDF for testing."""
    pdf = TechnicalAuditReport()
    pdf.add_page()

    pdf.cell(0, 10, f'Projekt: {project_name}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.cell(0, 6, f'Robot: {robot["brand"]} {robot["model_name"]}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 6, f'Greifer: {gripper["manufacturer"]} {gripper["model_name"]}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 6, f'Valides System: {"Ja" if results["valid"] else "Nein"}', new_x='LMARGIN', new_y='NEXT')

    return pdf.output(dest='S').encode('latin-1', 'replace')