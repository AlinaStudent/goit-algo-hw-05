# -*- coding: utf-8 -*-
"""
Пошук підрядка: реалізації алгоритмів
- Боєра–Мура (евристика "поганого символу")
- Кнута–Морріса–Пратта (KMP)
- Рабіна–Карпа (хешування рядків)
"""
from typing import Dict

def boyer_moore_bad_character(text: str, pattern: str) -> int:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    # останні входження символів
    last: Dict[str, int] = {}
    for i, ch in enumerate(pattern):
        last[ch] = i
    i = m - 1  # індекс у тексті
    j = m - 1  # індекс у патерні
    while i < n:
        if text[i] == pattern[j]:
            if j == 0:
                return i
            i -= 1
            j -= 1
        else:
            lo = last.get(text[i], -1)
            i = i + m - min(j, lo + 1)
            j = m - 1
    return -1

def kmp_search(text: str, pattern: str) -> int:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    # префікс-функція (LPS)
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    # пошук
    i = j = 0
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                return i - j
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return -1

def rabin_karp(text: str, pattern: str, base: int = 256, mod: int = 1_000_000_007) -> int:
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
    if m > n:
        return -1
    h = pow(base, m - 1, mod)
    th = 0
    ph = 0
    for i in range(m):
        th = (th * base + ord(text[i])) % mod
        ph = (ph * base + ord(pattern[i])) % mod
    for s in range(n - m + 1):
        if th == ph:
            if text[s:s + m] == pattern:
                return s
        if s < n - m:
            th = ((th - ord(text[s]) * h) * base + ord(text[s + m])) % mod
            if th < 0:
                th += mod
    return -1

ALGORITHMS = {
    "Boyer-Moore (bad char)": boyer_moore_bad_character,
    "KMP": kmp_search,
    "Rabin-Karp": rabin_karp,
}
