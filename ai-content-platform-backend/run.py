# run.py
from app import create_app

app = create_app()


if __name__ == "__main__":
    print("\n🔗 目前已註冊的路由 (Routes):")
    for rule in app.url_map.iter_rules():
        print(f" - {rule} ({','.join(rule.methods)})")
    print("-" * 30 + "\n")
    
    app.run(debug=True, port=5000)
