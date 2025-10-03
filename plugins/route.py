from aiohttp import web
import markdown
import os

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if not os.path.exists(readme_path):
        return web.Response(text="README.md not found", status=404)

    with open(readme_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    html = markdown.markdown(md_text, extensions=["fenced_code", "codehilite", "tables"])

    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Yugen FileStore - README</title>
        <style>
            body {{
                font-family: sans-serif;
                max-width: 900px;
                margin: auto;
                padding: 2rem;
                background: #f9f9f9;
                color: #333;
            }}
            pre {{
                background: #282c34;
                color: #f8f8f2;
                padding: 1em;
                overflow-x: auto;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.5;
                white-space: pre; /* Important: prevents weird wrapping */
            }}
            code {{
                font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 0.5rem;
                text-align: left;
            }}
            h1, h2, h3 {{
                border-bottom: 1px solid #ddd;
                padding-bottom: 0.3em;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    return web.Response(text=html_page, content_type="text/html")


app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=8080)
