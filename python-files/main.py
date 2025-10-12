#!/usr/bin/env python3
# save_editor.py
# Edytor save'ów do Maxdila - prosta próba podmiany wartości pieniędzy i aktualizacji checksum (jeśli wykrywalna).
# Używaj na własne ryzyko — ZAWSZE rób kopię zapasową!

import argparse
import shutil
import sys
from typing import List

def load_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]

def save_lines(path: str, lines: List[str]):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line) + "\n")

def is_int(s: str):
    try:
        int(s)
        return True
    except:
        return False

def find_first_occurrence(lines: List[str], value: int):
    s = str(value)
    for i, line in enumerate(lines):
        if line == s:
            return i
    return None

def find_checksum_line(lines: List[str]):
    # Szukamy linii, której wartość = suma wszystkich poprzednich wartości numerycznych
    numeric_indices = []
    for idx, line in enumerate(lines):
        if is_int(line):
            numeric_indices.append(idx)
    running = 0
    for j, idx in enumerate(numeric_indices):
        val = int(lines[idx])
        if running == val and j > 0:
            return idx
        running += val
    return None

def compute_numeric_sum_up_to_index(lines: List[str], checksum_index: int):
    s = 0
    for i in range(0, checksum_index):
        if is_int(lines[i]):
            s += int(lines[i])
    return s

def main():
    parser = argparse.ArgumentParser(description="Simple Maxdila save editor")
    parser.add_argument("input", help="ścieżka do pliku save (wejście)")
    parser.add_argument("output", nargs="?", help="ścieżka wyjściowa (jeśli pominięte - zostanie użyta nazwa input_modified.data)")
