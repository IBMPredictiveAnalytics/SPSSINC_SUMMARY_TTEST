
#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2020
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/
"""SPSSINC SUMMARY TTEST extension command"""

__author__ =  'spss, JKP'
__version__=  '1.0.1'

# Initial formulas provided by Marta Garc<i with acute accent>a-Granero.

# history
# 27-jan-2010 initial version


helptext = """SPSSINC SUMMARY TTEST N1=value(s) N2=value(s) MEAN1=value(s) MEAN2=value(s)
SD1=value(s) SD2=value(s) [CI=percentage] LABEL1=text(s) LABEL2=text(s)
[/HELP]

N1 and N2 are the case counts for the two samples.
MEAN1 and MEAN2 are the means.
SD1 and SD2 are the standard deviations.
LABEL1 and LABEL2 are optional labels for the samples as quoted text.

The N's, means, standard deviations, and labels can be lists of items.  
One set of statistics is produced for each
item in the list.  All the lists must be the same length.

CI is the confidence level expressed as a percentage.  It defaults to 95.

/HELP displays this help and does nothing else.
"""

import spss, spssaux
from extension import Template, Syntax, processcmd
import sys, locale, random
from math import sqrt

class DataStep(object):
    def __enter__(self):
        """initialization for with statement"""
        try:
            spss.StartDataStep()
        except:
            spss.Submit("EXECUTE")
            spss.StartDataStep()
        return self
    
    def __exit__(self, type, value, tb):
        spss.EndDataStep()
        return False

class C(object):   # for holding computation variables
    pass

def summaryttest(n1, n2, mean1, mean2, sd1, sd2, ci=95., label1=None, label2=None):
    """Create a set of dummy variables that span the values of varname within any current filter.
    
    The parameters are the obvious statistics.
    label1 and label2 are text to label the two groups
    """

    ##debugging
    #try:
        #import wingdbstub
        #if wingdbstub.debugger != None:
            #import time
            #wingdbstub.debugger.StopDebug()
            #time.sleep(2)
            #wingdbstub.debugger.StartDebug()
    #except:
        #pass
    ###myenc = locale.getlocale()[1]  # get current encoding in case conversions needed
    numtests = len(n1)
    
    if label1 is None:
        label1 = numtests * [_("Sample 1")]
    if label2 is None:
        label2 = numtests * [_("Sample 2")]
    testlist = [len(item) for item in [n1, n2, mean1, mean2, sd1, sd2, label1, label2]]
    if min(testlist) != max(testlist):
        raise ValueError(_("The same number of values must be given for each statistic or label"))
    currentactive = spss.ActiveDataset()
    if currentactive == "*":
        currentactive = "D" + str(random.uniform(0,1))
        spss.Submit("DATASET NAME " + currentactive)

    sl = 1 - ci/100.
    halfsiglevel = 1.- sl/2.
    c = []
        
    for i in range(numtests):
        c.append(C())
        d = c[i]
        if n1[i] < 1. or n2[i] < 1.:
            raise ValueError(_("Sample sizes must be at least 1"))
        d.sem1 = sd1[i]/sqrt(n1[i])
        d.sem2 = sd2[i]/sqrt(n2[i])
        d.diff = mean1[i] - mean2[i]
        d.var1 =sd1[i]*sd1[i]
        d.var2 = sd2[i]*sd2[i]
        if d.var1 >= d.var2:
            d.ftest = d.var1/d.var2
            d.num = n1[i]
            d.denom = n2[i]
        else:
            d.ftest = d.var2/d.var1
            d.num = n2[i]
            d.denom = n1[i]
        d.n = n1[i] + n2[i]
        d.poolvar = ((n1[i]-1.) * d.var1 + (n2[i]-1.) * d.var2)/(d.n-2.)
        d.eedif1 = sqrt(d.poolvar*(1./n1[i]+1./n2[i]))
        d.t1 = d.diff/d.eedif1
        d.df1 = d.n-2.
        d.eedif2 = sqrt(d.var1/n1[i]+d.var2/n2[i])
        d.t2 = d.diff/d.eedif2
        d.df2 = ((d.var1/n1[i]+d.var2/n2[i])**2)/(((d.var1/n1[i])**2)/(n1[i]-1.)+((d.var2/n2[i])**2)/(n2[i]-1.))
    
    with DataStep():
        ###ds = spss.Dataset(None, hidden=True)
        dsa = spss.Dataset()   # current active
        if len(dsa) == 0:   # check for empty dataset automatically created when Statistics start
            currentactive = None
        ds = spss.Dataset(None)
        dsname = ds.name
        ds.varlist.append('n1',0)
        ds.varlist.append('n2',0)
        ds.varlist.append('ftest',0)
        ds.varlist.append('df1',0)
        ds.varlist.append('df2',0)
        ds.varlist.append('halfsiglevel',0)
        ds.varlist.append('num',0)
        ds.varlist.append('denom',0) 
        ds.varlist.append('t1',0)
        ds.varlist.append('t2',0)  #9
        for i in range(numtests):
            d = c[i]
            ds.cases.append([n1[i], n2[i], d.ftest, d.df1, d.df2, halfsiglevel, d.num, d.denom, d.t1, d.t2])
        spss.SetActive(ds)
        
    spss.Submit("""compute fsig = 1-cdf.f(ftest, num, denom).
    compute t1sig=2*(1-cdf.t(abs(t1),df1)).
    compute t2sig=2*(1-cdf.t(abs(t2),df2)).
    compute idft1 = IDF.T(halfsiglevel,df1).
    compute idft2 = IDF.T(halfsiglevel,df2).
    compute norm = idf.normal(halfsiglevel,0,1).
    execute.""")
    
    with DataStep():
        ds = spss.Dataset(dsname)
        for i in range(numtests):
            d = c[i]
            d.fsig = ds.cases[i][10]
            d.t1sig = ds.cases[i][11]
            d.t2sig = ds.cases[i][12]
            d.idft1 = ds.cases[i][13]
            d.idft2 = ds.cases[i][14]
            norm = abs(ds.cases[0][15])
        ds.close()

    spss.StartProcedure("Summary T-Test")
    for i in range(numtests):
        if numtests > 1:
            seq = _("Test %d:  ") % (i+1)
        else:
            seq = ""
        d = c[i]
        d.low1 = d.diff - norm * d.eedif1
        d.upp1 = d.diff + norm * d.eedif1
        d.low2 = d.diff - norm * d.eedif2
        d.upp2 = d.diff + norm * d.eedif2
            
        d.low1exact = d.diff - d.eedif1 * d.idft1
        d.upp1exact = d.diff + d.eedif1 * d.idft1
        d.low2exact = d.diff - d.eedif2 * d.idft2
        d.upp2exact = d.diff +d.eedif2 * d.idft2
            
        pt = NonProcPivotTable("Group Statistics", outlinetitle=_("Summary Data"), tabletitle=seq + _("Summary Data"),
                columnlabels=[_("N"), _("Mean"), _("Std. Deviation"), _("Std. Error Mean")])
        pt.addrow(rowlabel=label1[i], cvalues=[n1[i], mean1[i], sd1[i], d.sem1])
        pt.addrow(rowlabel=label2[i], cvalues=[n2[i], mean2[i], sd2[i], d.sem2])
        pt.generate()
        
        pt = NonProcPivotTable("TTEST", outlinetitle=_("Independent Samples Test"), 
            tabletitle=seq +_("Independent Samples Test"), columnlabels=[_("Mean Difference"), _("Std. Error Difference"),
                _("t"), _("df"), _("Sig. (2-tailed)")], caption=_("Hartley test for equal variance: F = %.3f, Sig. = %.4f") %(d.ftest, d.fsig))
        pt.addrow(_("Equal variances assumed"), cvalues=[d.diff, d.eedif1, d.t1, d.df1, d.t1sig])
        pt.addrow(_("Equal variances not assumed"), cvalues=[d.diff, d.eedif2, d.t2, d.df2, d.t2sig])
        pt.generate()
        
        pt = NonProcPivotTable("Confidence Intervals", outlinetitle=_("Confidence Intervals"),
            tabletitle=seq + _("%.1f%% Confidence Intervals for Difference") % ci,
            columnlabels=[_("Lower Limit"), _("Upper Limit")])
        pt.addrow(rowlabel=_("Asymptotic (equal variance)"), cvalues=[d.low1, d.upp1])
        pt.addrow(rowlabel=_("Asymptotic (unequal variance)"), cvalues=[d.low2, d.upp2])
        pt.addrow(rowlabel=_("Exact (equal variance)"), cvalues = [d.low1exact, d.upp1exact])
        pt.addrow(rowlabel=_("Exact (unequal variance)"), cvalues = [d.low2exact, d.upp2exact])
        pt.generate()
        
    spss.EndProcedure() 

    try:
        if not currentactive is None:
            spss.Submit("DATASET ACTIVATE " + currentactive)
        else:
            spss.Submit("""NEW FILE.
            DATASET NAME D%s.""" % str(random.uniform(0,1)))
    except:
        pass
    
def Run(args):
    """Execute the SPSSINC SUMMARY TTEST extension command"""

    args = args[list(args.keys())[0]]

    oobj = Syntax([
        Template("N1", subc="",  ktype="float", var="n1", vallist=[0], islist=True),
        Template("N2", subc="",  ktype="float", var="n2", vallist=[0], islist=True),
        Template("MEAN1", subc="",  ktype="float", var="mean1", islist=True),
        Template("MEAN2", subc="",  ktype="float", var="mean2", islist=True),
        Template("SD1", subc="",  ktype="float", var="sd1", vallist=[0.0001], islist=True),
        Template("SD2", subc="",  ktype="float", var="sd2", vallist=[0.0001], islist=True),
        Template("LABEL1", subc="", ktype="literal", var="label1", islist=True),
        Template("LABEL2", subc="", ktype="literal", var="label2", islist=True),
        Template("CI", subc="", ktype="float", var="ci", vallist=[.1, 99.9999]),
        Template("HELP", subc="", ktype="bool")])
    
    #enable localization
    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg
    # A HELP subcommand overrides all else
    if "HELP" in args:
        #print helptext
        helper()
    else:
        processcmd(oobj, args, summaryttest)

def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""
    
    import webbrowser, os.path
    
    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"
    
    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print(("Help file not found:" + helpspec))
try:    #override
    from extension import helper
except:
    pass        
class NonProcPivotTable(object):
    """Accumulate an object that can be turned into a basic pivot table once a procedure state can be established"""
    
    def __init__(self, omssubtype, outlinetitle="", tabletitle="", caption="", rowdim="", coldim="", columnlabels=[],
                 procname="Messages"):
        """omssubtype is the OMS table subtype.
        caption is the table caption.
        tabletitle is the table title.
        columnlabels is a sequence of column labels.
        If columnlabels is empty, this is treated as a one-column table, and the rowlabels are used as the values with
        the label column hidden
        
        procname is the procedure name.  It must not be translated."""
        
        attributesFromDict(locals())
        self.rowlabels = []
        self.columnvalues = []
        self.rowcount = 0

    def addrow(self, rowlabel=None, cvalues=None):
        """Append a row labelled rowlabel to the table and set value(s) from cvalues.
        
        rowlabel is a label for the stub.
        cvalues is a sequence of values with the same number of values are there are columns in the table."""

        if cvalues is None:
            cvalues = []
        self.rowcount += 1
        if rowlabel is None:
            self.rowlabels.append(str(self.rowcount))
        else:
            self.rowlabels.append(rowlabel)
        self.columnvalues.extend(cvalues)
        
    def generate(self):
        """Produce the table assuming that a procedure state is now in effect if it has any rows."""
        
        privateproc = False
        if self.rowcount > 0:
            try:
                table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            except:
                spss.StartProcedure(self.procname)
                privateproc = True
                table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            if self.caption:
                table.Caption(self.caption)
            if self.columnlabels != []:
                table.SimplePivotTable(self.rowdim, self.rowlabels, self.coldim, self.columnlabels, self.columnvalues)
            else:
                table.Append(spss.Dimension.Place.row,"rowdim",hideName=True,hideLabels=True)
                table.Append(spss.Dimension.Place.column,"coldim",hideName=True,hideLabels=True)
                colcat = spss.CellText.String("Message")
                for r in self.rowlabels:
                    cellr = spss.CellText.String(r)
                    table[(cellr, colcat)] = cellr
            if privateproc:
                spss.EndProcedure()
                
def attributesFromDict(d):
    """build self attributes from a dictionary d."""
    self = d.pop('self')
    for name, value in d.items():
        setattr(self, name, value)

        
