import json, os, subprocess, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(__file__))
from check_copy import turn, verdict

U = lambda t: json.dumps({"type": "user", "message": {"role": "user", "content": t}})
R = json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}})
A = lambda t: json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": t}]}})
T = lambda c: json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "input": {"command": c}}]}})


class CheckCopy(unittest.TestCase):
    def check(self, lines):
        return verdict(*turn(lines))

    def test_claim_without_copy_blocks(self):
        self.assertIn("no copy command", self.check([U("hola"), A("x\n📋 Copiado al portapapeles")]))

    def test_claim_with_copy_passes(self):
        self.assertIsNone(self.check([U("hola"), T("python clip.py <<'E'\nx\nE"), R, A("📋 Copiado al portapapeles")]))

    def test_copy_in_previous_turn_does_not_count(self):
        lines = [U("a"), T("python clip.py"), R, A("ok"), U("b"), A("📋 Copied to clipboard")]
        self.assertIsNotNone(self.check(lines))

    def test_bang_block_without_copy_blocks(self):
        self.assertIn("`!` command", self.check([U("x"), A("Pega:\n```\n! printf '%s' k > f\n```")]))

    def test_plain_reply_passes(self):
        self.assertIsNone(self.check([U("x"), A("Hecho. ```py\nprint(1)\n```")]))

    def test_main_blocks_and_respects_stop_hook_active(self):
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write("\n".join([U("x"), A("📋 Copiado al portapapeles")]))
        script = os.path.join(os.path.dirname(__file__), "check_copy.py")
        run = lambda d: subprocess.run([sys.executable, script], input=json.dumps(d), capture_output=True, text=True).stdout
        self.assertEqual(json.loads(run({"transcript_path": f.name}))["decision"], "block")
        self.assertEqual(run({"transcript_path": f.name, "stop_hook_active": True}), "")
        os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
