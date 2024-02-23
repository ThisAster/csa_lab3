import contextlib
import io
import logging
import os
import tempfile

import pytest

import machine
import translator


@pytest.mark.golden_test("golden/*.yaml")
def test_golden(golden, caplog):
    caplog.set_level(logging.DEBUG)

    def read_golden_file(name):
        golden_dir = os.path.join(".", "tests", "golden")
        with open(os.path.join(golden_dir, golden[name]), encoding="utf-8") as file:
            return file.read()

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_js = os.path.join(tmpdirname, "source.js")
        tmp_code = os.path.join(tmpdirname, "target.code")
        tmp_data = os.path.join(tmpdirname, "target.data")
        tmp_txt = os.path.join(tmpdirname, "input.txt")

        with open(tmp_js, "w", encoding="utf-8") as file2:
            file2.write(read_golden_file("js"))
        with open(tmp_txt, "w", encoding="utf-8") as file2:
            file2.write(read_golden_file("txt"))

        separator = "========================================"

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(tmp_js, tmp_code, tmp_data)
            print(separator)
            machine.main(tmp_code, tmp_data, tmp_txt)

        assert open(tmp_code).read().strip() == read_golden_file("code").strip()
        assert open(tmp_data).read().strip() == read_golden_file("data").strip()

        expected_translator_stdout = read_golden_file("translator_log").strip()
        expected_machine_stdout = read_golden_file("machine_log").strip()
        stdout_text = stdout.getvalue()
        real_translator_stdout = stdout_text.split(separator)[0].strip()
        real_machine_stdout = stdout_text.split(separator)[1].strip()

        assert real_translator_stdout == expected_translator_stdout
        assert real_machine_stdout == expected_machine_stdout
