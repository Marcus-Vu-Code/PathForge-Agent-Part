import { copyFile, mkdir } from "node:fs/promises";
import { resolve } from "node:path";

const workerFiles = ["index.js", "career-taxonomy.js"];
const targetDirectory = resolve("dist/server");

await mkdir(targetDirectory, { recursive: true });
await Promise.all(
  workerFiles.map((filename) => copyFile(resolve("worker", filename), resolve(targetDirectory, filename)))
);
