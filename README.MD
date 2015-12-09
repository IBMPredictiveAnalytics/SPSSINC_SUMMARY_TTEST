STATS OPEN PROJECT Extension Command
====================================

Open a project defined in a project file


STATS OPEN PROJECT  
FILE="*file*"   
PASSWORD="*password*"  
STARTUP = ASIS^&#42;&#42; or SET or DELETE

/HELP

^&#42; Required  
^&#42;&#42; Default

/HELP displays this help and does nothing else.

A project file defines a set of files to open and SPSS code to run.  A
project can be set to open automatically when Statistics is launched.

**FILE** is the name of a project file to open.  A project file is a plain text
file with the following format.
```
[RUN]
syntax commands in interactive format
[OPEN]
list of data (.sav), syntax (.sps), and output (.spv) files to open,
one per line
[PROJECT]
list of other project files to be opened
```

Sections may appear in any order and may be repeated.
Files listed in a PROJECT section must follow this same format.
If you have a standard utility library and various working projects,
it may be convenient to reference a standard project file first and then
make working project specifications.

File handles defined in executed RUN sections or before this command can
be used in file listings.

Lines starting with a semicolon are comments and are echoed to the Viewer.

Optionally a single password, encrypted or in plain text can be
specified to be applied to files listed in OPEN sections if your version
of Statistics supports this.  The password must be enclosed in quotes.

**STARTUP** specifies what happens in future sessions.  
* SET: future sessions will open this project automatically
* DELETE: future sessions will not open this project.
* ASIS: future sessions will operate the same as the current
session.

Note: SET creates a script that is automatically executed when
Statistics starts.  If there is an existing startup script, it
is replaced if it appears to have been created by this command.  
STARTUP=DELETE erases the startup script if it appears to have
been created with this command.

If you want to combine automatic project opening with other scripted
activities at startup, you can add the startup code to your
existing script.  This portion of the script would look like this.
```
import SpssClient
SpssClient.StartClient()
SpssClient.RunSyntax(r'''STATS OPEN PROJECT FILE="project filename".''')
SpssClient.StopClient()
```

(C) Copyright IBM Corp. 1989, 2014
