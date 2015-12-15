# SPSSINC SUMMARY TTEST
Calculate a t test from the N's, means, and standard deviations rather than the case data

----
Requirements
----
- IBM SPSS Statistics 18 or later

---
Installation intructions
----
1. Open IBM SPSS Statistics
2. Navigate to Utilities -> Extension Bundles -> Download and Install Extension Bundles
3. Search for the name of the extension and click Ok. Your extension will be available.

---
Tutorial
----
SPSSINC SUMMARY TTEST N1=*value(s)*^&#42; N2=*value(s)*^&#42;  
MEAN1=*value(s)*^&#42; MEAN2=*value(s)*^&#42;  
SD1=*value(s)*^&#42; SD2=*value(s)*^&#42;  
CI=percentage  
LABEL1="*text*" "*text*" LABEL2="*text*"

/HELP

^&#42; Required  
^&#42;^&#42; Default

/HELP displays this help and does nothing else.

Example:
```
SPSSINC SUMMARY TTEST N1=20 MEAN1=5 SD1=2 LABEL1="Sample 1" 
N2=30 MEAN2=5.5 SD2=2.3 LABEL2="Sample 2" CI=95.
```

**N1** and **N2** are the case counts for the two samples.

**MEAN1** and **MEAN2** are the means.

**SD1** and **SD2** are the standard deviations.

**LABEL1** and **LABEL2** are optional labels for the samples as quoted text.

The N's, means, standard deviations, and labels can be lists of items.  
One set of statistics is produced for each
set of items in the lists.  All the lists must be the same length.

CI is the confidence level expressed as a percentage.  It defaults to 95.

---
License
----

- Apache 2.0
                              
Contributors
----

  - JKP, IBM SPSS
