import click


@click.command()
@click.help_option("--help", "-h")
def main():
    """Archive Panopto sessions from a folder."""
    print("Hello from panochive!")


if __name__ == "__main__":
    main()
