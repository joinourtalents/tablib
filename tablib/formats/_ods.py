# -*- coding: utf-8 -*-

""" Tablib - ODF Support.
"""

import sys


if sys.version_info[0] > 2:
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from tablib.compat import opendocument, style, table, text, unicode

title = 'ods'
extentions = ('ods',)

bold = style.Style(name="bold", family="paragraph")
bold.addElement(style.TextProperties(fontweight="bold", fontweightasian="bold", fontweightcomplex="bold"))

def detect(stream):
    """Returns True if given stream is a readable excel file."""
    try:
        doc = opendocument.load(stream)
        return True
    except:
        return False

def export_set(dataset):
    """Returns ODF representation of Dataset."""

    wb = opendocument.OpenDocumentSpreadsheet()
    wb.automaticstyles.addElement(bold)

    ws = table.Table(name=dataset.title if dataset.title else 'Tablib Dataset')
    wb.spreadsheet.addElement(ws)
    dset_sheet(dataset, ws)

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def export_book(databook):
    """Returns ODF representation of DataBook."""

    wb = opendocument.OpenDocumentSpreadsheet()
    wb.automaticstyles.addElement(bold)

    for i, dset in enumerate(databook._datasets):
        ws = table.Table(name=dset.title if dset.title else 'Sheet%s' % (i))
        wb.spreadsheet.addElement(ws)
        dset_sheet(dset, ws)


    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


def import_set(dset, in_stream, headers=True):
    """Returns dataset from ODS stream. Default sheet 1"""
    dset.wipe()

    doc = opendocument.load(in_stream)
    sheet = doc.spreadsheet.childNodes[0]
    rows = sheet.getElementsByType(table.TableRow)
    row_count = 0
    for row in rows:
        cells = row.getElementsByType(table.TableCell)
        arrCells = []
        cell_count = 0
        for cell in cells:
            # repeated value?
            repeat = cell.getAttribute("numbercolumnsrepeated")
            if(not repeat):
                repeat = 1

            ps = cell.getElementsByType(text.P)
            textContent = ""

            # for each text node
            for p in ps:
                c = p.firstChild  # TODO: Where is it used?
                textContent = textContent + unicode(p)

            if textContent and textContent[0] != "#": # ignore comments cells
                for rr in range(int(repeat)): # repeated?
                    arrCells.append(textContent)
                    cell_count += 1
            else:
                arrCells.append("")

        if row_count == 0 and headers:
            dset.headers = arrCells
        elif cell_count > 1:
            # empty cells are needed, but last string == ['']
            dset.append(arrCells)
        else:
            pass
        row_count += 1


def dset_sheet(dataset, ws):
    """Completes given worksheet from given Dataset."""
    _package = dataset._package(dicts=False)

    for i, sep in enumerate(dataset._separators):
        _offset = i
        _package.insert((sep[0] + _offset), (sep[1],))

    for i, row in enumerate(_package):
        row_number = i + 1
        odf_row = table.TableRow(stylename=bold, defaultcellstylename='bold')
        for j, col in enumerate(row):
            try:
                col = unicode(col, errors='ignore')
            except TypeError:
                ## col is already unicode
                pass
            ws.addElement(table.TableColumn())

            # bold headers
            if (row_number == 1) and dataset.headers:
                odf_row.setAttribute('stylename', bold)
                ws.addElement(odf_row)
                cell = table.TableCell()
                p = text.P()
                p.addElement(text.Span(text=col, stylename=bold))
                cell.addElement(p)
                odf_row.addElement(cell)

            # wrap the rest
            else:
                try:
                    if '\n' in col:
                        ws.addElement(odf_row)
                        cell = table.TableCell()
                        cell.addElement(text.P(text=col))
                        odf_row.addElement(cell)
                    else:
                        ws.addElement(odf_row)
                        cell = table.TableCell()
                        cell.addElement(text.P(text=col))
                        odf_row.addElement(cell)
                except TypeError:
                    ws.addElement(odf_row)
                    cell = table.TableCell()
                    cell.addElement(text.P(text=col))
                    odf_row.addElement(cell)
