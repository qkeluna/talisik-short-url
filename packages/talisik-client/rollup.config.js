const resolve = require("@rollup/plugin-node-resolve");
const commonjs = require("@rollup/plugin-commonjs");
const typescript = require("@rollup/plugin-typescript");
const dts = require("rollup-plugin-dts");

const packageJson = require("./package.json");

module.exports = [
  // ESM and CommonJS builds
  {
    input: "src/index.ts",
    output: [
      {
        file: packageJson.main,
        format: "cjs",
        sourcemap: true,
      },
      {
        file: packageJson.module,
        format: "esm",
        sourcemap: true,
      },
    ],
    plugins: [
      resolve.default({
        browser: true,
        preferBuiltins: false,
      }),
      commonjs.default(),
      typescript.default({
        tsconfig: "./tsconfig.json",
        declaration: true,
        declarationMap: true,
        outDir: "./dist",
      }),
    ],
    external: ["react", "react-dom"],
  },
  // Type declarations
  {
    input: "src/index.ts",
    output: [{ file: "dist/index.d.ts", format: "esm" }],
    plugins: [dts.default()],
    external: [/\.css$/],
  },
];
