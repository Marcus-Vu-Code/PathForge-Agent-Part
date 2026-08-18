import { copyFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const source = resolve("worker/index.js");
const target = resolve("dist/server/index.js");

await mkdir(dirname(target), { recursive: true });
await copyFile(source, target);
