#!/usr/bin/env python

import os
import sys
import fnmatch
import argparse
import re
from StringIO import StringIO
try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

# Import available PDF parser libraries
PARSER_LIBS = []
try:
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.converter import TextConverter
    from pdfminer.pdfinterp import PDFPageInterpreter
    from pdfminer.layout import LAParams
    PARSER_LIBS.append('pdfminer')
except ImportError:
    pass

class PDF_Dumper(object):
    def __init__(self, library='pdfminer'):
        if library not in PARSER_LIBS:
            e = 'Selected PDF parser library not found: %s' % (library)
            raise ImportError(e)
        self.library = library

    def dump_pdf_pdfminer(self, fpath_in):
        fpath_out = os.path.splitext(fpath_in)[0] + ".txt"
        n = 0

        with open(fpath_in, 'rb') as fin:
            with open(fpath_out, 'wb') as fout:
                try:
                    laparams = LAParams()
                    laparams.all_texts = True  
                    rsrcmgr = PDFResourceManager()
                    pagenos = set()

                    page_num = 0
                    for page in PDFPage.get_pages(fin, pagenos, check_extractable=True):
                        page_num += 1

                        retstr = StringIO()
                        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
                        interpreter = PDFPageInterpreter(rsrcmgr, device)
                        interpreter.process_page(page)
                        data = retstr.getvalue()
                        retstr.close()

                        fout.write(data)
                        n += len(data)
                    print "Written %d bytes to %s" % (n, fpath_out)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as e:
                    print "Failed parsing %s" % (fpath_in)

    def dump_pdf(self, fpath):
        parser_format = "dump_pdf_" + self.library
        try:
            self.parser_func = getattr(self, parser_format)
        except AttributeError:
            e = 'Selected PDF parser library is not supported: %s' % (self.library)
            raise NotImplementedError(e)
            
        self.parser_func(fpath)

    def dump(self, path):
        if os.path.isfile(path):
            self.dump_pdf(path)
            return

        if os.path.isdir(path):
            for walk_root, walk_dirs, walk_files in os.walk(path):
                for walk_file in fnmatch.filter(walk_files, "*.pdf"):
                    self.dump_pdf(os.path.join(walk_root, walk_file))
            return

        e = 'File path is not a file or directory: %s' % (path)
        raise IOError(e)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('FILE', action='store', help='File/directory path to report(s)')
    argparser.add_argument('-l', dest='LIB', default='pdfminer', help='PDF parsing library (pypdf2/pdfminer)')
    args = argparser.parse_args()

    dumper = PDF_Dumper(args.LIB)
    dumper.dump(args.FILE)
