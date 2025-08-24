# kinda/cli.py

import argparse
import sys
from pathlib import Path


def show_examples():
    """Show example kinda programs with attitude"""
    print("🎲 Here are some kinda programs to get you started:")
    print()
    
    examples = [
        ("Hello World", "examples/hello.py.knda", "The classic, but fuzzy"),
        ("Chaos Greeter", "examples/unified_syntax.py.knda", "Variables that kinda work"),
        ("Maybe Math", None, "~kinda int x = 5\n~kinda int y ~= 10\n~sometimes (x < y) {\n    ~sorta print(\"Math happened!\")\n}"),
    ]
    
    for title, filename, description in examples:
        print(f"📝 {title}")
        if filename and Path(filename).exists():
            print(f"   Try: kinda run {filename}")
            print(f"   Or:  kinda interpret {filename}")
        elif description:
            print("   Example code:")
            for line in description.split('\n'):
                print(f"   {line}")
        print(f"   {description}")
        print()
    
    print("🤷 Pro tip: Run any example with 'interpret' for maximum chaos")


def show_syntax_reference():
    """Show syntax reference with snark"""
    print("📚 Kinda Syntax Reference (your cheat sheet)")
    print()
    
    constructs = [
        ("~kinda int x = 42", "Fuzzy integer (adds ±1 noise)"),
        ("~kinda int y ~= 10", "Extra fuzzy assignment"),
        ("~sorta print(x)", "Maybe prints (80% chance)"),
        ("~sometimes (x > 0) { }", "Random conditional (50% chance)"),
        ("x ~= x + 1", "Fuzzy reassignment"),
    ]
    
    print("✨ Basic Constructs:")
    for syntax, description in constructs:
        print(f"   {syntax:<25} # {description}")
    
    print()
    print("🎯 Pro Tips:")
    print("   • Everything fuzzy starts with ~")
    print("   • Your code will behave... differently each time")
    print("   • That's the point. Embrace the chaos.")
    print("   • Use 'kinda examples' to see it in action")


def get_transformer(lang: str):
    if lang == "python":
        from kinda.langs.python import transformer
        return transformer
    elif lang == "c":
        # C path not ready yet
        return None
    else:
        raise ValueError(f"Unsupported language: {lang}")


def detect_language(path: Path, forced: str | None) -> str:
    """Tiny heuristic; lets --lang override."""
    if forced:
        return forced
    name = str(path)
    if name.endswith(".py.knda") or name.endswith(".py"):
        return "python"
    # Default to python for now
    return "python"


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="kinda", 
        description="🤷 A programming language for people who aren't totally sure"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_transform = sub.add_parser(
        "transform", help="Turn your kinda code into actual code (how responsible of you)"
    )
    p_transform.add_argument("input", help="Your .knda file (yes, it needs the extension)")
    p_transform.add_argument(
        "--out", default="build", help="Where to dump the results (default: build)"
    )
    p_transform.add_argument("--lang", default=None, help="Force a language if you're feeling decisive")

    p_run = sub.add_parser("run", help="Transform then execute (living dangerously, I see)")
    p_run.add_argument("input", help="The .knda file you want to run")
    p_run.add_argument("--lang", default=None, help="Override language detection (sure, why not)")

    p_interpret = sub.add_parser("interpret", help="Run directly in fuzzy runtime (maximum chaos mode)")
    p_interpret.add_argument("input", help="Your questionable life choices in .knda form")
    p_interpret.add_argument("--lang", default=None, help="Force language (you know what you did)")

    p_examples = sub.add_parser("examples", help="Show example kinda programs (for inspiration)")
    
    p_syntax = sub.add_parser("syntax", help="Quick syntax reference (because you'll forget)")

    args = parser.parse_args(argv)

    if args.command == "transform":
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"🤔 '{args.input}' doesn't exist. Are you sure you typed that right?")
            return 1
        out_dir = Path(args.out)
        lang = detect_language(input_path, args.lang)
        transformer = get_transformer(lang)
        if transformer is None:
            print(f"🤷 Sorry, I don't speak {lang} yet. Try Python maybe?")
            return 0
        output_paths = transformer.transform(input_path, out_dir=out_dir)
        for path in output_paths:
            print(f"✨ Transformed your chaos into: {path}")
        print(f"🎲 Generated {len(output_paths)} file(s). Hope they work!")
        return 0

    if args.command == "run":
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"🤷‍♂️ Can't find '{args.input}'. Did you make that up?")
            return 1
        lang = detect_language(input_path, args.lang)
        transformer = get_transformer(lang)
        if transformer is None:
            print(f"🙄 Can't run {lang} files yet. Python works though.")
            return 1
        out_dir = Path(".kinda-build")
        out_paths = transformer.transform(input_path, out_dir=out_dir)
        if lang == "python":
            import runpy
            print("🎮 Running your questionable code...")
            # Execute the transformed file
            runpy.run_path(str(out_paths[0]), run_name="__main__")
            print("🎉 Well, that didn't crash. Success?")
            return 0
        print(f"😅 I can transform {lang} but can't run it. Try 'transform' instead?")
        return 1

    if args.command == "interpret":
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"🙃 '{args.input}' is nowhere to be found. Try again?")
            return 1
        lang = detect_language(input_path, args.lang)
        if lang == "python":
            from kinda.interpreter.repl import run_interpreter
            print("🔮 Entering the chaos dimension...")
            run_interpreter(str(input_path), lang)
            print("🌪️ Chaos complete. Reality may have shifted slightly.")
            return 0
        print(f"🤨 Interpret mode only works with Python. What are you even trying to do?")
        return 1

    if args.command == "examples":
        show_examples()
        return 0
        
    if args.command == "syntax":
        show_syntax_reference()
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())