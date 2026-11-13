"""Keep checklist articles within the exact released terraphim-agent surface."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "scripts/tests/fixtures/terraphim-agent-v1.21.22"
ARTICLES = (
    ROOT / "content/posts/graph-embeddings-checklists.md",
    ROOT / "content/posts/kg-concepts-code-checklists.md",
)
FENCED_BLOCK_RE = re.compile(
    r"^[ ]{0,3}```([^\n]*)\n(.*?)\n^[ ]{0,3}```[ \t]*$",
    flags=re.DOTALL | re.MULTILINE,
)


def released_commands_in_help(help_text):
    block = help_text.split("Commands:\n", 1)[1].split("\n\nOptions:", 1)[0]
    return {line.split()[0] for line in block.splitlines() if line.startswith("  ")}


def executable_agent_commands(page):
    commands = set()
    fenced = [block for _, block in FENCED_BLOCK_RE.findall(page)]
    prose = FENCED_BLOCK_RE.sub("", page)
    imperative_prose = [
        match.group(0)
        for match in re.finditer(
            r"\b(?:execute|use|invoke|try|run)[ \t]+`{0,2}terraphim-agent\b[^\n]*",
            prose,
            flags=re.IGNORECASE,
        )
    ]
    for block in (*fenced, *imperative_prose):
        normalized = block.replace("\\\n", " ")
        for match in re.finditer(r"\bterraphim-agent\b([^\n]*)", normalized):
            tokens = shlex.split(match.group(1))
            index = 0
            while index < len(tokens):
                token = tokens[index]
                if token in ("--server", "--transparent", "--robot"):
                    index += 1
                    continue
                if token in ("--config", "--server-url", "--format"):
                    if index + 1 >= len(tokens):
                        raise ValueError(f"missing value for global option: {token}")
                    index += 2
                    continue
                if any(
                    token.startswith(option + "=")
                    for option in ("--config", "--server-url", "--format")
                ):
                    if token.endswith("="):
                        raise ValueError(f"missing value for global option: {token}")
                    index += 1
                    continue
                if token in ("-h", "--help", "-V", "--version"):
                    break
                if token.startswith("-"):
                    raise ValueError(f"unrecognized global option: {token}")
                if not re.fullmatch(r"[a-z][a-z0-9-]*", token):
                    raise ValueError(f"unrecognized subcommand token: {token}")
                commands.add(token)
                break
    return commands


def json_output_blocks_after_agent_hooks(page):
    fences = FENCED_BLOCK_RE.findall(page)
    outputs = []
    for index, (_, block) in enumerate(fences):
        if "hook" not in executable_agent_commands(f"```shell\n{block}\n```"):
            continue
        if index + 1 >= len(fences) or fences[index + 1][0].strip() != "json":
            raise ValueError("terraphim-agent hook command lacks an adjacent JSON output")
        outputs.append(fences[index + 1][1] + "\n")
    return outputs


def _parse_options(tokens, valued, flags):
    values = {}
    enabled = set()
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in valued:
            if token in values or index + 1 >= len(tokens):
                raise ValueError(f"missing or duplicate value for option: {token}")
            values[token] = tokens[index + 1]
            index += 2
        elif token in flags:
            if token in enabled:
                raise ValueError(f"duplicate flag: {token}")
            enabled.add(token)
            index += 1
        else:
            raise ValueError(f"unrecognized article command option: {token}")
    return values, enabled


def _parse_agent_pipeline(block):
    normalized = block.replace("\\\n", " ")
    tokens = shlex.split(normalized)
    try:
        pipe = tokens.index("|")
        agent = tokens.index("terraphim-agent")
    except ValueError as error:
        raise ValueError("fixture command must pipe stdin to terraphim-agent") from error
    if tokens[:1] != ["echo"] or pipe != 2 or agent != 3:
        raise ValueError("fixture command must use one exact echo stdin argument")
    stdin = tokens[1]
    index = agent + 1
    config = None
    if index < len(tokens) and tokens[index] == "--config":
        if index + 1 >= len(tokens):
            raise ValueError("missing --config value")
        config = tokens[index + 1]
        index += 2
    if index >= len(tokens):
        raise ValueError("missing terraphim-agent subcommand")
    subcommand = tokens[index]
    arguments = tokens[index + 1 :]
    if subcommand == "hook":
        values, flags = _parse_options(
            arguments, {"--hook-type", "--role"}, {"--json", "--rewrite"}
        )
        if set(values) != {"--hook-type", "--role"} or "--json" not in flags:
            raise ValueError("hook fixture requires type, role, and JSON output")
        return {
            "subcommand": "hook",
            "stdin": stdin,
            "config": config,
            "hookType": values["--hook-type"],
            "role": values["--role"],
            "json": True,
            "rewrite": "--rewrite" in flags,
        }
    if subcommand == "validate":
        values, flags = _parse_options(arguments, {"--checklist"}, {"--json"})
        if set(values) != {"--checklist"} or flags != {"--json"}:
            raise ValueError("validate fixture requires checklist and JSON output")
        return {
            "subcommand": "validate",
            "stdin": stdin,
            "config": config,
            "checklist": values["--checklist"],
            "json": True,
        }
    raise ValueError(f"unsupported fixture subcommand: {subcommand}")


def article_command_fixture_bindings(page):
    fences = FENCED_BLOCK_RE.findall(page)
    bindings = []
    for index, (_, block) in enumerate(fences):
        if "terraphim-agent" not in block:
            continue
        commands = executable_agent_commands(f"```shell\n{block}\n```")
        if not commands.intersection({"hook", "validate"}):
            continue
        if index + 1 >= len(fences) or fences[index + 1][0].strip() != "json":
            raise ValueError("fixture command lacks an adjacent JSON output")
        binding = _parse_agent_pipeline(block)
        displayed = fences[index + 1][1] + "\n"
        if binding["subcommand"] == "validate":
            binding["rawFixture"] = "validate-checklist-code-review.raw.json"
            binding["displayFixture"] = "validate-checklist-code-review.human.json"
        elif binding["rewrite"]:
            binding["rawFixture"] = "hook-rewrite.raw.json"
            binding["displayFixture"] = "hook-rewrite.raw.json"
        else:
            binding["rawFixture"] = "hook-no-rewrite.raw.json"
            binding["displayFixture"] = "hook-no-rewrite.raw.json"
        binding["commandBlockSha256"] = hashlib.sha256(
            (block + "\n").encode()
        ).hexdigest()
        binding["rawSha256"] = hashlib.sha256(
            (FIXTURE / binding["rawFixture"]).read_bytes()
        ).hexdigest()
        binding["displaySha256"] = hashlib.sha256(displayed.encode()).hexdigest()
        binding["exitCode"] = 0
        bindings.append(binding)
    return bindings


class ChecklistPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.help_text = (FIXTURE / "help.raw.txt").read_text()
        cls.identity = json.loads((FIXTURE / "identity.json").read_text())
        cls.pages = {path.name: path.read_text() for path in ARTICLES}

    def assert_article_command_provenance(self, pages):
        actual = {
            article: article_command_fixture_bindings(page)
            for article, page in pages.items()
        }
        self.assertEqual(actual, self.identity["articleCommandFixtures"])

    def test_help_fixture_is_bound_to_exact_release_identity(self):
        self.assertEqual(self.identity["version"], "terraphim-agent 1.21.22")
        self.assertEqual(
            hashlib.sha256(self.help_text.encode()).hexdigest(),
            self.identity["helpRawSha256"],
        )
        self.assertEqual(len(self.identity["sourceSha"]), 40)
        self.assertEqual(len(self.identity["archiveSha256"]), 64)
        self.assertEqual(len(self.identity["binarySha256"]), 64)
        snapshot = json.loads(
            (ROOT / "scripts/tests/fixtures/release-update/snapshot/complete.json").read_text()
        )
        clients = next(
            release
            for release in snapshot["repositories"]["terraphim/terraphim-clients"]
            if release["tag_name"] == "v1.21.22"
        )
        asset = next(
            asset for asset in clients["assets"]
            if asset["name"] == self.identity["archive"]
        )
        self.assertEqual(asset["digest"], "sha256:" + self.identity["archiveSha256"])
        self.assertIn(self.identity["sourceSha"], clients["body"])
        self.assertEqual(
            self.identity["binarySha256"],
            "0680d81956350eb26ac916c426b7b5e60776e587aba624d36f5fab95f385fb09",
        )
        self.assertIn("hermetic CI", self.identity["ciScope"])

    def test_executable_article_commands_exist_in_pinned_release_help(self):
        released = released_commands_in_help(self.help_text)
        advertised = set().union(
            *(executable_agent_commands(page) for page in self.pages.values())
        )
        self.assertEqual(advertised, {"hook", "validate"})
        self.assertEqual(advertised - released, set())
        self.assertNotIn("code", released)
        negative_control = "```bash\nterraphim-agent code run demo\n```"
        self.assertEqual(executable_agent_commands(negative_control) - released, {"code"})

    def test_executable_command_fences_are_checked_or_rejected(self):
        for fence in ("", "bash", "sh", "zsh", "fish", "console", "text", "custom"):
            with self.subTest(fence=fence):
                injected = f"```{fence}\nterraphim-agent code run demo\n```"
                self.assertEqual(executable_agent_commands(injected), {"code"})

    def test_indented_executable_fences_are_checked(self):
        for width in (1, 2, 3):
            indent = " " * width
            with self.subTest(indent=width):
                injected = (
                    f"{indent}```zsh\n"
                    f"{indent}terraphim-agent code run demo\n"
                    f"{indent}```"
                )
                self.assertEqual(executable_agent_commands(injected), {"code"})

    def test_prose_cannot_hide_an_unreleased_command(self):
        for verb in ("Run", "Execute", "Use", "Invoke", "Try"):
            for ticks in ("", "`"):
                with self.subTest(verb=verb, backticks=bool(ticks)):
                    prose = (
                        f"{verb} {ticks}terraphim-agent code run{ticks} "
                        "to execute the bounded loop."
                    )
                    self.assertEqual(executable_agent_commands(prose), {"code"})

    def test_historical_prose_is_not_treated_as_an_instruction(self):
        prose = (
            "The historical capture showed `terraphim-agent code run`, but the "
            "released CLI does not provide that command."
        )
        self.assertEqual(executable_agent_commands(prose), set())

    def test_indented_hook_and_json_fixtures_are_parsed_or_rejected(self):
        command = (
            "  ```zsh\n"
            "  echo '{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":"
            "\"npm install react\"}}' \\\n"
            "    | terraphim-agent --config \"$TERRAPHIM_REWRITE_CONFIG\" \\\n"
            "      hook --hook-type pre-tool-use --rewrite \\\n"
            "      --role \"Command Rewriter\" --json\n"
            "  ```\n"
        )
        output = (
            "  ```json\n"
            "  {\"tool_input\":{\"command\":\"bun add react\"},"
            "\"tool_name\":\"Bash\"}\n"
            "  ```"
        )
        page = command + output
        self.assertEqual(
            json_output_blocks_after_agent_hooks(page),
            ['  {"tool_input":{"command":"bun add react"},"tool_name":"Bash"}\n'],
        )
        bindings = article_command_fixture_bindings(page)
        self.assertEqual(len(bindings), 1)
        self.assertEqual(bindings[0]["hookType"], "pre-tool-use")
        self.assertEqual(bindings[0]["role"], "Command Rewriter")
        self.assertTrue(bindings[0]["rewrite"])
        with self.assertRaisesRegex(ValueError, "adjacent JSON output"):
            article_command_fixture_bindings(command)

    def test_global_option_forms_cannot_hide_the_subcommand(self):
        self.assertEqual(
            executable_agent_commands(
                "```sh\nterraphim-agent --config=role.json validate --help\n```"
            ),
            {"validate"},
        )
        with self.assertRaisesRegex(ValueError, "unrecognized global option"):
            executable_agent_commands(
                "```console\n$ terraphim-agent --unknown validate --help\n```"
            )

    def test_articles_state_released_hook_and_checklist_contracts(self):
        per_article_claims = {
            "graph-embeddings-checklists.md": (
                "v1.21.22",
                "bun add react",
                "does not return `validations.findings`",
            ),
            "kg-concepts-code-checklists.md": (
                "v1.21.22",
                "bun add react",
                "Passed: false",
                "exits 0",
                "lexical coverage",
                "not a quality authorization",
                "Gitea PR #432",
            ),
        }
        for article, claims in per_article_claims.items():
            for claim in claims:
                with self.subTest(article=article, claim=claim):
                    self.assertIn(claim, self.pages[article])
        joined = "\n".join(self.pages.values())
        self.assertNotIn("findings are always emitted", joined)
        self.assertNotIn("findings-based `hook` path", joined)
        self.assertNotIn('"suggested_replacement":"bun install"', joined)

    def test_rewrite_config_uses_one_unique_shell_scratch_path(self):
        graph_page = self.pages["graph-embeddings-checklists.md"]
        joined = "\n".join(self.pages.values())
        self.assertNotIn("/tmp/terraphim-rewrite-role.json", joined)
        self.assertIn('mktemp "${TMPDIR:-/tmp}/terraphim-rewrite-role.json.XXXXXX"', graph_page)
        self.assertNotIn("XXXXXX.json", graph_page)
        self.assertGreaterEqual(joined.count("$TERRAPHIM_REWRITE_CONFIG"), 3)

    def test_raw_release_fixtures_have_distinct_identity_hashes(self):
        fixture_keys = {
            "help.raw.txt": "helpRawSha256",
            "validate-checklist-code-review.raw.json": "validateChecklistRawSha256",
            "validate-checklist-code-review.human.json": "validateChecklistHumanSha256",
            "hook-no-rewrite.raw.json": "hookNoRewriteRawSha256",
            "hook-rewrite.raw.json": "hookRewriteRawSha256",
        }
        for name, identity_key in fixture_keys.items():
            with self.subTest(fixture=name):
                raw = (FIXTURE / name).read_bytes()
                self.assertEqual(
                    hashlib.sha256(raw).hexdigest(), self.identity[identity_key]
                )

    def test_each_article_hook_output_matches_raw_release_fixture(self):
        no_rewrite = (FIXTURE / "hook-no-rewrite.raw.json").read_text()
        rewrite = (FIXTURE / "hook-rewrite.raw.json").read_text()
        graph_outputs = json_output_blocks_after_agent_hooks(
            self.pages["graph-embeddings-checklists.md"]
        )
        kg_outputs = json_output_blocks_after_agent_hooks(
            self.pages["kg-concepts-code-checklists.md"]
        )
        self.assertEqual(graph_outputs, [no_rewrite, rewrite])
        self.assertEqual(kg_outputs, [rewrite])

    def test_article_commands_match_pinned_fixture_provenance(self):
        self.assert_article_command_provenance(self.pages)

    def test_fixture_provenance_rejects_exact_review_mutations(self):
        graph_name = "graph-embeddings-checklists.md"
        kg_name = "kg-concepts-code-checklists.md"
        mutations = (
            (
                "checklist stdin",
                kg_name,
                'echo "no tests; no documentation; no error handling; no security; no performance"',
                'echo "the release notes are ready"',
            ),
            (
                "hook input",
                graph_name,
                'echo \'{"tool_name":"Bash","tool_input":{"command":"npm install react"}}\'',
                'echo \'{"tool_name":"Bash","tool_input":{"command":"printf safe"}}\'',
            ),
            (
                "hook type",
                graph_name,
                "hook --hook-type pre-tool-use",
                "hook --hook-type post-tool-use",
            ),
            (
                "hook role",
                graph_name,
                '--role "Command Rewriter"',
                '--role "Missing Role"',
            ),
            (
                "rewrite flag",
                graph_name,
                "hook --hook-type pre-tool-use --rewrite",
                "hook --hook-type pre-tool-use",
            ),
        )
        for label, article, old, new in mutations:
            with self.subTest(mutation=label):
                self.assertIn(old, self.pages[article])
                mutated_pages = dict(self.pages)
                mutated_pages[article] = self.pages[article].replace(old, new, 1)
                with self.assertRaises((AssertionError, ValueError)):
                    self.assert_article_command_provenance(mutated_pages)

    def test_raw_help_exposes_only_documented_release_features(self):
        raw_help = (FIXTURE / "help.raw.txt").read_text()
        released = released_commands_in_help(raw_help)
        self.assertIn("hook", released)
        self.assertIn("validate", released)
        self.assertNotIn("code", released)

    def test_validate_json_sample_matches_pinned_raw_fixture(self):
        fixture_path = FIXTURE / "validate-checklist-code-review.raw.json"
        fixture_text = fixture_path.read_text()
        self.assertEqual(
            hashlib.sha256(fixture_text.encode()).hexdigest(),
            self.identity["validateChecklistRawSha256"],
        )
        self.assertEqual(self.identity["validateChecklistExitCode"], 0)
        expected = json.loads(fixture_text)
        article = self.pages["kg-concepts-code-checklists.md"]
        command_at = article.index("terraphim-agent validate --checklist code_review --json")
        sample = re.search(r"```json\n(.*?)\n```", article[command_at:], re.DOTALL)
        self.assertIsNotNone(sample)
        human_fixture = (FIXTURE / "validate-checklist-code-review.human.json").read_text()
        self.assertEqual(sample.group(1) + "\n", human_fixture)
        self.assertEqual(json.loads(human_fixture), expected)
        self.assertIn("Formatted for reading", article[command_at:])
        self.assertNotEqual(fixture_text, human_fixture)
        self.assertFalse(expected["passed"])
        self.assertEqual(len(expected["satisfied"]), 0)
        self.assertEqual(expected["total_items"], 5)
        self.assertIn("score of `0/5`", article)

    def test_demo_storyboard_is_historical_pr_only(self):
        article = self.pages["kg-concepts-code-checklists.md"]
        self.assertIn("## Historical PR-only Demo", article)
        self.assertIn("historical PR #432 capture", article)

    def test_public_role_graph_has_the_documented_rewrite(self):
        rule = (ROOT / ".terraphim/rewrite/bun install.md").read_text()
        self.assertIn("# bun add", rule)
        self.assertIn("npm install", rule)
        joined = "\n".join(self.pages.values())
        self.assertIn("--config", joined)
        self.assertIn(".terraphim/rewrite", joined)


if __name__ == "__main__":
    unittest.main()
