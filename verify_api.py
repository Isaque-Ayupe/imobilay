from fastapi import FastAPI, HTTPException, Header
import importlib.util
import sys

# just verify syntax
import py_compile
py_compile.compile("api.py")
print("Syntax OK")
