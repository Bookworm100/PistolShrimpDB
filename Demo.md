# Demo
1. When prompted for an input file (as specified in Setup), you can pick any in the folder marked DemoFiles.
2. After you select a file, you follow the setup.
3. Then, you will be asked to specify an output file, and you can choose to specify one.
4. Remember that at any point, you can choose to exit, quit, abort, undo, or save your commands.
Here is a following demo for AirQualityMeasures.json as the input file (don't worry, other files takes less time to run commands. This one just happens to be pretty big):

5. Insert:
- Insert VALUES measureid=nonexistent, statename=California
- Insert anewkey with values measureid=fictional, countyname=San Diego

6. DELETE:
- DELETE row-m25u-q6ux~kz6d
- DELETE VALUES (statename=Connecticut, countyname=Tolland) (or alternatively, DELETE VALUES (statename=Connecticut AND countyname=Tolland))
- You can try out ands/ors in any combination!

7. Update:
- UPDATE row-tmj3.7qu6.ckbc WITH VALUES (measureid=100, year=2050)

8. Rename:
- Rename 'countyfips' 'countyid'

9. Select:
- SELECT * FROM KEYS (or SELECT \*)
- SELECT * FROM VALUES
- SELECT * FROM ALL
- SELECT row-tmj3.7qu6.ckbc to see that your changes were saved, or if you undoed or aborted, that nothing changed!
- SELECT measureid
- SELECT WHERE measureId=84, statefips=1, countyfips=1101, reportyear=1999
(again, ands/ors can go anywhere)

10. Search:
- SEARCH KEY tmj3 AND ckbc
- SEARCH VALUES elby, exa
- SEARCH KEY AND VALUES value=532 AND statename=necticu

11. Find:
- FIND KEY tmj3.7qu6.kbc
- FIND 0.7 VALUES Selby AND Teas
- FIND KEY AND VALUES 0.9 statenam=Connecicut