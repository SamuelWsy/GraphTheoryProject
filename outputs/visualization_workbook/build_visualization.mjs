import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/Users/wangsiyan/Courses/面计离散/proj/outputs/visualization_workbook";
const outputPath = `${outputDir}/arbitrage_pruning_visualization.xlsx`;
const largeBaseTimeCapMs = 100000;

const expA = [
  { n: 8, trap: "False", condition: "N=8 / No trap", baseProfit: 2.510, baseProfitSd: 0.32, baseTime: 17.80, baseTimeSd: 0.34, theoryL6: 3.532, lap6Profit: 1.997, lap6Opt: 79.6, lap6Time: 0.40, lap6TimeSd: 0.01, theoryL8: 4.710, lap8Profit: 2.510, lap8Opt: 100.0, lap8Time: 17.74, lap8TimeSd: 0.22, svd8Profit: 2.510, svd8Opt: 100.0, svd8Time: 18.04, svd8TimeSd: 0.21 },
  { n: 8, trap: "True", condition: "N=8 / Trap", baseProfit: 13.757, baseProfitSd: 0.30, baseTime: 17.95, baseTimeSd: 0.24, theoryL6: 3.532, lap6Profit: 13.242, lap6Opt: 96.3, lap6Time: 0.41, lap6TimeSd: 0.02, theoryL8: 4.710, lap8Profit: 13.757, lap8Opt: 100.0, lap8Time: 18.01, lap8TimeSd: 0.28, svd8Profit: 13.757, svd8Opt: 100.0, svd8Time: 18.08, svd8TimeSd: 0.33 },
  { n: 10, trap: "False", condition: "N=10 / No trap", baseProfit: 3.257, baseProfitSd: 0.58, baseTime: 1358.80, baseTimeSd: 26.41, theoryL6: 3.717, lap6Profit: 1.714, lap6Opt: 52.6, lap6Time: 0.42, lap6TimeSd: 0.01, theoryL8: 4.956, lap8Profit: 2.459, lap8Opt: 75.5, lap8Time: 17.95, lap8TimeSd: 0.37, svd8Profit: 2.345, svd8Opt: 72.0, svd8Time: 17.84, svd8TimeSd: 0.21 },
  { n: 10, trap: "True", condition: "N=10 / Trap", baseProfit: 14.620, baseProfitSd: 0.19, baseTime: 1341.69, baseTimeSd: 28.43, theoryL6: 3.717, lap6Profit: 12.993, lap6Opt: 88.9, lap6Time: 0.41, lap6TimeSd: 0.01, theoryL8: 4.956, lap8Profit: 13.670, lap8Opt: 93.5, lap8Time: 17.93, lap8TimeSd: 0.35, svd8Profit: 13.737, svd8Opt: 94.0, svd8Time: 17.94, svd8TimeSd: 0.49 },
];

const expB = [
  { n: 50, trap: "False", condition: "N=50 / No trap", baseEst: "约 10^50 年", theoryL6: 4.845, lap6Profit: 2.098, lap6ProfitSd: 0.34, lap6Opt: 69.6, lap6Time: 0.42, lap6TimeSd: 0.00, theoryL8: 6.460, lap8Profit: 3.015, lap8ProfitSd: 0.40, lap8Opt: 100.0, lap8Time: 17.49, lap8TimeSd: 0.17, svd8Profit: 2.779, svd8ProfitSd: 0.12, svd8Opt: 92.2, svd8Time: 17.54, svd8TimeSd: 0.16 },
  { n: 50, trap: "True", condition: "N=50 / Trap", baseEst: "约 10^50 年", theoryL6: 4.845, lap6Profit: 12.833, lap6ProfitSd: 0.76, lap6Opt: 91.2, lap6Time: 0.43, lap6TimeSd: 0.01, theoryL8: 6.460, lap8Profit: 14.076, lap8ProfitSd: 0.58, lap8Opt: 100.0, lap8Time: 17.56, lap8TimeSd: 0.16, svd8Profit: 13.819, svd8ProfitSd: 0.47, svd8Opt: 98.2, svd8Time: 17.69, svd8TimeSd: 0.12 },
  { n: 100, trap: "False", condition: "N=100 / No trap", baseEst: "约 10^144 年", theoryL6: 5.257, lap6Profit: 2.192, lap6ProfitSd: 0.38, lap6Opt: 71.6, lap6Time: 0.45, lap6TimeSd: 0.00, theoryL8: 7.009, lap8Profit: 3.060, lap8ProfitSd: 0.26, lap8Opt: 100.0, lap8Time: 17.79, lap8TimeSd: 0.04, svd8Profit: 2.910, svd8ProfitSd: 0.23, svd8Opt: 95.1, svd8Time: 17.92, svd8TimeSd: 0.17 },
  { n: 100, trap: "True", condition: "N=100 / Trap", baseEst: "约 10^144 年", theoryL6: 5.257, lap6Profit: 13.324, lap6ProfitSd: 0.15, lap6Opt: 93.5, lap6Time: 0.44, lap6TimeSd: 0.01, theoryL8: 7.009, lap8Profit: 14.244, lap8ProfitSd: 0.51, lap8Opt: 100.0, lap8Time: 18.03, lap8TimeSd: 0.18, svd8Profit: 13.921, svd8ProfitSd: 0.46, svd8Opt: 97.7, svd8Time: 17.65, svd8TimeSd: 0.28 },
  { n: 200, trap: "False", condition: "N=200 / No trap", baseEst: "接近无限时间", theoryL6: 5.638, lap6Profit: 2.156, lap6ProfitSd: 0.13, lap6Opt: 71.8, lap6Time: 0.47, lap6TimeSd: 0.01, theoryL8: 7.518, lap8Profit: 2.763, lap8ProfitSd: 0.28, lap8Opt: 92.0, lap8Time: 17.67, lap8TimeSd: 0.32, svd8Profit: 3.003, svd8ProfitSd: 0.36, svd8Opt: 100.0, svd8Time: 17.89, svd8TimeSd: 0.19 },
  { n: 200, trap: "True", condition: "N=200 / Trap", baseEst: "接近无限时间", theoryL6: 5.638, lap6Profit: 13.268, lap6ProfitSd: 0.35, lap6Opt: 91.4, lap6Time: 0.47, lap6TimeSd: 0.01, theoryL8: 7.518, lap8Profit: 14.515, lap8ProfitSd: 0.19, lap8Opt: 100.0, lap8Time: 17.85, lap8TimeSd: 0.17, svd8Profit: 14.002, svd8ProfitSd: 0.34, svd8Opt: 96.5, svd8Time: 18.00, svd8TimeSd: 0.16 },
];

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("Dashboard");
const sheetA = workbook.worksheets.add("Experiment A");
const sheetB = workbook.worksheets.add("Experiment B");
const chartData = workbook.worksheets.add("Chart Data");
const notes = workbook.worksheets.add("Notes");

function put(sheet, address, values) {
  sheet.getRange(address).values = values;
}

function styleTitle(sheet, range) {
  sheet.getRange(range).format = {
    fill: "#153243",
    font: { color: "#FFFFFF", bold: true, size: 16 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
}

function styleHeader(sheet, range) {
  sheet.getRange(range).format = {
    fill: "#2E6F73",
    font: { color: "#FFFFFF", bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: "#C9D6D5" },
  };
}

function styleBody(sheet, range) {
  sheet.getRange(range).format = {
    borders: { preset: "outside", style: "thin", color: "#DEE7E6" },
    verticalAlignment: "center",
    wrapText: true,
  };
}

function styleKpi(sheet, range) {
  sheet.getRange(range).format = {
    fill: "#EEF6F4",
    font: { color: "#153243", bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: "#B7C8C5" },
    wrapText: true,
  };
}

function colName(indexOneBased) {
  let n = indexOneBased;
  let name = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

function drawLogTimePanel(sheet, { startRow, startCol, title, rows, minLog, maxLog, barCols = 12 }) {
  const titleEnd = colName(startCol + 2 + barCols);
  sheet.getRange(`${colName(startCol)}${startRow}:${titleEnd}${startRow}`).merge();
  sheet.getRange(`${colName(startCol)}${startRow}:${titleEnd}${startRow}`).values = [[title]];
  sheet.getRange(`${colName(startCol)}${startRow}:${titleEnd}${startRow}`).format = {
    fill: "#153243",
    font: { color: "#FFFFFF", bold: true, size: 12 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };

  const headerRow = startRow + 1;
  const headerEnd = colName(startCol + 2 + barCols);
  sheet.getRange(`${colName(startCol)}${headerRow}:${headerEnd}${headerRow}`).values = [[
    "Condition",
    "Method",
    "Time",
    ...Array.from({ length: barCols }, (_, i) => `${i + 1}`),
  ]];
  sheet.getRange(`${colName(startCol)}${headerRow}:${headerEnd}${headerRow}`).format = {
    fill: "#D8EDE9",
    font: { color: "#153243", bold: true, size: 9 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: "#B7C8C5" },
  };

  rows.forEach((row, idx) => {
    const r = startRow + 2 + idx;
    const logValue = row.isInfinity ? maxLog : Math.log10(row.time);
    const normalized = Math.max(0, Math.min(1, (logValue - minLog) / (maxLog - minLog)));
    const filled = row.isInfinity ? barCols : Math.max(1, Math.round(normalized * barCols));
    const methodColor = row.method === "Base" ? "#153243" : row.method === "Lap-6" ? "#2E6F73" : row.method === "Lap-8" ? "#84A98C" : "#C1666B";
    sheet.getRange(`${colName(startCol)}${r}:${colName(startCol + 2)}${r}`).values = [[row.condition, row.method, row.label]];
    sheet.getRange(`${colName(startCol)}${r}:${colName(startCol + 2)}${r}`).format = {
      fill: idx % 2 === 0 ? "#FFFFFF" : "#F7FAFA",
      font: { color: "#153243", size: 9, bold: row.method === "Base" },
      horizontalAlignment: "center",
      verticalAlignment: "center",
      borders: { preset: "outside", style: "thin", color: "#DEE7E6" },
      wrapText: true,
    };
    const barStart = startCol + 3;
    const barEnd = startCol + 2 + barCols;
    sheet.getRange(`${colName(barStart)}${r}:${colName(barEnd)}${r}`).format = {
      fill: "#EEF2F2",
      borders: { preset: "outside", style: "thin", color: "#E2E8E7" },
    };
    sheet.getRange(`${colName(barStart)}${r}:${colName(barStart + filled - 1)}${r}`).format = {
      fill: methodColor,
      borders: { preset: "outside", style: "thin", color: "#FFFFFF" },
    };
  });
}

put(sheetA, "A1:T1", [["N", "Trap", "Condition", "Base Profit %", "Base Profit SD", "Base Time ms", "Base Time SD", "Theory L6 %", "Lap-6 Profit %", "Lap-6 Opt %", "Lap-6 Time ms", "Lap-6 Time SD", "Theory L8 %", "Lap-8 Profit %", "Lap-8 Opt %", "Lap-8 Time ms", "Lap-8 Time SD", "SVD-8 Profit %", "SVD-8 Opt %", "SVD-8 Time ms"]]);
put(sheetA, "A2:T5", expA.map(r => [r.n, r.trap, r.condition, r.baseProfit, r.baseProfitSd, r.baseTime, r.baseTimeSd, r.theoryL6, r.lap6Profit, r.lap6Opt, r.lap6Time, r.lap6TimeSd, r.theoryL8, r.lap8Profit, r.lap8Opt, r.lap8Time, r.lap8TimeSd, r.svd8Profit, r.svd8Opt, r.svd8Time]));
styleHeader(sheetA, "A1:T1");
styleBody(sheetA, "A2:T5");
sheetA.getRange("A1:T5").format.autofitColumns();
sheetA.getRange("D2:T5").format.numberFormat = "0.00";

put(sheetB, "A1:V1", [["N", "Trap", "Condition", "Base Est Time", "Theory L6 %", "Lap-6 Profit %", "Lap-6 Profit SD", "Lap-6 Opt %", "Lap-6 Time ms", "Lap-6 Time SD", "Theory L8 %", "Lap-8 Profit %", "Lap-8 Profit SD", "Lap-8 Opt %", "Lap-8 Time ms", "Lap-8 Time SD", "SVD-8 Profit %", "SVD-8 Profit SD", "SVD-8 Opt %", "SVD-8 Time ms", "SVD-8 Time SD", "Best Method"]]);
put(sheetB, "A2:V7", expB.map(r => {
  const opts = [["Lap-6", r.lap6Opt], ["Lap-8", r.lap8Opt], ["SVD-8", r.svd8Opt]];
  opts.sort((a, b) => b[1] - a[1]);
  return [r.n, r.trap, r.condition, r.baseEst, r.theoryL6, r.lap6Profit, r.lap6ProfitSd, r.lap6Opt, r.lap6Time, r.lap6TimeSd, r.theoryL8, r.lap8Profit, r.lap8ProfitSd, r.lap8Opt, r.lap8Time, r.lap8TimeSd, r.svd8Profit, r.svd8ProfitSd, r.svd8Opt, r.svd8Time, r.svd8TimeSd, opts[0][0]];
}));
styleHeader(sheetB, "A1:V1");
styleBody(sheetB, "A2:V7");
sheetB.getRange("A1:V7").format.autofitColumns();
sheetB.getRange("E2:U7").format.numberFormat = "0.00";

const smallOptRows = [["Condition", "Lap-6 Opt %", "Lap-8 Opt %", "SVD-8 Opt %"], ...expA.map(r => [r.condition, r.lap6Opt, r.lap8Opt, r.svd8Opt])];
const smallTimeRows = [["Condition", "Base Time ms", "Lap-6 Time ms", "Lap-8 Time ms", "SVD-8 Time ms"], ...expA.map(r => [r.condition, r.baseTime, r.lap6Time, r.lap8Time, r.svd8Time])];
const largeOptRows = [["Condition", "Lap-6 Opt %", "Lap-8 Opt %", "SVD-8 Opt %"], ...expB.map(r => [r.condition, r.lap6Opt, r.lap8Opt, r.svd8Opt])];
const largeTimeRows = [["Condition", "Base Time", "Lap-6 Time ms", "Lap-8 Time ms", "SVD-8 Time ms"], ...expB.map(r => [r.condition, largeBaseTimeCapMs, r.lap6Time, r.lap8Time, r.svd8Time])];
const theoryRows = [["N", "Theory L8 %", "Lap-8 No-trap Profit %", "SVD-8 No-trap Profit %"], ...expB.filter(r => r.trap === "False").map(r => [r.n, r.theoryL8, r.lap8Profit, r.svd8Profit])];
const trapRows = [["N", "Lap-8 No trap %", "Lap-8 Trap %", "SVD-8 No trap %", "SVD-8 Trap %"], ...[50, 100, 200].map(n => {
  const noTrap = expB.find(r => r.n === n && r.trap === "False");
  const trap = expB.find(r => r.n === n && r.trap === "True");
  return [n, noTrap.lap8Profit, trap.lap8Profit, noTrap.svd8Profit, trap.svd8Profit];
})];

put(chartData, "A1:D5", smallOptRows);
put(chartData, "F1:J5", smallTimeRows);
put(chartData, "A8:D14", largeOptRows);
put(chartData, "F8:J14", largeTimeRows);
put(chartData, "K8:N11", theoryRows);
put(chartData, "P8:T11", trapRows);
styleHeader(chartData, "A1:D1");
styleHeader(chartData, "F1:J1");
styleHeader(chartData, "A8:D8");
styleHeader(chartData, "F8:J8");
styleHeader(chartData, "K8:N8");
styleHeader(chartData, "P8:T8");
styleBody(chartData, "A2:D5");
styleBody(chartData, "F2:J5");
styleBody(chartData, "A9:D14");
styleBody(chartData, "F9:J14");
styleBody(chartData, "K9:N11");
styleBody(chartData, "P9:T11");
chartData.getRange("A1:T14").format.autofitColumns();
chartData.getRange("B2:T14").format.numberFormat = "0.00";

put(dashboard, "A1:H1", [["基于线性代数剪枝的套利回路搜索可视化"]]);
dashboard.getRange("A1:H1").merge();
styleTitle(dashboard, "A1:H1");
dashboard.getRange("A2:H2").values = [["数据来源：report/5.md 中重复 5 次重新生成的实验结果；图表按报告“全图基准 -> 线性代数热点节点 -> 诱导子图 DFS”的论证顺序组织。", "", "", "", "", "", "", ""]];
dashboard.getRange("A2:H2").merge();
dashboard.getRange("A2:H2").format = { fill: "#F7FAFA", font: { color: "#415A5B", italic: true }, wrapText: true, verticalAlignment: "center" };

put(dashboard, "A4:D6", [
  ["小规模基准", "N=10 全图 DFS", "Lap-6 最快耗时", "大规模基准"],
  ["可精确比较收益", "约 1.35 秒", "约 0.4 ms", "50+ 节点全图不可算"],
  ["收益保留率衡量剪枝质量", "用于时间对比", "速度优势最明显", "用理论值与剪枝结果参照"],
]);
styleKpi(dashboard, "A4:D6");
dashboard.getRange("A4:D4").format.fill = "#D8EDE9";
dashboard.getRange("A5:D5").format.font = { color: "#153243", bold: true, size: 13 };

dashboard.charts.add("column", {
  title: "实验 A：小规模收益保留率",
  categories: expA.map(r => r.condition),
  series: [
    { name: "Lap-6", values: expA.map(r => r.lap6Opt), fill: { type: "solid", color: "#2E6F73" } },
    { name: "Lap-8", values: expA.map(r => r.lap8Opt), fill: { type: "solid", color: "#84A98C" } },
    { name: "SVD-8", values: expA.map(r => r.svd8Opt), fill: { type: "solid", color: "#C1666B" } },
  ],
  hasLegend: true,
  legend: { position: "bottom", textStyle: { fontSize: 10 } },
  yAxis: { title: { text: "Opt retained (%)" }, numberFormatCode: "0" },
  xAxis: { textStyle: { fontSize: 9 } },
  dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 8 } },
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 70 },
  from: { row: 8, col: 1 },
  extent: { widthPx: 560, heightPx: 300 },
});

drawLogTimePanel(dashboard, {
  startRow: 9,
  startCol: 9,
  title: "实验 A：小规模运行时间对比（条长按 log10(ms)）",
  minLog: Math.log10(0.3),
  maxLog: Math.log10(Math.max(...expA.map(r => r.baseTime))),
  barCols: 11,
  rows: expA.flatMap(r => [
    { condition: r.condition, method: "Base", time: r.baseTime, label: `${r.baseTime.toFixed(2)} ms` },
    { condition: r.condition, method: "Lap-6", time: r.lap6Time, label: `${r.lap6Time.toFixed(2)} ms` },
    { condition: r.condition, method: "Lap-8", time: r.lap8Time, label: `${r.lap8Time.toFixed(2)} ms` },
    { condition: r.condition, method: "SVD-8", time: r.svd8Time, label: `${r.svd8Time.toFixed(2)} ms` },
  ]),
});

dashboard.charts.add("column", {
  title: "实验 B：大规模诱导子图收益保留率",
  categories: expB.map(r => r.condition),
  series: [
    { name: "Lap-6", values: expB.map(r => r.lap6Opt), fill: { type: "solid", color: "#2E6F73" } },
    { name: "Lap-8", values: expB.map(r => r.lap8Opt), fill: { type: "solid", color: "#84A98C" } },
    { name: "SVD-8", values: expB.map(r => r.svd8Opt), fill: { type: "solid", color: "#C1666B" } },
  ],
  hasLegend: true,
  legend: { position: "bottom", textStyle: { fontSize: 10 } },
  yAxis: { title: { text: "Opt retained (%)" }, numberFormatCode: "0" },
  xAxis: { textStyle: { fontSize: 8 } },
  dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 7 } },
  barOptions: { direction: "column", grouping: "clustered", gapWidth: 70 },
  from: { row: 25, col: 1 },
  extent: { widthPx: 560, heightPx: 300 },
});

dashboard.charts.add("line", {
  title: "实验 B：无 Trap 场景理论参考与剪枝收益",
  categories: expB.filter(r => r.trap === "False").map(r => String(r.n)),
  series: [
    { name: "理论 L=8", values: expB.filter(r => r.trap === "False").map(r => r.theoryL8), line: { fill: "#153243", style: "dashed", width: 2 } },
    { name: "Lap-8 实测", values: expB.filter(r => r.trap === "False").map(r => r.lap8Profit), line: { fill: "#84A98C", style: "solid", width: 2 } },
    { name: "SVD-8 实测", values: expB.filter(r => r.trap === "False").map(r => r.svd8Profit), line: { fill: "#C1666B", style: "solid", width: 2 } },
  ],
  hasLegend: true,
  legend: { position: "bottom", textStyle: { fontSize: 10 } },
  yAxis: { title: { text: "Profit (%)" }, numberFormatCode: "0.0" },
  xAxis: { title: { text: "N" } },
  dataLabels: { showValue: true, position: "outEnd", textStyle: { fontSize: 8 } },
  from: { row: 27, col: 9 },
  extent: { widthPx: 560, heightPx: 300 },
});

drawLogTimePanel(dashboard, {
  startRow: 43,
  startCol: 1,
  title: "实验 B：大规模运行时间对比（Base = ∞，条形顶格）",
  minLog: Math.log10(0.3),
  maxLog: Math.log10(largeBaseTimeCapMs),
  barCols: 13,
  rows: expB.flatMap(r => [
    { condition: r.condition, method: "Base", time: largeBaseTimeCapMs, label: "∞", isInfinity: true },
    { condition: r.condition, method: "Lap-6", time: r.lap6Time, label: `${r.lap6Time.toFixed(2)} ms` },
    { condition: r.condition, method: "Lap-8", time: r.lap8Time, label: `${r.lap8Time.toFixed(2)} ms` },
    { condition: r.condition, method: "SVD-8", time: r.svd8Time, label: `${r.svd8Time.toFixed(2)} ms` },
  ]),
});

put(notes, "A1:D1", [["图表", "对应报告思路", "主要读法", "数据来源"]]);
put(notes, "A2:D6", [
  ["实验 A 收益保留率", "小规模全图 DFS 可作为精确基准", "Lap-8/SVD-8 在 N=8 基本达到 100%，N=10 时仍保留较高收益", "5.md 实验 A"],
  ["实验 A 时间对比", "剪枝后在诱导子图搜索，避免全图简单环枚举", "对数时间轴显示 Base 与剪枝耗时；Lap-6 的毫秒级优势最明显", "5.md 实验 A"],
  ["实验 B 收益保留率", "大规模全图 DFS 不可计算，比较剪枝方法之间的相对表现", "Lap-8 在多数大规模设置中达到最高或接近最高保留率", "5.md 实验 B"],
  ["理论与实测收益", "随机噪声背景下用概率论理论值作为参照", "无 trap 时理论最优高于剪枝实测，说明剪枝是在极小子图中近似搜索", "5.md 实验 B"],
  ["实验 B 时间对比", "大规模全图 DFS 的估算时间不可实际运行", "Base 以 ∞ 顶格显示，剪枝方法仍保持约 0.4 ms 或 18 ms", "5.md 实验 B"],
]);
styleHeader(notes, "A1:D1");
styleBody(notes, "A2:D6");
notes.getRange("A1:D6").format.autofitColumns();

for (const sheet of [dashboard, sheetA, sheetB, chartData, notes]) {
  sheet.getRange("A1:V75").format.font = { name: "Aptos", size: 10 };
}
dashboard.getRange("A:A").format.columnWidthPx = 120;
dashboard.getRange("B:D").format.columnWidthPx = 150;
dashboard.getRange("I:I").format.columnWidthPx = 120;
dashboard.getRange("J:J").format.columnWidthPx = 72;
dashboard.getRange("K:K").format.columnWidthPx = 90;
dashboard.getRange("L:V").format.columnWidthPx = 24;
dashboard.getRange("A1:H2").format.rowHeight = 28;

await fs.mkdir(outputDir, { recursive: true });

const dashboardPreview = await workbook.render({ sheetName: "Dashboard", range: "A1:V72", scale: 1.5 });
await fs.writeFile(`${outputDir}/dashboard_preview.png`, Buffer.from(await dashboardPreview.arrayBuffer()));
const expAPreview = await workbook.render({ sheetName: "Experiment A", range: "A1:T7", scale: 1.5 });
await fs.writeFile(`${outputDir}/experiment_a_preview.png`, Buffer.from(await expAPreview.arrayBuffer()));
const expBPreview = await workbook.render({ sheetName: "Experiment B", range: "A1:V9", scale: 1.5 });
await fs.writeFile(`${outputDir}/experiment_b_preview.png`, Buffer.from(await expBPreview.arrayBuffer()));
const notesPreview = await workbook.render({ sheetName: "Notes", range: "A1:D8", scale: 1.5 });
await fs.writeFile(`${outputDir}/notes_preview.png`, Buffer.from(await notesPreview.arrayBuffer()));

const errorScan = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "formula error scan",
});
console.log(errorScan.ndjson);

const dashboardCheck = await workbook.inspect({
  kind: "table",
  range: "Dashboard!A1:H6",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 8,
});
console.log(dashboardCheck.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
