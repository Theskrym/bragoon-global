#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

try:
    import scrapper_optimized
    print("✓ Sintaxe OK - arquivo importado com sucesso")
except SyntaxError as e:
    print(f"✗ Erro de sintaxe: {e}")
    sys.exit(1)
except Exception as e:
    print(f"! Outro erro ao importar: {type(e).__name__}: {e}")
