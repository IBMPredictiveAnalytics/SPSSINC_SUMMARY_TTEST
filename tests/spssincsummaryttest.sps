* test SPSSINC SUMMARY TTEST against standard T-TEST command.
file handle data/name="c:/spss18/samples/english".
get file = "data/cars.sav".
dataset name cars.

COMPUTE filter_$=(uniform(1)<=.05).
FILTER  BY filter_$.

dataset declare groupstats.
oms select tables /if subtypes='Group Statistics'
/destination format =sav outfile=groupstats.
COMPUTE filter_$=(uniform(1)<=.05).
FILTER  BY filter_$.
T-TEST GROUPS=origin(1 2)  /VARIABLES=mpg.
FILTER OFF.
COMPUTE filter_$=(uniform(1)<=.20).
FILTER  BY filter_$.
T-TEST GROUPS=origin(1 2)  /VARIABLES=mpg.
omsend.
dataset activate groupstats.
begin program.
import spss, spssdata
cases = spssdata.Spssdata().fetchall()
cmd = """SPSSINC SUMMARY TTEST 
N1=%s %s N2 = %s %s
MEAN1 = %s %s MEAN2=%s %s
SD1 = %s %s SD2 = %s %s
LABEL1="%s" "%s" LABEL2="%s" "%s" """
values = (cases[0].N, cases[2].N, cases[1].N, cases[3].N,
cases[0].Mean, cases[2].Mean, cases[1].Mean, cases[3].Mean, 
cases[0][7], cases[2][7], cases[1][7], cases[3][7],
cases[0].Var2, cases[2].Var2, cases[1].Var2, cases[3].Var2)

fullcmd = cmd % values
print fullcmd
spss.Submit(fullcmd)
end program.

