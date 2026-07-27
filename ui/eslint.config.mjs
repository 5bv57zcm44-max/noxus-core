import babelParser from "@babel/eslint-parser";
import eslint from "@eslint/js";
import hooks from "eslint-plugin-react-hooks";
import globals from "globals";

export default [
  { ignores: ["dist", "coverage", "playwright-report"] },
  eslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: babelParser,
      parserOptions: {
        requireConfigFile: false,
        babelOptions: { presets: ["@babel/preset-typescript", ["@babel/preset-react", { runtime: "automatic" }]] },
      },
      globals: { ...globals.browser, ...globals.node },
    },
    plugins: { "react-hooks": hooks },
    rules: { ...hooks.configs.recommended.rules, "no-unused-vars": "off", "no-undef": "off" },
  },
];
