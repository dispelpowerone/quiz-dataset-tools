import importlib
import sys
import unittest
from unittest.mock import patch

from quiz_dataset_tools.util import gpt


class TestGPTModuleImport(unittest.TestCase):
    def test_import_does_not_require_openai_or_config(self) -> None:
        module_name = "quiz_dataset_tools.util.gpt"
        parent_module = sys.modules["quiz_dataset_tools.util"]
        original_parent_gpt = parent_module.gpt
        original_module = sys.modules.pop(module_name, None)
        try:
            with patch.dict(
                sys.modules,
                {
                    "openai": None,
                    "openai.types": None,
                    "openai.types.chat": None,
                    "quiz_dataset_tools.config": None,
                },
            ):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module.GPTService)
        finally:
            sys.modules.pop(module_name, None)
            if original_module is not None:
                sys.modules[module_name] = original_module
            parent_module.gpt = original_parent_gpt

    def test_client_initialization_error_is_not_retried(self) -> None:
        service = gpt.GPTService("test", max_retries=3, retry_delay=0)
        with (
            patch.object(
                gpt,
                "_get_client",
                side_effect=RuntimeError("missing config"),
            ) as get_client,
            patch.object(gpt.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(RuntimeError, "missing config"):
                service.send_prompt("test")

        get_client.assert_called_once_with()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
