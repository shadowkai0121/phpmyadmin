#!/usr/bin/env python3
import os
import sys
import subprocess
import click

ENV_FILE = ".env"
VENV_DIR = ".venv"
REQUIREMENTS = "requirements.txt"


VENV_DIR = ".venv"
ENV_FILE = ".env"
REQUIREMENTS = "requirements.txt"


@click.group()
def cli():
    pass


@cli.command()
@click.option('--auth', default='cookie', type=click.Choice(['cookie', 'config']), help="Global AUTH_TYPE")
def init(auth):
    if os.path.exists(ENV_FILE):
        click.confirm(".env 已存在，是否覆蓋？", abort=False)
    env = {
        'AUTH_TYPE': auth
    }
    save_env(env)
    click.echo(f"✅ .env initialized with AUTH_TYPE={auth}")


def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env[k] = v
    return env


def save_env(env):
    with open(ENV_FILE, 'w') as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")


def next_index(env):
    nums = [int(k.split('_')[-1]) for k in env if k.startswith('PMA_HOST_')]
    return max(nums, default=0)+1


@cli.command()
@click.option('--host', prompt=True)
@click.option('--user', prompt=True)
@click.option('--password', prompt=True, default=None)
@click.option('--label', prompt=True)
@click.option('--port', default=3306)
@click.option('--ssl/--no-ssl', default=False)
@click.option('--ssl-ca', default="")
@click.option('--ssl-verify/--no-verify', default=True)
def add(host, user, password, label, port, ssl, ssl_ca, ssl_verify):
    env = load_env()
    n = next_index(env)
    env.update({
        f"PMA_HOST_{n}": host,
        f"PMA_USER_{n}": user,
        f'PMA_PASS_{n}': password,
        f"PMA_LABEL_{n}": label,
        f"PMA_PORT_{n}": str(port),
        f"PMA_SSL_{n}": str(ssl).lower(),
        f"PMA_SSL_CA_{n}": ssl_ca,
        f"PMA_SSL_VERIFY_{n}": str(ssl_verify).lower(),
    })
    save_env(env)
    click.echo(f"✅ Added server #{n} – {host}")


@cli.command(name="list")
def _list():
    env = load_env()
    click.echo("🌐 Current PMA servers:")
    for k, v in sorted(env.items()):
        if k.startswith("PMA_HOST_"):
            n = k.split('_')[-1]
            click.echo(f"• [{n}] {v}")


@cli.command()
@click.argument('n', type=int)
def remove(n):
    env = load_env()
    for prefix in ["PMA_HOST", "PMA_USER", "PMA_PASS",  "PMA_LABEL", "PMA_PORT", "PMA_SSL", "PMA_SSL_CA", "PMA_SSL_VERIFY"]:
        env.pop(f"{prefix}_{n}", None)
    save_env(env)
    click.echo(f"🗑 Removed server #{n}")


if __name__ == "__main__":
    cli()
