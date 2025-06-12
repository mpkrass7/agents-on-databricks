import os

import dotenv
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.apps import App, AppResource, AppResourceSecret, AppResourceSecretSecretPermission
from databricks.sdk.errors.platform import AlreadyExists
from rich import console


c = console.Console()

dotenv.load_dotenv()

APP_NAME = os.getenv("APP_NAME")
SCOPE = os.getenv("SCOPE_NAME")

client = WorkspaceClient()

def put_secret(scope: str) -> None:
    """
    Make a scope if it doesn't exist and put the token in it.
    """
    try:
        client.secrets.create_scope(scope)
    except Exception:
        pass
    client.secrets.put_secret(scope=scope, key='token', string_value=client.tokens.create().token_value)


if __name__ == "__main__":
    put_secret(SCOPE)

    app = App(
        name=APP_NAME,
        resources=[
            AppResource(
                name="DATABRICKS_TOKEN",
                description="Databricks PAT",
                secret=AppResourceSecret(
                    scope=SCOPE,
                    key="token",
                    permission=AppResourceSecretSecretPermission.READ
                ),
                
            )
        ],

    )
    try:
        with c.status("[bold yellow]Creating App...[/bold yellow") as status:
            c.print("Creating App... Please wait..")

            app = client.apps.create_and_wait(
                app=app
            )
        c.print("[bold green]App created successfully![/bold green]")
    except AlreadyExists:
        c.print("[bold yellow]App already exists. Fetching existing app...[/bold yellow]")
        app = client.apps.get(APP_NAME)
    c.print(f"[bold blue]App Details:[/bold blue]")
    c.print(app, highlight=True)