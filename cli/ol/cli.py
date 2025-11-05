#!/usr/bin/env python3
import argparse
def main():
    p = argparse.ArgumentParser(prog="ol", description="OpenLambda helper CLI")
    s = p.add_subparsers(dest="cmd", required=True)
    iv = s.add_parser("invoke", help="Invoke a function")
    iv.add_argument("func")
    a = p.parse_args()
    if a.cmd == "invoke":
        print(f"[ok] would invoke function: {a.func}")
if __name__ == "__main__":
    main()
