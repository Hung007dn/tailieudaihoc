"""
PyQt6 GUI for evphashdirect.dll

This GUI uses the algorithm-specific OpenSSL EVP Hash DLL exported by:

    include/evp_hash_direct_c_api.h
    src/evp_hash_direct_c_api.cpp

DLL name expected:
    evphashdirect.dll

Supported algorithm-specific digest APIs:

    sha1
    sha224
    sha256
    sha384
    sha512
    sha512-224
    sha512-256

    sha3-224
    sha3-256
    sha3-384
    sha3-512

    shake128
    shake256

    md5-sha1  # legacy TLS combined digest; learning only

Install:
    pip install PyQt6

Run:
    python evphashdirect_pyqt6_gui.py

Place evphashdirect.dll beside this .py file, or select it in the GUI.

Runtime dependency note on Windows:
    evphashdirect.dll also needs OpenSSL and MinGW runtime DLLs, for example:
        libcrypto-4-x64.dll
        libstdc++-6.dll
        libgcc_s_seh-1.dll
        libwinpthread-1.dll

    Put these DLLs beside evphashdirect.dll, or make sure their folders are in PATH.
    This GUI also calls os.add_dll_directory() for the selected DLL folder.
"""

from __future__ import annotations

import ctypes
import os
import re
import secrets
import sys
from pathlib import Path
from typing import Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


EVPHASHDIRECT_OK = 0
EVPHASHDIRECT_ERR_BUFFER_TOO_SMALL = -2


def clean_hex(s: str) -> str:
    """
    Accept teaching-friendly hex forms:
        001122
        00 11 22
        00:11:22
        0x00 0x11 0x22
    """
    s = s.strip()
    s = re.sub(r"0x", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^0-9a-fA-F]", "", s)
    return s


def hex_to_bytes_py(s: str, field_name: str = "hex") -> bytes:
    s = clean_hex(s)

    if not s:
        return b""

    if len(s) % 2 != 0:
        raise ValueError(f"{field_name} must contain an even number of hex digits")

    try:
        return bytes.fromhex(s)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}") from exc


def bytes_to_text_lossy(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def as_u8_array(data: bytes):
    if not data:
        return None
    return (ctypes.c_uint8 * len(data)).from_buffer_copy(data)


def as_u8_ptr(arr):
    if arr is None:
        return None
    return ctypes.cast(arr, ctypes.POINTER(ctypes.c_uint8))


def prepare_windows_dll_loading(dll_path: str) -> tuple[list[object], list[ctypes.CDLL]]:
    """
    Prepare Windows DLL dependency loading for ctypes.

    evphashdirect.dll depends on libcrypto and MinGW runtime DLLs.
    On modern Python/Windows, the selected DLL folder is not always used for
    dependent DLL resolution unless explicitly added.
    """
    if sys.platform != "win32":
        return [], []

    dll_file = Path(dll_path).resolve()

    candidate_dirs: list[Path] = []

    if dll_file.parent.exists():
        candidate_dirs.append(dll_file.parent)

    script_dir = Path(__file__).resolve().parent
    if script_dir.exists():
        candidate_dirs.append(script_dir)

    local_dlls = script_dir / "dlls"
    if local_dlls.exists():
        candidate_dirs.append(local_dlls)

    seen: set[str] = set()
    unique_dirs: list[Path] = []

    for d in candidate_dirs:
        key = str(d).lower()
        if key not in seen:
            seen.add(key)
            unique_dirs.append(d)

    handles: list[object] = []

    for d in unique_dirs:
        try:
            handles.append(os.add_dll_directory(str(d)))
        except AttributeError:
            os.environ["PATH"] = str(d) + os.pathsep + os.environ.get("PATH", "")
        except OSError:
            pass

    dependency_names = [
        "libcrypto-4-x64.dll",
        "libcrypto-3-x64.dll",
        "libcrypto-1_1-x64.dll",
        "libssl-4-x64.dll",
        "libssl-3-x64.dll",
        "libssl-1_1-x64.dll",
        "libstdc++-6.dll",
        "libgcc_s_seh-1.dll",
        "libgcc_s_dw2-1.dll",
        "libwinpthread-1.dll",
        "zlib1.dll",
    ]

    preloaded: list[ctypes.CDLL] = []

    for d in unique_dirs:
        for name in dependency_names:
            dep = d / name
            if dep.exists():
                try:
                    preloaded.append(ctypes.CDLL(str(dep)))
                except OSError:
                    pass

    return handles, preloaded


class EVPHashDirectDLL:
    """
    ctypes wrapper for evphashdirect.dll.

    Uses the two-pass buffer-sizing pattern:
        1. call with output buffer = NULL and capacity 0
        2. DLL returns required output length with ERR_BUFFER_TOO_SMALL
        3. allocate buffer
        4. call again
    """

    def __init__(self, dll_path: str):
        self.dll_path = str(Path(dll_path).resolve())

        # Keep these alive while the DLL is used.
        self._dll_dir_handles, self._preloaded_dependencies = prepare_windows_dll_loading(
            self.dll_path
        )

        self.lib = ctypes.CDLL(self.dll_path)
        self._bind()

    def _bind(self) -> None:
        u8p = ctypes.POINTER(ctypes.c_uint8)
        sizep = ctypes.POINTER(ctypes.c_size_t)
        intp = ctypes.POINTER(ctypes.c_int)
        ctxp = ctypes.c_void_p
        ctxpp = ctypes.POINTER(ctypes.c_void_p)

        self.lib.evphashdirect_version.argtypes = []
        self.lib.evphashdirect_version.restype = ctypes.c_char_p

        self.lib.evphashdirect_last_error.argtypes = []
        self.lib.evphashdirect_last_error.restype = ctypes.c_char_p

        self.lib.evphashdirect_clear_error.argtypes = []
        self.lib.evphashdirect_clear_error.restype = None

        self.lib.evphashdirect_digest_available.argtypes = [ctypes.c_char_p]
        self.lib.evphashdirect_digest_available.restype = ctypes.c_int

        self.lib.evphashdirect_digest_info.argtypes = [
            ctypes.c_char_p,
            intp,
            intp,
            intp,
        ]
        self.lib.evphashdirect_digest_info.restype = ctypes.c_int

        self.lib.evphashdirect_digest.argtypes = [
            ctypes.c_char_p,
            u8p,
            ctypes.c_size_t,
            ctypes.c_size_t,
            u8p,
            ctypes.c_size_t,
            sizep,
        ]
        self.lib.evphashdirect_digest.restype = ctypes.c_int

        self.lib.evphashdirect_ctx_new.argtypes = [
            ctypes.c_char_p,
            ctxpp,
        ]
        self.lib.evphashdirect_ctx_new.restype = ctypes.c_int

        self.lib.evphashdirect_ctx_update.argtypes = [
            ctxp,
            u8p,
            ctypes.c_size_t,
        ]
        self.lib.evphashdirect_ctx_update.restype = ctypes.c_int

        self.lib.evphashdirect_ctx_copy.argtypes = [
            ctxp,
            ctxpp,
        ]
        self.lib.evphashdirect_ctx_copy.restype = ctypes.c_int

        self.lib.evphashdirect_ctx_final.argtypes = [
            ctxp,
            u8p,
            ctypes.c_size_t,
            sizep,
        ]
        self.lib.evphashdirect_ctx_final.restype = ctypes.c_int

        self.lib.evphashdirect_ctx_final_xof.argtypes = [
            ctxp,
            ctypes.c_size_t,
            u8p,
            ctypes.c_size_t,
            sizep,
        ]
        self.lib.evphashdirect_ctx_final_xof.restype = ctypes.c_int

        self.lib.evphashdirect_ctx_free.argtypes = [ctxp]
        self.lib.evphashdirect_ctx_free.restype = None

        self.lib.evphashdirect_hex_to_bytes.argtypes = [
            ctypes.c_char_p,
            u8p,
            ctypes.c_size_t,
            sizep,
        ]
        self.lib.evphashdirect_hex_to_bytes.restype = ctypes.c_int

        self.lib.evphashdirect_bytes_to_hex.argtypes = [
            u8p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
            sizep,
        ]
        self.lib.evphashdirect_bytes_to_hex.restype = ctypes.c_int

    def version(self) -> str:
        raw = self.lib.evphashdirect_version()
        return raw.decode("utf-8", errors="replace") if raw else "unknown"

    def last_error(self) -> str:
        raw = self.lib.evphashdirect_last_error()
        return raw.decode("utf-8", errors="replace") if raw else ""

    def _check(self, status: int, allowed: Tuple[int, ...] = (EVPHASHDIRECT_OK,)) -> None:
        if status not in allowed:
            msg = self.last_error() or f"EVPHashDirect error status {status}"
            raise RuntimeError(msg)

    def digest_available(self, algorithm: str) -> bool:
        status = self.lib.evphashdirect_digest_available(algorithm.encode("utf-8"))
        if status in (0, 1):
            return bool(status)
        self._check(status)
        return False

    def digest_info(self, algorithm: str) -> tuple[int, int, bool]:
        output_size = ctypes.c_int(0)
        block_size = ctypes.c_int(0)
        is_xof = ctypes.c_int(0)

        status = self.lib.evphashdirect_digest_info(
            algorithm.encode("utf-8"),
            ctypes.byref(output_size),
            ctypes.byref(block_size),
            ctypes.byref(is_xof),
        )

        self._check(status)
        return int(output_size.value), int(block_size.value), bool(is_xof.value)

    def digest(self, algorithm: str, data: bytes, xof_output_len: int = 0) -> bytes:
        alg_b = algorithm.encode("utf-8")
        data_arr = as_u8_array(data)

        out_len = ctypes.c_size_t(0)

        status = self.lib.evphashdirect_digest(
            alg_b,
            as_u8_ptr(data_arr),
            len(data),
            int(xof_output_len),
            None,
            0,
            ctypes.byref(out_len),
        )

        self._check(status, allowed=(EVPHASHDIRECT_OK, EVPHASHDIRECT_ERR_BUFFER_TOO_SMALL))

        if out_len.value == 0:
            return b""

        out_buf = (ctypes.c_uint8 * out_len.value)()

        status = self.lib.evphashdirect_digest(
            alg_b,
            as_u8_ptr(data_arr),
            len(data),
            int(xof_output_len),
            out_buf,
            out_len.value,
            ctypes.byref(out_len),
        )

        self._check(status)

        return bytes(out_buf[: out_len.value])

    def ctx_new(self, algorithm: str) -> ctypes.c_void_p:
        ctx = ctypes.c_void_p(None)

        status = self.lib.evphashdirect_ctx_new(
            algorithm.encode("utf-8"),
            ctypes.byref(ctx),
        )

        self._check(status)

        if not ctx.value:
            raise RuntimeError("DLL returned null digest context")

        return ctx

    def ctx_update(self, ctx: ctypes.c_void_p, data: bytes) -> None:
        data_arr = as_u8_array(data)

        status = self.lib.evphashdirect_ctx_update(
            ctx,
            as_u8_ptr(data_arr),
            len(data),
        )

        self._check(status)

    def ctx_copy(self, ctx: ctypes.c_void_p) -> ctypes.c_void_p:
        out = ctypes.c_void_p(None)

        status = self.lib.evphashdirect_ctx_copy(
            ctx,
            ctypes.byref(out),
        )

        self._check(status)

        if not out.value:
            raise RuntimeError("DLL returned null copied digest context")

        return out

    def ctx_final(self, ctx: ctypes.c_void_p) -> bytes:
        out_len = ctypes.c_size_t(0)

        status = self.lib.evphashdirect_ctx_final(
            ctx,
            None,
            0,
            ctypes.byref(out_len),
        )

        self._check(status, allowed=(EVPHASHDIRECT_OK, EVPHASHDIRECT_ERR_BUFFER_TOO_SMALL))

        if out_len.value == 0:
            return b""

        out_buf = (ctypes.c_uint8 * out_len.value)()

        status = self.lib.evphashdirect_ctx_final(
            ctx,
            out_buf,
            out_len.value,
            ctypes.byref(out_len),
        )

        self._check(status)

        return bytes(out_buf[: out_len.value])

    def ctx_final_xof(self, ctx: ctypes.c_void_p, xof_output_len: int) -> bytes:
        out_len = ctypes.c_size_t(0)

        status = self.lib.evphashdirect_ctx_final_xof(
            ctx,
            int(xof_output_len),
            None,
            0,
            ctypes.byref(out_len),
        )

        self._check(status, allowed=(EVPHASHDIRECT_OK, EVPHASHDIRECT_ERR_BUFFER_TOO_SMALL))

        if out_len.value == 0:
            return b""

        out_buf = (ctypes.c_uint8 * out_len.value)()

        status = self.lib.evphashdirect_ctx_final_xof(
            ctx,
            int(xof_output_len),
            out_buf,
            out_len.value,
            ctypes.byref(out_len),
        )

        self._check(status)

        return bytes(out_buf[: out_len.value])

    def ctx_free(self, ctx: Optional[ctypes.c_void_p]) -> None:
        if ctx is not None and ctx.value:
            self.lib.evphashdirect_ctx_free(ctx)


class MainWindow(QMainWindow):
    ALGORITHMS = [
        "sha1",
        "sha224",
        "sha256",
        "sha384",
        "sha512",
        "sha512-224",
        "sha512-256",
        "sha3-224",
        "sha3-256",
        "sha3-384",
        "sha3-512",
        "shake128",
        "shake256",
        "md5-sha1",
    ]

    def __init__(self):
        super().__init__()
        self.dll: Optional[EVPHashDirectDLL] = None
        self.setWindowTitle("EVP Hash Direct GUI - PyQt6 + evphashdirect.dll")
        self.resize(1120, 820)
        self._build_ui()
        self._auto_find_dll()
        self._update_algorithm_fields()

    def _build_ui(self) -> None:
        root = QWidget()
        main_layout = QVBoxLayout(root)

        dll_box = QGroupBox("DLL")
        dll_layout = QGridLayout(dll_box)

        self.dll_path = QLineEdit()
        self.dll_path.setPlaceholderText("Path to evphashdirect.dll")

        self.btn_browse_dll = QPushButton("Browse...")
        self.btn_load_dll = QPushButton("Load DLL")
        self.lbl_dll_status = QLabel("Not loaded")

        self.btn_browse_dll.clicked.connect(self._browse_dll)
        self.btn_load_dll.clicked.connect(self._load_dll)

        dll_layout.addWidget(QLabel("DLL path:"), 0, 0)
        dll_layout.addWidget(self.dll_path, 0, 1)
        dll_layout.addWidget(self.btn_browse_dll, 0, 2)
        dll_layout.addWidget(self.btn_load_dll, 0, 3)
        dll_layout.addWidget(self.lbl_dll_status, 1, 1, 1, 3)

        main_layout.addWidget(dll_box)

        config_box = QGroupBox("Digest Configuration")
        config_layout = QGridLayout(config_box)

        self.algorithm = QComboBox()
        self.algorithm.addItems(self.ALGORITHMS)
        self.algorithm.setCurrentText("sha256")
        self.algorithm.currentTextChanged.connect(self._update_algorithm_fields)

        self.xof_len = QSpinBox()
        self.xof_len.setRange(0, 65536)
        self.xof_len.setValue(32)
        self.xof_len.setToolTip("Used only for SHAKE/XOF. 0 means DLL/OpenSSL default output size.")

        self.info_label = QLabel("Info: -")

        self.btn_info = QPushButton("Digest Info")
        self.btn_available = QPushButton("Check Availability")
        self.btn_info.clicked.connect(self._show_digest_info)
        self.btn_available.clicked.connect(self._check_availability)

        config_layout.addWidget(QLabel("Algorithm:"), 0, 0)
        config_layout.addWidget(self.algorithm, 0, 1)
        config_layout.addWidget(QLabel("XOF length:"), 0, 2)
        config_layout.addWidget(self.xof_len, 0, 3)
        config_layout.addWidget(self.btn_info, 0, 4)
        config_layout.addWidget(self.btn_available, 0, 5)
        config_layout.addWidget(self.info_label, 1, 1, 1, 5)

        main_layout.addWidget(config_box)

        self.tabs = QTabWidget()

        self._build_one_shot_tab()
        self._build_streaming_tab()
        self._build_random_tab()

        main_layout.addWidget(self.tabs, 1)

        buttons = QHBoxLayout()

        self.btn_hash = QPushButton("Hash Input")
        self.btn_hash.clicked.connect(self._hash_one_shot)

        self.btn_clear = QPushButton("Clear Output")
        self.btn_clear.clicked.connect(self.output_data.clear)

        self.btn_load_sha256_abc = QPushButton("Load SHA-256 abc")
        self.btn_load_sha256_abc.clicked.connect(self._load_sha256_abc)

        self.btn_load_shake_abc = QPushButton("Load SHAKE128 abc")
        self.btn_load_shake_abc.clicked.connect(self._load_shake_abc)

        buttons.addWidget(self.btn_hash)
        buttons.addWidget(self.btn_clear)
        buttons.addWidget(self.btn_load_sha256_abc)
        buttons.addWidget(self.btn_load_shake_abc)

        main_layout.addLayout(buttons)

        self.setCentralWidget(root)

    def _build_one_shot_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        input_top = QHBoxLayout()

        self.input_type = QComboBox()
        self.input_type.addItems(["Text", "Hex", "File"])

        self.input_file = QLineEdit()
        self.input_file.setPlaceholderText("Input file path")

        self.btn_input_file = QPushButton("Browse Input...")
        self.btn_input_file.clicked.connect(self._browse_input_file)

        input_top.addWidget(QLabel("Input type:"))
        input_top.addWidget(self.input_type)
        input_top.addWidget(self.input_file, 1)
        input_top.addWidget(self.btn_input_file)

        self.input_data = QPlainTextEdit()
        self.input_data.setPlaceholderText("Input text or hex")

        output_top = QHBoxLayout()

        self.output_type = QComboBox()
        self.output_type.addItems(["Hex", "Text", "File"])

        self.output_file = QLineEdit()
        self.output_file.setPlaceholderText("Output file path. File output writes raw digest bytes.")

        self.btn_output_file = QPushButton("Browse Output...")
        self.btn_output_file.clicked.connect(self._browse_output_file)

        output_top.addWidget(QLabel("Output type:"))
        output_top.addWidget(self.output_type)
        output_top.addWidget(self.output_file, 1)
        output_top.addWidget(self.btn_output_file)

        self.output_data = QPlainTextEdit()
        self.output_data.setPlaceholderText("Digest output")

        layout.addLayout(input_top)
        layout.addWidget(self.input_data, 1)
        layout.addLayout(output_top)
        layout.addWidget(self.output_data, 1)

        self.tabs.addTab(tab, "One-shot Hash")

    def _build_streaming_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        desc = QLabel(
            "Streaming mode hashes each chunk in order using evphashdirect_ctx_new/update/final. "
            "Each line below is one chunk. Optional clone demo copies the context after the selected chunk."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.streaming_chunks = QPlainTextEdit()
        self.streaming_chunks.setPlaceholderText("Each line is one chunk, e.g.\nabc\ndef")
        layout.addWidget(self.streaming_chunks, 1)

        controls = QHBoxLayout()

        self.streaming_chunk_type = QComboBox()
        self.streaming_chunk_type.addItems(["Text lines", "Hex lines"])

        self.clone_enabled = QCheckBox("Clone context after chunk index")
        self.clone_index = QSpinBox()
        self.clone_index.setRange(0, 9999)
        self.clone_index.setValue(0)
        self.clone_extra_type = QComboBox()
        self.clone_extra_type.addItems(["Text", "Hex"])
        self.clone_extra = QLineEdit()
        self.clone_extra.setPlaceholderText("Extra data appended only to cloned context")

        self.btn_stream_hash = QPushButton("Streaming Hash")
        self.btn_stream_hash.clicked.connect(self._hash_streaming)

        controls.addWidget(QLabel("Chunk type:"))
        controls.addWidget(self.streaming_chunk_type)
        controls.addWidget(self.clone_enabled)
        controls.addWidget(self.clone_index)
        controls.addWidget(QLabel("Clone extra type:"))
        controls.addWidget(self.clone_extra_type)
        controls.addWidget(self.clone_extra, 1)
        controls.addWidget(self.btn_stream_hash)

        layout.addLayout(controls)

        self.streaming_output = QPlainTextEdit()
        self.streaming_output.setPlaceholderText("Streaming hash output")
        layout.addWidget(self.streaming_output, 1)

        self.tabs.addTab(tab, "Streaming / Context API")

    def _build_random_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        info = QLabel(
            "Generate random input bytes for hashing tests. Hashes do not use keys; this tab is only for random messages."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()

        self.random_len = QSpinBox()
        self.random_len.setRange(0, 1024 * 1024)
        self.random_len.setValue(32)

        self.random_output_type = QComboBox()
        self.random_output_type.addItems(["Hex", "Text-safe preview"])

        self.btn_random_input = QPushButton("Generate Random Input")
        self.btn_random_input.clicked.connect(self._generate_random_input)

        row.addWidget(QLabel("Random length:"))
        row.addWidget(self.random_len)
        row.addWidget(QLabel("Output format:"))
        row.addWidget(self.random_output_type)
        row.addWidget(self.btn_random_input)
        row.addStretch(1)

        layout.addLayout(row)

        self.random_preview = QPlainTextEdit()
        self.random_preview.setPlaceholderText("Random input preview")
        layout.addWidget(self.random_preview, 1)

        self.tabs.addTab(tab, "Random Input")

    def _auto_find_dll(self) -> None:
        candidates = [
            Path.cwd() / "evphashdirect.dll",
            Path(__file__).resolve().parent / "evphashdirect.dll",
        ]

        for p in candidates:
            if p.exists():
                self.dll_path.setText(str(p))
                return

    def _browse_dll(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select evphashdirect.dll",
            "",
            "DLL Files (*.dll);;All Files (*)",
        )
        if path:
            self.dll_path.setText(path)

    def _browse_input_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select input file",
            "",
            "All Files (*)",
        )
        if path:
            self.input_file.setText(path)
            self.input_type.setCurrentText("File")

    def _browse_output_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select output file",
            "",
            "All Files (*)",
        )
        if path:
            self.output_file.setText(path)
            self.output_type.setCurrentText("File")

    def _load_dll(self) -> None:
        path = self.dll_path.text().strip()

        if not path:
            self._error("Please select evphashdirect.dll")
            return

        try:
            self.dll = EVPHashDirectDLL(path)
            self.lbl_dll_status.setText(f"Loaded: {self.dll.version()}")
            self.lbl_dll_status.setStyleSheet("color: green;")
            self.statusBar().showMessage("DLL loaded", 5000)
            self._update_algorithm_fields()
        except Exception as exc:
            self.dll = None
            self.lbl_dll_status.setText("Load failed")
            self.lbl_dll_status.setStyleSheet("color: red;")
            self._error(
                str(exc)
                + "\n\n"
                + "Check that evphashdirect.dll and its dependency DLLs are in the same folder "
                  "or in PATH. Typical non-system dependencies are: "
                  "libcrypto-4-x64.dll, libstdc++-6.dll, libgcc_s_seh-1.dll, "
                  "and libwinpthread-1.dll."
            )

    def _require_dll(self) -> EVPHashDirectDLL:
        if self.dll is None:
            self._load_dll()

        if self.dll is None:
            raise RuntimeError("evphashdirect.dll is not loaded")

        return self.dll

    def _update_algorithm_fields(self) -> None:
        alg = self.algorithm.currentText().lower()
        is_xof = alg in {"shake128", "shake256"}
        self.xof_len.setEnabled(is_xof)

        if not is_xof:
            self.xof_len.setValue(0)
        elif self.xof_len.value() == 0:
            self.xof_len.setValue(32)

        if self.dll is not None:
            try:
                out_size, block_size, dll_is_xof = self.dll.digest_info(alg)
                self.info_label.setText(
                    f"Info: output={out_size} byte(s), block={block_size} byte(s), XOF={'yes' if dll_is_xof else 'no'}"
                )
            except Exception:
                self.info_label.setText("Info: unavailable")
        else:
            self.info_label.setText("Info: DLL not loaded")

    def _read_input_bytes(self) -> bytes:
        input_type = self.input_type.currentText()

        if input_type == "File":
            path = self.input_file.text().strip()
            if not path:
                raise ValueError("Input file path is empty")
            return Path(path).read_bytes()

        text = self.input_data.toPlainText()

        if input_type == "Hex":
            return hex_to_bytes_py(text, "input hex")

        return text.encode("utf-8")

    def _write_output_bytes(self, data: bytes) -> None:
        output_type = self.output_type.currentText()

        if output_type == "File":
            path = self.output_file.text().strip()
            if not path:
                raise ValueError("Output file path is empty")
            Path(path).write_bytes(data)
            self.output_data.setPlainText(f"Wrote {len(data)} raw digest byte(s) to:\n{path}")
            return

        if output_type == "Text":
            self.output_data.setPlainText(bytes_to_text_lossy(data))
            return

        self.output_data.setPlainText(data.hex())

    def _current_xof_len(self) -> int:
        alg = self.algorithm.currentText().lower()
        if alg in {"shake128", "shake256"}:
            return int(self.xof_len.value())
        return 0

    def _hash_one_shot(self) -> None:
        try:
            dll = self._require_dll()
            alg = self.algorithm.currentText()
            data = self._read_input_bytes()
            digest = dll.digest(alg, data, self._current_xof_len())
            self._write_output_bytes(digest)
            self.statusBar().showMessage("Hash completed", 5000)
        except Exception as exc:
            self._error(str(exc))

    def _show_digest_info(self) -> None:
        try:
            dll = self._require_dll()
            alg = self.algorithm.currentText()
            out_size, block_size, is_xof = dll.digest_info(alg)
            available = dll.digest_available(alg)

            QMessageBox.information(
                self,
                "Digest Info",
                f"Algorithm: {alg}\n"
                f"Available: {'yes' if available else 'no'}\n"
                f"Output size: {out_size} byte(s)\n"
                f"Block size: {block_size} byte(s)\n"
                f"XOF: {'yes' if is_xof else 'no'}\n\n"
                f"For SHAKE/XOF, choose a custom output length in bytes.",
            )
        except Exception as exc:
            self._error(str(exc))

    def _check_availability(self) -> None:
        try:
            dll = self._require_dll()
            alg = self.algorithm.currentText()
            available = dll.digest_available(alg)

            QMessageBox.information(
                self,
                "Availability",
                f"{alg}: {'available' if available else 'not available'}",
            )
        except Exception as exc:
            self._error(str(exc))

    def _parse_streaming_chunks(self) -> list[bytes]:
        raw_lines = self.streaming_chunks.toPlainText().splitlines()
        lines = [line for line in raw_lines if line != ""]

        if self.streaming_chunk_type.currentText() == "Hex lines":
            return [hex_to_bytes_py(line, f"hex chunk line {idx + 1}") for idx, line in enumerate(lines)]

        return [line.encode("utf-8") for line in lines]

    def _hash_streaming(self) -> None:
        ctx = None
        clone_ctx = None

        try:
            dll = self._require_dll()
            alg = self.algorithm.currentText()
            chunks = self._parse_streaming_chunks()

            ctx = dll.ctx_new(alg)

            clone_after = int(self.clone_index.value())
            clone_enabled = self.clone_enabled.isChecked()

            for idx, chunk in enumerate(chunks):
                dll.ctx_update(ctx, chunk)

                if clone_enabled and idx == clone_after:
                    clone_ctx = dll.ctx_copy(ctx)

            if clone_enabled and clone_ctx is None:
                clone_ctx = dll.ctx_copy(ctx)

            if clone_ctx is not None and self.clone_extra.text():
                if self.clone_extra_type.currentText() == "Hex":
                    extra = hex_to_bytes_py(self.clone_extra.text(), "clone extra hex")
                else:
                    extra = self.clone_extra.text().encode("utf-8")
                dll.ctx_update(clone_ctx, extra)

            _, _, is_xof = dll.digest_info(alg)
            xof_len = self._current_xof_len()

            if is_xof:
                main_digest = dll.ctx_final_xof(ctx, xof_len)
            else:
                main_digest = dll.ctx_final(ctx)

            lines = []
            lines.append(f"Algorithm: {alg}")
            lines.append(f"Chunks: {len(chunks)}")
            lines.append(f"Main digest: {main_digest.hex()}")

            if clone_ctx is not None:
                if is_xof:
                    clone_digest = dll.ctx_final_xof(clone_ctx, xof_len)
                else:
                    clone_digest = dll.ctx_final(clone_ctx)

                lines.append("")
                lines.append(f"Clone made after chunk index: {clone_after}")
                lines.append(f"Clone extra: {self.clone_extra.text()!r}")
                lines.append(f"Clone digest: {clone_digest.hex()}")

            self.streaming_output.setPlainText("\n".join(lines))
            self.statusBar().showMessage("Streaming hash completed", 5000)

            # Contexts are finalized. The DLL context object itself still must be freed.
            dll.ctx_free(ctx)
            ctx = None

            if clone_ctx is not None:
                dll.ctx_free(clone_ctx)
                clone_ctx = None

        except Exception as exc:
            self._error(str(exc))

            if ctx is not None:
                try:
                    self.dll.ctx_free(ctx)  # type: ignore[union-attr]
                except Exception:
                    pass

            if clone_ctx is not None:
                try:
                    self.dll.ctx_free(clone_ctx)  # type: ignore[union-attr]
                except Exception:
                    pass

    def _generate_random_input(self) -> None:
        data = secrets.token_bytes(int(self.random_len.value()))

        if self.random_output_type.currentText() == "Text-safe preview":
            # Most random bytes are not valid text. Use latin-1 to preserve bytes
            # while still letting users see a one-codepoint-per-byte preview.
            preview = data.decode("latin-1", errors="replace")
            self.input_type.setCurrentText("Text")
            self.input_data.setPlainText(preview)
            self.random_preview.setPlainText(preview)
        else:
            hex_data = data.hex()
            self.input_type.setCurrentText("Hex")
            self.input_data.setPlainText(hex_data)
            self.random_preview.setPlainText(hex_data)

        self.tabs.setCurrentIndex(0)

    def _load_sha256_abc(self) -> None:
        self.algorithm.setCurrentText("sha256")
        self.input_type.setCurrentText("Text")
        self.input_data.setPlainText("abc")
        self.output_type.setCurrentText("Hex")
        self.output_data.clear()
        self._update_algorithm_fields()
        self.statusBar().showMessage(
            "Expected SHA-256(abc): ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            12000,
        )

    def _load_shake_abc(self) -> None:
        self.algorithm.setCurrentText("shake128")
        self.xof_len.setValue(32)
        self.input_type.setCurrentText("Text")
        self.input_data.setPlainText("abc")
        self.output_type.setCurrentText("Hex")
        self.output_data.clear()
        self._update_algorithm_fields()
        self.statusBar().showMessage(
            "Loaded SHAKE128(abc) with 32-byte output.",
            8000,
        )

    def _error(self, msg: str) -> None:
        QMessageBox.critical(self, "EVP Hash Direct Error", msg)
        self.statusBar().showMessage("Error", 5000)


def main() -> int:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
