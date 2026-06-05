set workbookPath to "/Users/wangsiyan/Courses/面计离散/proj/outputs/v7_structured_workbook/experiment_v7_structured_results.xlsx"
set macroPath to "/Users/wangsiyan/Courses/面计离散/proj/outputs/v7_structured_workbook/build_v7_charts.bas"
set macroCode to read POSIX file macroPath

tell application "Microsoft Excel"
	activate
	open workbook workbook file name workbookPath
	delay 1
	do Visual Basic macroCode
	save active workbook
end tell
