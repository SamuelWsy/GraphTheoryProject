import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/Users/wangsiyan/Courses/面计离散/proj/outputs/v7_structured_workbook";
const outputPath = `${outputDir}/experiment_v7_structured_results.xlsx`;

const metadata = [
  ["Field", "Value"],
  ["Source file", "experiment_v7_results_2026-06-05.md"],
  ["Source script", "experiment_v7_theory_ratio.py"],
  ["Run date", "2026-06-05"],
  ["Included sections", "Experiment A; Experiment B"],
  ["Excluded section", "Trapped Expectation 诊断：理论最大项来源"],
  ["Profit unit", "percentage points"],
  ["Ratio unit", "percentage points"],
  ["Time unit", "milliseconds unless a header says Log10Years"],
];

const expAHeaders = [
  "N",
  "Trap",
  "BaseProfitMeanPct",
  "BaseProfitStdPct",
  "BaseTimeMeanMs",
  "BaseTimeStdMs",
  "TheoryLEQ6ProfitPct",
  "Lap6ProfitMeanPct",
  "Lap6ProfitStdPct",
  "Lap6ProfitOverBaseProfitMeanPct",
  "Lap6ProfitOverBaseProfitStdPct",
  "Lap6TimeMeanMs",
  "Lap6TimeStdMs",
  "TheoryLEQ8ProfitPct",
  "Lap8ProfitMeanPct",
  "Lap8ProfitStdPct",
  "Lap8ProfitOverBaseProfitMeanPct",
  "Lap8ProfitOverBaseProfitStdPct",
  "Lap8TimeMeanMs",
  "Lap8TimeStdMs",
  "SVD8ProfitMeanPct",
  "SVD8ProfitStdPct",
  "SVD8ProfitOverBaseProfitMeanPct",
  "SVD8ProfitOverBaseProfitStdPct",
  "SVD8TimeMeanMs",
  "SVD8TimeStdMs",
];

const expARows = [
  [8, false, 2.590, 0.34, 17.99, 0.13, 2.888, 1.900, 0.27, 73.5, 5.7, 0.41, 0.01, 3.426, 2.590, 0.34, 100.0, 0.0, 17.94, 0.22, 2.590, 0.34, 100.0, 0.0, 18.03, 0.25],
  [8, true, 13.853, 0.26, 18.33, 0.48, 13.746, 13.162, 0.26, 95.0, 1.9, 0.41, 0.00, 14.330, 13.853, 0.26, 100.0, 0.0, 18.02, 0.23, 13.853, 0.26, 100.0, 0.0, 17.91, 0.10],
  [10, false, 3.516, 0.42, 1364.96, 25.79, 3.232, 2.067, 0.40, 58.4, 5.7, 0.43, 0.04, 4.135, 2.884, 0.38, 82.0, 4.8, 17.92, 0.28, 2.561, 0.33, 73.1, 8.2, 17.97, 0.27],
  [10, true, 15.147, 0.24, 1352.51, 10.30, 13.961, 13.039, 0.23, 86.1, 0.6, 0.40, 0.00, 15.003, 14.079, 0.42, 92.9, 1.4, 17.67, 0.14, 14.329, 0.26, 94.6, 1.0, 17.78, 0.13],
];

const expBHeaders = [
  "N",
  "Trap",
  "BaseTimeEstLog10Years",
  "BaseTimeEstText",
  "TheoryLEQ6ProfitPct",
  "Lap6ProfitMeanPct",
  "Lap6ProfitStdPct",
  "Lap6ProfitOverTheoryLEQ6ProfitMeanPct",
  "Lap6ProfitOverTheoryLEQ6ProfitStdPct",
  "Lap6TimeMeanMs",
  "Lap6TimeStdMs",
  "TheoryLEQ8ProfitPct",
  "Lap8ProfitMeanPct",
  "Lap8ProfitStdPct",
  "Lap8ProfitOverTheoryLEQ8ProfitMeanPct",
  "Lap8ProfitOverTheoryLEQ8ProfitStdPct",
  "Lap8TimeMeanMs",
  "Lap8TimeStdMs",
  "SVD8ProfitMeanPct",
  "SVD8ProfitStdPct",
  "SVD8ProfitOverTheoryLEQ8ProfitMeanPct",
  "SVD8ProfitOverTheoryLEQ8ProfitStdPct",
  "SVD8TimeMeanMs",
  "SVD8TimeStdMs",
];

const expBRows = [
  [50, false, 49, "约 10^49 年", 4.729, 2.224, 0.12, 47.0, 2.5, 0.43, 0.01, 6.369, 3.037, 0.18, 47.7, 2.9, 17.55, 0.12, 3.132, 0.22, 49.2, 3.4, 17.57, 0.17],
  [50, true, 49, "约 10^49 年", 14.704, 12.670, 0.42, 86.2, 2.9, 0.43, 0.01, 16.557, 13.808, 0.61, 83.4, 3.7, 17.53, 0.11, 14.440, 0.28, 87.2, 1.7, 17.51, 0.20],
  [100, false, 143, "约 10^143 年", 5.196, 1.970, 0.45, 37.9, 8.7, 0.44, 0.01, 7.011, 2.979, 0.38, 42.5, 5.4, 18.00, 0.28, 3.117, 0.17, 44.4, 2.5, 17.80, 0.16],
  [100, true, 143, "约 10^143 年", 14.913, 13.007, 0.41, 87.2, 2.8, 0.44, 0.01, 16.950, 13.961, 0.10, 82.4, 0.6, 17.89, 0.29, 13.968, 0.27, 82.4, 1.6, 17.82, 0.19],
  [200, false, 359, "约 10^359 年", 5.620, 2.060, 0.25, 36.7, 4.4, 0.47, 0.01, 7.589, 2.908, 0.31, 38.3, 4.1, 17.92, 0.11, 2.855, 0.18, 37.6, 2.4, 17.89, 0.23],
  [200, true, 359, "约 10^359 年", 15.099, 13.106, 0.27, 86.8, 1.8, 0.47, 0.01, 17.299, 14.014, 0.33, 81.0, 1.9, 17.74, 0.16, 14.366, 0.44, 83.0, 2.6, 17.77, 0.17],
];

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

function rangeAddress(startRow, startCol, rowCount, colCount) {
  const endRow = startRow + rowCount - 1;
  const endCol = startCol + colCount - 1;
  return `${colName(startCol)}${startRow}:${colName(endCol)}${endRow}`;
}

function writeTable(sheet, startRow, startCol, headers, rows) {
  const values = [headers, ...rows];
  const range = rangeAddress(startRow, startCol, values.length, headers.length);
  sheet.getRange(range).values = values;

  const headerRange = rangeAddress(startRow, startCol, 1, headers.length);
  sheet.getRange(headerRange).format = {
    fill: "#1F4E5F",
    font: { color: "#FFFFFF", bold: true },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: "#AFC2C8" },
  };

  const bodyRange = rangeAddress(startRow + 1, startCol, rows.length, headers.length);
  sheet.getRange(bodyRange).format = {
    verticalAlignment: "center",
    wrapText: false,
    borders: { preset: "outside", style: "thin", color: "#D8E2E7" },
  };
  sheet.getRange(range).format.autofitColumns();
  return range;
}

function styleTitle(sheet, range, text) {
  sheet.getRange(range).values = [[text]];
  sheet.getRange(range).format = {
    fill: "#DDEBF0",
    font: { bold: true, color: "#173A46", size: 13 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
}

const workbook = Workbook.create();
const readme = workbook.worksheets.add("README");
const sheetA = workbook.worksheets.add("Experiment_A_Small");
const sheetB = workbook.worksheets.add("Experiment_B_Large");

styleTitle(readme, "A1:B1", "Experiment v7 Structured Workbook");
writeTable(readme, 3, 1, metadata[0], metadata.slice(1));
readme.getRange("A1:B1").format.autofitColumns();

styleTitle(sheetA, "A1:Z1", "Experiment A: Small-Scale Absolute Accuracy and Runtime");
writeTable(sheetA, 3, 1, expAHeaders, expARows);
sheetA.getRange("C4:Z7").format.numberFormat = "0.00";
sheetA.getRange("A3:Z7").format.autofitColumns();

styleTitle(sheetB, "A1:X1", "Experiment B: Large-Scale Hard-Constrained Induced-Subgraph Experiment");
writeTable(sheetB, 3, 1, expBHeaders, expBRows);
sheetB.getRange("C4:C9").format.numberFormat = "0";
sheetB.getRange("E4:X9").format.numberFormat = "0.00";
sheetB.getRange("A3:X9").format.autofitColumns();

for (const sheet of [readme, sheetA, sheetB]) {
  sheet.getRange("A1:Z40").format.font = { name: "Aptos", size: 10 };
}

await fs.mkdir(outputDir, { recursive: true });

const inspectA = await workbook.inspect({
  kind: "table",
  range: "Experiment_A_Small!A3:Z7",
  include: "values",
  tableMaxRows: 6,
  tableMaxCols: 26,
});
console.log(inspectA.ndjson);

const inspectB = await workbook.inspect({
  kind: "table",
  range: "Experiment_B_Large!A3:X9",
  include: "values",
  tableMaxRows: 8,
  tableMaxCols: 24,
});
console.log(inspectB.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

const previewA = await workbook.render({ sheetName: "Experiment_A_Small", range: "A1:Z7", scale: 1.5 });
await fs.writeFile(`${outputDir}/experiment_a_preview.png`, Buffer.from(await previewA.arrayBuffer()));
const previewB = await workbook.render({ sheetName: "Experiment_B_Large", range: "A1:X9", scale: 1.5 });
await fs.writeFile(`${outputDir}/experiment_b_preview.png`, Buffer.from(await previewB.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
