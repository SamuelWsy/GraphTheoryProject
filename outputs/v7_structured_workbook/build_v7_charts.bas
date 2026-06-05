Sub BuildV7Charts()
    Dim wb As Workbook
    Dim wsA As Worksheet
    Dim wsB As Worksheet
    Dim wsC As Worksheet
    Dim co As ChartObject
    Dim labelsA(1 To 4) As String
    Dim labelsB(1 To 6) As String
    Dim i As Long

    Set wb = ActiveWorkbook
    Set wsA = wb.Worksheets("Experiment_A_Small")
    Set wsB = wb.Worksheets("Experiment_B_Large")

    Application.DisplayAlerts = False
    On Error Resume Next
    wb.Worksheets("Charts").Delete
    On Error GoTo 0
    Application.DisplayAlerts = True

    Set wsC = wb.Worksheets.Add(After:=wb.Worksheets(wb.Worksheets.Count))
    wsC.Name = "Charts"

    labelsA(1) = "N=8 No Trap"
    labelsA(2) = "N=8 Trap"
    labelsA(3) = "N=10 No Trap"
    labelsA(4) = "N=10 Trap"

    labelsB(1) = "N=50 No Trap"
    labelsB(2) = "N=50 Trap"
    labelsB(3) = "N=100 No Trap"
    labelsB(4) = "N=100 Trap"
    labelsB(5) = "N=200 No Trap"
    labelsB(6) = "N=200 Trap"

    With wsC
        .Range("A1").Value = "Experiment v7 Charts"
        .Range("A1").Font.Bold = True
        .Range("A1").Font.Size = 16

        .Range("A3:D3").Value = Array("Condition", "Lap6/Base (%)", "Lap8/Base (%)", "SVD8/Base (%)")
        For i = 1 To 4
            .Cells(3 + i, 1).Value = labelsA(i)
            .Cells(3 + i, 2).Value = wsA.Cells(3 + i, 10).Value
            .Cells(3 + i, 3).Value = wsA.Cells(3 + i, 17).Value
            .Cells(3 + i, 4).Value = wsA.Cells(3 + i, 23).Value
        Next i

        .Range("F3:J3").Value = Array("Condition", "Base Time (ms)", "Lap6 Time (ms)", "Lap8 Time (ms)", "SVD8 Time (ms)")
        For i = 1 To 4
            .Cells(3 + i, 6).Value = labelsA(i)
            .Cells(3 + i, 7).Value = wsA.Cells(3 + i, 5).Value
            .Cells(3 + i, 8).Value = wsA.Cells(3 + i, 12).Value
            .Cells(3 + i, 9).Value = wsA.Cells(3 + i, 19).Value
            .Cells(3 + i, 10).Value = wsA.Cells(3 + i, 25).Value
        Next i

        .Range("A26:D26").Value = Array("Condition", "Lap6/Theory6 (%)", "Lap8/Theory8 (%)", "SVD8/Theory8 (%)")
        For i = 1 To 6
            .Cells(26 + i, 1).Value = labelsB(i)
            .Cells(26 + i, 2).Value = wsB.Cells(3 + i, 8).Value
            .Cells(26 + i, 3).Value = wsB.Cells(3 + i, 15).Value
            .Cells(26 + i, 4).Value = wsB.Cells(3 + i, 21).Value
        Next i

        .Range("F26:I26").Value = Array("Condition", "Lap6 Time (ms)", "Lap8 Time (ms)", "SVD8 Time (ms)")
        For i = 1 To 6
            .Cells(26 + i, 6).Value = labelsB(i)
            .Cells(26 + i, 7).Value = wsB.Cells(3 + i, 10).Value
            .Cells(26 + i, 8).Value = wsB.Cells(3 + i, 17).Value
            .Cells(26 + i, 9).Value = wsB.Cells(3 + i, 23).Value
        Next i

        .Range("B4:D7").NumberFormat = "0.00"
        .Range("G4:J7").NumberFormat = "0.00"
        .Range("B27:D32").NumberFormat = "0.00"
        .Range("G27:I32").NumberFormat = "0.00"
        .Range("A3:J3,A26:I26").Font.Bold = True
        .Range("A3:J33").Columns.AutoFit
    End With

    Set co = wsC.ChartObjects.Add(Left:=20, Top:=150, Width:=520, Height:=300)
    With co.Chart
        .ChartType = xlColumnClustered
        .SetSourceData Source:=wsC.Range("A3:D7")
        .HasTitle = True
        .ChartTitle.Text = "Experiment A: Profit Ratio vs Base"
        .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = "Ratio (%)"
        .Legend.Position = xlLegendPositionBottom
    End With

    Set co = wsC.ChartObjects.Add(Left:=570, Top:=150, Width:=560, Height:=300)
    With co.Chart
        .ChartType = xlColumnClustered
        .SetSourceData Source:=wsC.Range("F3:J7")
        .HasTitle = True
        .ChartTitle.Text = "Experiment A: Runtime Comparison"
        .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = "Time (ms, log scale)"
        .Axes(xlValue).ScaleType = xlScaleLogarithmic
        .Legend.Position = xlLegendPositionBottom
    End With

    Set co = wsC.ChartObjects.Add(Left:=20, Top:=520, Width:=520, Height:=320)
    With co.Chart
        .ChartType = xlColumnClustered
        .SetSourceData Source:=wsC.Range("A26:D32")
        .HasTitle = True
        .ChartTitle.Text = "Experiment B: Profit Ratio vs Theory"
        .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = "Ratio (%)"
        .Legend.Position = xlLegendPositionBottom
    End With

    Set co = wsC.ChartObjects.Add(Left:=570, Top:=520, Width:=560, Height:=320)
    With co.Chart
        .ChartType = xlColumnClustered
        .SetSourceData Source:=wsC.Range("F26:I32")
        .HasTitle = True
        .ChartTitle.Text = "Experiment B: Pruned Runtime Comparison"
        .Axes(xlValue).HasTitle = True
        .Axes(xlValue).AxisTitle.Text = "Time (ms)"
        .Legend.Position = xlLegendPositionBottom
    End With

    wsC.Activate
    wb.Save
End Sub

BuildV7Charts
