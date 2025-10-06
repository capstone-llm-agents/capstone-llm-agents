#https://stackoverflow.com/questions/10112244/convert-plain-text-to-pdf-in-python
import textwrap
from fpdf import FPDF

def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    title_font_size = 50
    title_fontsize_mm = title_font_size * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')
    i = 0
    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            if i == 0:
                pdf.set_font(family='Courier', size=title_fontsize_mm, style='B')
                pdf.cell(0, title_fontsize_mm, wrap, ln=1, align='C')
                i = (i + 1)
            else:
                pdf.set_font(family='Courier', size=fontsize_pt)
                pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')

output_filename = 'output.pdf'
text = "Test two Title\ntest two text\n\n\ntest two text\ntest two text\ntest two text finsih"
text_to_pdf(text, output_filename)
