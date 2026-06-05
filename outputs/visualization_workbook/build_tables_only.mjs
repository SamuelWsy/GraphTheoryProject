import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/Users/wangsiyan/Courses/面计离散/proj/outputs/visualization_workbook";
const outputPath = `${outputDir}/arbitrage_pruning_visualization.xlsx`;

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
const summary = workbook.worksheets.add("Read Me");
const ready = workbook.worksheets.add("Chart Ready");
const sheetA = workbook.worksheets.add("Experiment A Raw");
const sheetB = workbook.worksheets.add("Experiment B Raw");

function put(sheet, address, values) {
  sheet.getRange(address).values = values;
}

function header(sheet, range) {
  sheet.getRange(range).format = {
    fill: "#1F4E5F",
    font: { color: "#FFFFFF", bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: "#BFCAD0" },
  };
}

function body(sheet, range) {
  sheet.getRange(range).format = {
    borders: { preset: "outside", style: "thin", color: "#D9E2E7" },
    verticalAlignment: "center",
    wrapText: true,
  };
}

function title(sheet, range, text) {
  sheet.getRange(range).values = [[text]];
  sheet.getRange(range).format = {
    fill: "#DDEBF0",
    font: { color: "#173A46", bold: true, size: 12 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
}

function addBlock(sheet, startCell, blockTitle, rows, numberRange) {
  title(sheet, startCell, blockTitle);
  const col = startCell.match(/[A-Z]+/)[0];
  const row = Number(startCell.match(/\d+/)[0]) + 1;
  const width = rows[0].length;
  const height = rows.length;
  const endCol = String.fromCharCode(col.charCodeAt(0) + width - 1);
  put(sheet, `${col}${row}:${endCol}${row + height - 1}`, rows);
  header(sheet, `${col}${row}:${endCol}${row}`);
  body(sheet, `${col}${row + 1}:${endCol}${row + height - 1}`);
  if (numberRange) sheet.getRange(numberRange).format.numberFormat = "0.00";
}

put(summary, "A1:D1", [["用途", "建议图表", "可选数据区域", "备注"]]);
put(summary, "A2:D7", [
  ["小规模收益保留率", "簇状柱形图", "Chart Ready!A2:D6", "展示 Lap-6/Lap-8/SVD-8 相对全图 DFS 的最优收益保留率"],
  ["小规模运行时间", "簇状柱形图；纵轴可手动设为对数坐标", "Chart Ready!F2:J6", "展示 Base 与三种剪枝方法的 ms 时间"],
  ["大规模收益保留率", "簇状柱形图", "Chart Ready!A10:D16", "全图 DFS 不可运行，比较剪枝方法之间的保留率"],
  ["大规模运行时间", "簇状柱形图；Base 可手动标注为 ∞", "Chart Ready!F10:J16", "Base Height 列只用于让 Base 柱顶格，Base Label 列保留文字标注"],
  ["无 Trap 理论参考", "折线图", "Chart Ready!A20:D23", "比较理论 L=8 与 Lap-8/SVD-8 实测利润"],
  ["Trap 对利润影响", "折线图或簇状柱形图", "Chart Ready!F20:J23", "比较 No trap 与 Trap 下的利润"],
]);
header(summary, "A1:D1");
body(summary, "A2:D7");
summary.getRange("A1:D7").format.autofitColumns();

addBlock(ready, "A1", "1. 实验 A：小规模收益保留率（%）", [
  ["Condition", "Lap-6 Opt %", "Lap-8 Opt %", "SVD-8 Opt %"],
  ...expA.map(r => [r.condition, r.lap6Opt, r.lap8Opt, r.svd8Opt]),
], "B3:D6");

addBlock(ready, "F1", "2. 实验 A：小规模运行时间（ms）", [
  ["Condition", "Base Time ms", "Lap-6 Time ms", "Lap-8 Time ms", "SVD-8 Time ms"],
  ...expA.map(r => [r.condition, r.baseTime, r.lap6Time, r.lap8Time, r.svd8Time]),
], "G3:J6");

addBlock(ready, "A9", "3. 实验 B：大规模收益保留率（%）", [
  ["Condition", "Lap-6 Opt %", "Lap-8 Opt %", "SVD-8 Opt %"],
  ...expB.map(r => [r.condition, r.lap6Opt, r.lap8Opt, r.svd8Opt]),
], "B11:D16");

addBlock(ready, "F9", "4. 实验 B：大规模运行时间（ms）", [
  ["Condition", "Base Label", "Base Height", "Lap-6 Time ms", "Lap-8 Time ms", "SVD-8 Time ms"],
  ...expB.map(r => [r.condition, "∞", 100000, r.lap6Time, r.lap8Time, r.svd8Time]),
], "H11:K16");

addBlock(ready, "A19", "5. 无 Trap 场景：理论参考与实测利润（%）", [
  ["N", "Theory L8 %", "Lap-8 Profit %", "SVD-8 Profit %"],
  ...expB.filter(r => r.trap === "False").map(r => [r.n, r.theoryL8, r.lap8Profit, r.svd8Profit]),
], "B21:D23");

addBlock(ready, "F19", "6. Trap 对利润的影响（%）", [
  ["N", "Lap-8 No trap %", "Lap-8 Trap %", "SVD-8 No trap %", "SVD-8 Trap %"],
  ...[50, 100, 200].map(n => {
    const noTrap = expB.find(r => r.n === n && r.trap === "False");
    const trap = expB.find(r => r.n === n && r.trap === "True");
    return [n, noTrap.lap8Profit, trap.lap8Profit, noTrap.svd8Profit, trap.svd8Profit];
  }),
], "G21:J23");

ready.getRange("A1:K23").format.autofitColumns();

put(sheetA, "A1:T1", [["N", "Trap", "Condition", "Base Profit %", "Base Profit SD", "Base Time ms", "Base Time SD", "Theory L6 %", "Lap-6 Profit %", "Lap-6 Opt %", "Lap-6 Time ms", "Lap-6 Time SD", "Theory L8 %", "Lap-8 Profit %", "Lap-8 Opt %", "Lap-8 Time ms", "Lap-8 Time SD", "SVD-8 Profit %", "SVD-8 Opt %", "SVD-8 Time ms"]]);
put(sheetA, "A2:T5", expA.map(r => [r.n, r.trap, r.condition, r.baseProfit, r.baseProfitSd, r.baseTime, r.baseTimeSd, r.theoryL6, r.lap6Profit, r.lap6Opt, r.lap6Time, r.lap6TimeSd, r.theoryL8, r.lap8Profit, r.lap8Opt, r.lap8Time, r.lap8TimeSd, r.svd8Profit, r.svd8Opt, r.svd8Time]));
header(sheetA, "A1:T1");
body(sheetA, "A2:T5");
sheetA.getRange("D2:T5").format.numberFormat = "0.00";
sheetA.getRange("A1:T5").format.autofitColumns();

put(sheetB, "A1:V1", [["N", "Trap", "Condition", "Base Est Time", "Theory L6 %", "Lap-6 Profit %", "Lap-6 Profit SD", "Lap-6 Opt %", "Lap-6 Time ms", "Lap-6 Time SD", "Theory L8 %", "Lap-8 Profit %", "Lap-8 Profit SD", "Lap-8 Opt %", "Lap-8 Time ms", "Lap-8 Time SD", "SVD-8 Profit %", "SVD-8 Profit SD", "SVD-8 Opt %", "SVD-8 Time ms", "SVD-8 Time SD", "Best Method"]]);
put(sheetB, "A2:V7", expB.map(r => {
  const opts = [["Lap-6", r.lap6Opt], ["Lap-8", r.lap8Opt], ["SVD-8", r.svd8Opt]].sort((a, b) => b[1] - a[1]);
  return [r.n, r.trap, r.condition, r.baseEst, r.theoryL6, r.lap6Profit, r.lap6ProfitSd, r.lap6Opt, r.lap6Time, r.lap6TimeSd, r.theoryL8, r.lap8Profit, r.lap8ProfitSd, r.lap8Opt, r.lap8Time, r.lap8TimeSd, r.svd8Profit, r.svd8ProfitSd, r.svd8Opt, r.svd8Time, r.svd8TimeSd, opts[0][0]];
}));
header(sheetB, "A1:V1");
body(sheetB, "A2:V7");
sheetB.getRange("E2:U7").format.numberFormat = "0.00";
sheetB.getRange("A1:V7").format.autofitColumns();

for (const sheet of [summary, ready, sheetA, sheetB]) {
  sheet.getRange("A1:V40").format.font = { name: "Aptos", size: 10 };
}

await fs.mkdir(outputDir, { recursive: true });
const preview = await workbook.render({ sheetName: "Chart Ready", range: "A1:K24", scale: 1.5 });
await fs.writeFile(`${outputDir}/chart_ready_preview.png`, Buffer.from(await preview.arrayBuffer()));
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "formula error scan",
});
console.log(errors.ndjson);
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
