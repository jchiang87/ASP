"""
@brief Process FERMI_GBM_FLT_POSITION notices for MOST_LIKELY fields
and fill the FERMI_GCN_NOTICE_INFO table with that information.  Also
process GIOC ARR emails and fill the ARR_FLAG field.

@author J. Chiang
"""
#
# $Header$
#

from databaseAccess import apply

def have_grb_id(grb_id):
    sql = "select GRB_ID from FERMI_GCN_NOTICE_INFO where GRB_ID=%i" % grb_id
    result_set = apply(sql, lambda curs : [x[0] for x in curs])
    if result_set:
        return True
    return False

def grb_error(grb_id):
    sql = "select GRB_ERROR from FERMI_GCN_NOTICE_INFO where GRB_ID=%i" % grb_id
    pos_err = apply(sql, lambda curs : [x[0] for x in curs][0])
    return pos_err

def line_filter(line, filter_items=('GCN/FERMI_GBM_FLT_POSITION',
                                    'GBM Negative ARR',
                                    'GBM Positive ARR'), position=0):
    if line.find('Subject') == 0:
        subject = line.strip().split(':')[1].strip()
        for item in filter_items:
            if subject.find(item) == position:
                return True
    return False

class GBM_Notice_parser(dict):
    def __init__(self, lines):
        dict.__init__(self)
        data_start = False
        for line in lines:
            if line.find('Subject') == 0:
                if not line_filter(line):
                    raise RuntimeError("Invalid Notice type")
            if not data_start and (line.find('TITLE') == 0 or
                                   line.find('Trigger Number')):
                data_start = True
            if data_start and line.find(':') != -1:
                tokens = line.strip().split(':')
                self[tokens[0]] = tokens[1].strip()
    def _apply(self, sql, debug):
        print sql
        if not debug:
            apply(sql)
    def update_tables(self, debug=False):
        try:
            grb_id = int(self['TRIGGER_NUM'])
            pos_err = float(self['GRB_ERROR'].split()[0])
            if not have_grb_id(grb_id):
                sql = ("""insert into FERMI_GCN_NOTICE_INFO 
                          (GRB_ID, GRB_ERROR, MOST_LIKELY, MOST_LIKELY_2)
                          values (%i, %e, '%s', '%s')""" 
                       % (grb_id, pos_err, self['MOST_LIKELY'],
                          self['2nd_MOST_LIKELY']))
                self._apply(sql, debug)
            else:
                if pos_err < grb_error(grb_id):
                    sql = ("""update FERMI_GCN_NOTICE_INFO set
                              GRB_ERROR=%f,MOST_LIKELY='%s',MOST_LIKELY_2='%s'
                              where GRB_ID=%i"""
                           % (pos_err, self['MOST_LIKELY'],
                              self['2nd_MOST_LIKELY'], grb_id))
                    self._apply(sql, debug)
        except KeyError:
            grb_id = int(self['Trigger Number'])
            arr_flag = int(self['Repoint Decision'].split()[0])
            if not have_grb_id(grb_id):
                sql = ("""insert into FERMI_GCN_NOTICE_INFO 
                          (GRB_ID, ARR_FLAG) values (%i, %i)"""
                       % (grb_id, arr_flag))
            else:
                sql = ("""update FERMI_GCN_NOTICE_INFO set
                          ARR_FLAG=%i where GRB_ID=%i"""
                       % (arr_flag, grb_id))
            self._apply(sql, debug)

if __name__ == '__main__':
    import sys
#    foo = GBM_Notice_parser(sys.stdin.readlines())
#    foo.update_tables()
    notice_files = ('example_notice.txt', 'neg_arr_example.txt', 
                    'example_notice_arr.txt', 'pos_arr_example.txt',
                    'GBM_gnd_notice.txt', 'Swift_bat_notice',
                    'Swift_xrt_notice')

    debug = True

    for notice in notice_files:
        try:
            foo = GBM_Notice_parser(open(notice))
            print "processing:", notice
            foo.update_tables(debug)
        except RuntimeError:
            print "skipping:", notice
