import sys
sys.path.append('E:\\Projects\\url-shortener\\URL-Shortener')
import typer

from commands.auth_commands import auth_app
from commands.admin_commands import admin_app
from commands.user_commands import user_app
from commands.url_commands import url_app


app = typer.Typer()

app.add_typer(auth_app, name='auth')
app.add_typer(user_app, name='user')
app.add_typer(admin_app, name='admin')
app.add_typer(url_app, name="url")

if __name__ == "__main__":
    app()